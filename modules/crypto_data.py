# pip install -U pycoingecko
from datetime import datetime, timedelta
from pycoingecko import CoinGeckoAPI

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
cg = CoinGeckoAPI()

def get_info(full_crypto_name):
    try:
        coin = cg.get_coin_by_id(id=full_crypto_name)
        data = {'name': coin['name'], 'current_price (usd)': coin['market_data']['current_price']['usd'], 'market cap (usd)': coin['market_data']['market_cap']['usd'], 'total volume (usd)': coin['market_data']['total_volume']['usd'], '24h change %': coin['market_data']['price_change_percentage_24h']}
        return data
    except Exception as e:
        return e
