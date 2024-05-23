# pip install -U polygon-api-client
# uses polygon.io to get data
from polygon import RESTClient
from datetime import datetime

# get your api key at https://polygon.io/
polygon_api_key = ''

client = RESTClient(api_key=polygon_api_key)

def get_info(ticker, date):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        info = client.get_daily_open_close_agg(ticker, date)
    except Exception as e:
        return e
    
    return info
