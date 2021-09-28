import requests
from time import time, sleep
import datetime
import re
import sqlalchemy
import pandas as pd

engine = sqlalchemy.create_engine('sqlite:///USDTRYstream.db')



while True:
    kur = []
    sleep(60 - time() % 60)
    now = datetime.datetime.now().strftime("%H:%M")
    response = requests.get('https://kurlar.altin.in/guncel.asp')
    r = response.content.decode("utf-8")
    print (now+" "+ re.findall(r"dolar_guncelle\('(.*?)',",r)[0])
    kur.append([now,re.findall(r"dolar_guncelle\('(.*?)',",r)[0]])
    kur = pd.DataFrame(kur,columns=['Time','Price'])
    kur.to_sql('USDTRY', engine, if_exists = 'append', index = False)

