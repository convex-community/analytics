from flask import Flask
import os
import requests_cache
from dotenv import load_dotenv

load_dotenv()

from modules.gas_price_locked_cvx import get_locked_crv_and_gas_price

app = Flask(__name__)


@app.route("/data/gaspricelocked")
def pricedatadtd():
    return get_locked_crv_and_gas_price()


@app.route('/gaslocked')
def gas_locked():
    return app.send_static_file('gas_price_locked_cvx.html')


@app.route('/')
def home():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    requests_cache.install_cache(cache_name='github_cache', backend='sqlite', expire_after=60*60)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)