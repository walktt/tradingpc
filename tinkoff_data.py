import tinkoff.invest as ti
import pandas as pd
from configparser import ConfigParser
import datetime
import functions
import sys

pd.set_option('display.max_columns', None)

def _get_api_params_from_config() -> dict:
    config_parser = ConfigParser()
    config_parser.read('config.cfg')

    return {'token': config_parser.get('core', 'TOKEN_TINKOFF')}

def get_figi_from_ticker(name, client):
    instruments = client.instruments.futures()
    for instrument in instruments.instruments:
        if instrument.ticker == name:
            break
    return instrument.figi

def create_df_from_ti(candles: [ti.HistoricCandle], token):
    df = pd.DataFrame([{
        'time': c.time + datetime.timedelta(hours=3),
        'open': c.open.units + c.open.nano / 1000000000,
        'close': c.close.units + c.close.nano / 1000000000,
        'low': c.low.units + c.low.nano / 1000000000,
        'high': c.high.units + c.high.nano / 1000000000,
        'dif': abs(c.close.units - c.open.units),
        'dir': functions.calcDirection(c.open.units + c.open.nano / 1000000000, c.close.units + c.close.nano / 1000000000),
        'token': token,
        'volume': c.volume
    } for c in candles])
    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['dif'] = pd.to_numeric(df['dif'], errors='coerce').round(2)
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    return df


def run_tinkoff_check(ticker: str, freq=ti.CandleInterval.CANDLE_INTERVAL_DAY, period_in_minutes: int = 0, period_in_hours: int = 0,
                      period_in_days: int = 0, perc=6):
    today_date = datetime.date.today()
    today_date_start = datetime.datetime(today_date.year, today_date.month, today_date.day)
    if (period_in_hours > 0):
        period = datetime.timedelta(hours=period_in_hours)
        interval = period_in_hours
    if (period_in_days > 0):
        period = datetime.timedelta(minutes=period_in_days)
        interval = period_in_days
    if (period_in_minutes > 0):
        period = datetime.timedelta(minutes=period_in_minutes)
        interval = period_in_minutes
    try:
        with ti.Client(**_get_api_params_from_config()) as client:
            figi = get_figi_from_ticker(ticker, client)
            raw_data = client.market_data.get_candles(
                figi=figi,
                from_=datetime.datetime.now() - period,
                to=datetime.datetime.now(),
                interval=freq
            )
        data = create_df_from_ti(raw_data.candles, ticker)
        data = functions.add_columns_for_df(data)
        print(str(datetime.datetime.now()) + ' ' + ticker)
        print(data)
        functions.pattern_check_pinbar(data, perc=perc, timeframe=interval)
        functions.pattern_check_ski(data)
    except Exception as e:
        print("Oops!", sys.exc_info()[0], "occurred.")
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)

# run_tinkoff_check(ticker='RIU2', freq=ti.CandleInterval.CANDLE_INTERVAL_15_MIN, period_in_minutes=45)

