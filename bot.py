#sqle yazdıktan sonra okuyup analiz etmeyi dene
# ya da dfye append etmeden eklemeyi dene


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
import talib as ta
import numpy as np


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

#apiye client 
client = Client(config.API_KEY, config.API_SECRET, tld = "com")
#sql engine
engine = sqlalchemy.create_engine('sqlite:///tether_usdtry.db')
#sql connection
conn = sqlite3.connect("tether_usdtry.db")

# random time determining for not beeing banned from altin.in
n = random. randint(5,15)

#to determine if in position or not
in_position = False
ema = []

while True:
    closes = []
    fark = []
    sleep(n - time() % n)
    

    usdttry_price = client.get_symbol_ticker(symbol="USDTTRY")
 
    now = datetime.datetime.now().strftime("%H:%M")

    response = requests.get('https://kurlar.altin.in/guncel.asp')
    r = response.content.decode("utf-8")
 
    kur = re.findall(r"dolar_guncelle\('(.*?)',",r)[0]


    closes.append([now,float(usdttry_price['price']),float(kur)])
    closes = pd.DataFrame(closes,columns=['Time','Tether','Kur'])

    ema.append(usdttry_price['price'])


    if closes.Kur.iloc[-1] > closes.Tether.iloc[-1]:
        
        fark = (closes.Kur.iloc[-1]- closes.Tether.iloc[-1]) / closes.Tether.iloc[-1]*100
        print(fark)
        
        if fark >= 0.95:
            if not in_position:
                print("buy")
                in_position = True
            else:
                print("already in position")

        if fark < 0.1:
            if in_position:
                print("Sell")
                in_position = False
        else:
            print("don't do anything")


    closes.to_sql('USDTTRY', engine, if_exists = 'append', index = False)

    print(closes)
    