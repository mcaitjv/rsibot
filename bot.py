from datetime import time
import config
from binance.client import Client
import pandas as pd
import sqlalchemy
import datetime
from time import time, sleep
import re,requests
import sqlite3
import random

ORDER_TYPE_MARKET = 'MARKET'
SIDE_BUY = 'BUY'
TRADE_SYMBOL = 'USDTTRY'
TRADE_QUANTITY = 3


def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

client = Client(config.API_KEY, config.API_SECRET, tld = "com")
engine = sqlalchemy.create_engine('sqlite:///tether_usdtry.db')

conn = sqlite3.connect("tether_usdtry.db")

n = random. randint(0,22)

while True:
    n = random. randint(45,59)
    closes = []
    sleep(n - time() % n)
    usdttry_price = client.get_symbol_ticker(symbol="USDTTRY")
    now = datetime.datetime.now().strftime("%H:%M")
    response = requests.get('https://kurlar.altin.in/guncel.asp')
    r = response.content.decode("utf-8")
    kur = re.findall(r"dolar_guncelle\('(.*?)',",r)[0]
    closes.append([now,float(usdttry_price['price']),float(kur)])
    closes = pd.DataFrame(closes,columns=['Time','Tether','Kur'])
    closes.to_sql('USDTTRY', engine, if_exists = 'append', index = False)
    df = pd.read_sql("select * from USDTTRY", con=conn)
    try:
        if df.Tether.iloc[-1] < df.Kur.iloc[-1]:
            if abs(df.Tether.iloc[-1] - df.Kur.iloc[-1]) / df.Tether.iloc[-1]>0.000006:
                order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
            else:
                print("sell")
    except:
        print("error")


