# pip install -U pycoingecko
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def get_info(full_crypto_name):
    name = full_crypto_name.lower()
    try:
        coin = cg.get_coin_by_id(id=name)
        data = {'name': coin['name'], 'current_price (usd)': coin['market_data']['current_price']['usd'], 'market cap (usd)': coin['market_data']['market_cap']['usd'], 'total volume (usd)': coin['market_data']['total_volume']['usd'], '24h change %': coin['market_data']['price_change_percentage_24h']}
        return data
    except Exception as e:
        return e
