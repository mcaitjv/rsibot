from datetime import time
import config
from binance.client import Client
import websocket,json,pprint
import pandas as pd
import sqlalchemy
import datetime

client = Client(config.API_KEY, config.API_SECRET)


SOCKET = 'wss://stream.binance.com:9443/ws/usdttry@kline_1m'
closes = []
engine = sqlalchemy.create_engine('sqlite:///USDTTRYstream.db')


def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes
    #print('received message')
    json_message = json.loads(message)
    #pprint.pprint(json_message)


    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']
    time_c = candle['T']
    #time_c = time.ctime(time_c)

    if is_candle_closed:
        closes = []
        print("candle closed at {} in {}".format(close,time_c))
        closes.append([float(close),time_c])
        print(closes)
        closes = pd.DataFrame(closes,columns=['Price','Time'])
        closes.to_sql('USDTTRY', engine, if_exists = 'append', index = False)

ws = websocket.WebSocketApp(SOCKET, on_open = on_open, on_close= on_close, on_message = on_message)
ws.run_forever()
