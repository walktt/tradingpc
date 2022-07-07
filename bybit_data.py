from pybit import inverse_perpetual
import time
import pandas as pd
import datetime
import functions
from configparser import ConfigParser
import sys

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

def sess_bybit():
    config_parser = ConfigParser()
    config_parser.read('config.cfg')
    session = inverse_perpetual.HTTP(
        endpoint='https://api.bybit.com',
        api_key=config_parser.get('core', 'BYBIT_KEY'),
        api_secret=config_parser.get('core', 'BYBIT_SECRET')
    )
    return session
# ws = inverse_perpetual.WebSocket(
#     test=False,
#     api_key="",
#     api_secret=""
# )

def create_df_from_bybit (candles: dict):
    df = pd.DataFrame([{
        'time': datetime.datetime.fromtimestamp(c['open_time']),
        'open': c['open'],
        'close': c['close'],
        'low': c['low'],
        'high': c['high'],
        'dif': abs(float(c['close']) - float(c['open'])),
        'dir': functions.calcDirection(c['open'], c['close']),
        'token': c['symbol'],
        'volume': c['volume']
    } for c in candles['result']])
    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['dif'] = pd.to_numeric(df['dif'], errors='coerce').round(2)
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    return df

def minutes_tf(min):
    timehourago = int(time.time()) - 60 * min
    return timehourago

def run_bybit_check(symbol="ETHUSD", interval="15", from_time=60, perc=6):
    #perc = 1 = 0.1 %
    try:
        session = sess_bybit()
        candles = session.query_kline(symbol=symbol, interval=interval, from_time=minutes_tf(from_time))
        data = create_df_from_bybit(candles)
        data = functions.add_columns_for_df(data)
        functions.pattern_check_pinbar(data, perc=perc, timeframe=interval)
        functions.pattern_check_ski(data, perc=perc, timeframe=interval)
    except Exception as e:
        # print("Oops!", sys.exc_info()[0], "occurred.")
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)

# run_bybit_check( 'ETHUSD', 15, 60, 6)