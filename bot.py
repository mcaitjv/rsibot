from datetime import time
import config
from binance.client import Client
import pandas as pd
import sqlalchemy
import datetime
from time import time, sleep
import re,requests


client = Client(config.API_KEY, config.API_SECRET)
engine = sqlalchemy.create_engine('sqlite:///tether_usdtry.db')

while True:
    closes = []
    sleep(60 - time() % 60)
    usdttry_price = client.get_symbol_ticker(symbol="USDTTRY")
    now = datetime.datetime.now().strftime("%H:%M")
    response = requests.get('https://kurlar.altin.in/guncel.asp')
    r = response.content.decode("utf-8")
    kur = re.findall(r"dolar_guncelle\('(.*?)',",r)[0]
    closes.append([now,float(usdttry_price['price']),float(kur)])
    closes = pd.DataFrame(closes,columns=['Time','Tether','Kur'])
    closes.to_sql('USDTTRY', engine, if_exists = 'append', index = False)
