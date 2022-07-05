import bybit_data
import tinkoff_data
import schedule
import time
import tinkoff.invest as ti

# run_bybit_check(symbol="ETHUSD", interval="15", from_time=60, perc=6):
schedule.every(3).minutes.do(bybit_data.run_bybit_check, 'ETHUSD', 15, 60, 6)
schedule.every(60).minutes.do(bybit_data.run_bybit_check, 'ETHUSD', 60, 240, 16)
schedule.every(3).minutes.do(tinkoff_data.run_tinkoff_check, ticker='RIU2', freq=ti.CandleInterval.CANDLE_INTERVAL_15_MIN, period_in_minutes=45, perc=6)
schedule.every(3).minutes.do(tinkoff_data.run_tinkoff_check, ticker='SiU2', freq=ti.CandleInterval.CANDLE_INTERVAL_15_MIN, period_in_minutes=45, perc=6)

while True:
    schedule.run_pending()
    time.sleep(10)

