import pandas as pd
import datetime
import os
import requests
from common.constants import BLOCK_CYPHER_URL, CRV_DEPOSITOR_ABI, CRV_DEPOSITOR_CONTRACT_ADDRESS
from web3.auto.infura import w3


def get_locked_crv_and_gas_price():
    block_info_response = requests.get(BLOCK_CYPHER_URL)
    current_block = block_info_response.json()['height']

    crv_depositor_contract_obj = w3.eth.contract(address=CRV_DEPOSITOR_CONTRACT_ADDRESS, abi=CRV_DEPOSITOR_ABI)
    go_back = 100000
    query = f"https://api.etherscan.io/api?module=account&action=txlist&address={CRV_DEPOSITOR_CONTRACT_ADDRESS}&startblock={current_block-go_back}&endblock={current_block}&sort=asc&page=1&offset=10000&apikey={os.environ['ETHERSCAN_TOKEN']}"
    etherscan_api_response = requests.post(query)
    crv_depositor_txes = etherscan_api_response.json()['result']

    crv_lock_txes = {'timestamp': [], 'qt': [], 'gas_price': []}
    for tx in crv_depositor_txes:
        try:
            func, params = crv_depositor_contract_obj.decode_function_input(tx['input'])
            if func.fn_name == 'deposit':
                crv_lock_txes['qt'].append(params['_amount'] * 1e-18)
                crv_lock_txes['gas_price'].append(int(tx['gasPrice']) * 1e-9)
                crv_lock_txes['timestamp'].append(datetime.datetime.fromtimestamp(int(tx['timeStamp'])))
        except Exception as e:
            print(e)
            continue

    df_crv_lock_txes = pd.DataFrame(crv_lock_txes)
    df_crv_lock_txes.set_index('timestamp', inplace=True)

    df_crv_lock_daily = pd.DataFrame()
    df_crv_lock_daily['avg_gas'] = df_crv_lock_txes.groupby(pd.Grouper(freq='1D'))['gas_price'].mean()
    df_crv_lock_daily['total_locked'] = df_crv_lock_txes.groupby(pd.Grouper(freq='1D'))['qt'].sum()

    return df_crv_lock_daily.reset_index().to_json(orient='records', date_format="iso")

