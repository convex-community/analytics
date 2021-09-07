from flask import Flask
import os
from dotenv import load_dotenv
from flask_caching import Cache

load_dotenv()

from modules.gas_price_locked_cvx import get_locked_crv_and_gas_price

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route("/data/gaspricelocked")
@cache.cached(timeout=60*60)
def pricedatadtd():
    return get_locked_crv_and_gas_price()


@app.route('/gaslocked')
def gas_locked():
    return app.send_static_file('gas_price_locked_cvx.html')


@app.route('/')
def home():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)