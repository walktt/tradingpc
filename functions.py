from configparser import ConfigParser
import telebot
import pandas as pd
import datetime

history={}
config_parser = ConfigParser()
config_parser.read('config.cfg')
bot = telebot.TeleBot(config_parser.get('tg', 'TOKEN_TG'))
chatid = config_parser.get('tg', 'CHAT_ID')

def calcDirection(open, close):
    if open == close:
        return '='
    if float(close) - float(open) > 0:
        return '+'
    if float(close) - float(open) < 0:
        return '-'
    else:
        return 'err'

def add_columns_for_df (df: pd.DataFrame):
    df.loc[df['dir'] == '+', 'shadow_down'] = df['open'] - df['low']
    df.loc[df['dir'] == '+', 'shadow_up'] = df['high'] - df['close']
    df.loc[df['dir'] == '-', 'shadow_down'] = df['close'] - df['low']
    df.loc[df['dir'] == '-', 'shadow_up'] = df['high'] - df['open']
    print(str(datetime.datetime.now()) + ' ' + df.iloc[0].token)
    print(df)
    return df

def notify(name, df: pd.DataFrame, timeframe):
    key = df.iloc[2].token + str(timeframe)
    if (key in history and history[key] != df.iloc[2].open) or key not in history:
        history[key] = df.iloc[2].open
        message = name + ' ' + df.iloc[2].token + ', time: ' + str(df.iloc[2].time) + ', timeframe: ' + str(timeframe)
        bot.send_message(chatid, message)
        # if df.iloc[2].token == 'ETHUSD':
        #     bot.send_message('913603845', message)
        print(message)

def pattern_check_ski(df: pd.DataFrame, perc, timeframe):
    percent1 = df.iloc[0].open / 130
    percent2 = df.iloc[0].open / 1000 * 4
    if (\
            df.iloc[0].dir == df.iloc[1].dir and \
            df.iloc[2].dir == df.iloc[3].dir and \
            df.iloc[1].dir != df.iloc[2].dir and \
            df.iloc[1].dif > percent1 and abs(df.iloc[1].dif - df.iloc[2].dif) < percent2 \
            and df.iloc[1].shadow_up < percent2 and df.iloc[1].shadow_down < percent2 \
            and df.iloc[2].shadow_up < percent2 and df.iloc[2].shadow_down < percent2 \
            ):
        notify('ski', df, timeframe)

def pattern_check_pinbar (df: pd.DataFrame, perc, timeframe):
    if (\
            df.iloc[0].dir == df.iloc[1].dir and \
            (df.iloc[2].shadow_up + df.iloc[2].shadow_down) > df.iloc[2].dif and \
            (df.iloc[2].shadow_up + df.iloc[2].shadow_down) > df.iloc[2].open / 1000 * perc and \
            ((df.iloc[2].shadow_up > df.iloc[2].shadow_down and df.iloc[1].dir == '+') \
            or (df.iloc[2].shadow_up < df.iloc[2].shadow_down and df.iloc[1].dir == '-') \
            # or (df.iloc[2].shadow_up > df.iloc[2].dif and df.iloc[2].shadow_down > df.iloc[2].dif))):
            or (df.iloc[2].shadow_up + df.iloc[2].shadow_down > df.iloc[2].dif*2))):
        notify('pinbar', df, timeframe)
