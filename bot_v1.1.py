
import warnings

warnings.filterwarnings("ignore")
from datetime import time
from binance.client import Client
import pandas as pd
import sqlalchemy
import datetime
from time import time, sleep
import re, requests
import sqlite3
import random
import talib
import numpy as np
import config
from binance.exceptions import BinanceAPIException

FARK_ORANI_AL = 0.7
FARK_ORANI_SAT = 0.1
ORDER_TYPE_MARKET = "MARKET"
SIDE_BUY = "BUY"
TRADE_SYMBOL = "USDTTRY"
TRADE_QUANTITY = 3
EMA_LENGTH = 20
RAND_TIME1 = 50
RAND_TIME2 = 59
TIMEOUT = 50

#order fonksiyonları
def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(
            symbol=symbol, side=side, type=order_type, quantity=quantity
        )
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

# apiye client
client = Client(config.API_KEY, config.API_SECRET,  {"verify": False, "timeout": TIMEOUT} ,tld="com")

# random time determining for not beeing banned from altin.in
n = random.randint(RAND_TIME1, RAND_TIME2)

# to determine if in position or not
in_position = False

# ema hesaplaması için boş array(array çünkü talip paketi array istiyor)
ema_array = np.array([])
#as
while True:
    now = datetime.datetime.now().strftime("%H:%M")
    closes = []
    fark = []
    sleep(n - time() % n)
    #hataları yakalamak için binanceden veri çekilen kısmı trycatche koydum
    while True:
        try:
            # binanceden tether fiyatı çekiyor
            usdttry_price = client.get_symbol_ticker(symbol="USDTTRY")
        except Exception as e:
            #hata oluştuğunda loop içinde sürekli deneyip takılmasın diye sleep koydum
            time.sleep(1)
            print("an error happened !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(e)
            #hata oluştuktan sonra clienti tekrar sıfırdan oluşturuyor
            client = Client(config.API_KEY, config.API_SECRET,  {"verify": False, "timeout": TIMEOUT} ,tld="com")
            #hata varsa denemeye devam ediyor veriyi alana kadar
            continue
        #veriyi alırsa looptan cıkıyor
        break

    # tam anlamadım ama bu headerları koymazsan, veri çekilen yerde pythondan request atıldığı belli oluyormuş, bu headerlar sayesinde
    # talep sanki bir web browserdan gelmiş gibi görünüyor. Kesin bilgi değil.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }

    # anlık dolar kuru çekimi ve format düzenlemesi
    response = requests.get("https://kurlar.altin.in/guncel.asp", headers=headers)
    r = response.content.decode("utf-8")
    kur = re.findall(r"dolar_guncelle\('(.*?)',", r)[0]

    #ema hesaplaması için arraya tether fiyatı append etme
    ema_array = np.append(ema_array, float(usdttry_price["price"]))

    # arrayin fazla büyümemesi için belli bir lengthden sonra ilk değeri siliyor
    if len(ema_array) > 25:
        ema_array = np.delete(ema_array, 0)

    # ema hesaplaması yapıyor ve arrayden son değeri alıyor
    ema = talib.EMA(ema_array, EMA_LENGTH)[-1]

    # closes listesine time, tether fiyatı, kur ve ema ekleme
    closes.append([now, float(usdttry_price["price"]), float(kur), ema])

    # strateji
    # eğer kur tetherdan büyükse ve aradaki fark yüzdesi FARK_ORANI_AL den büyükse ve tether fiyatı emadan büyükse al, posizyon alındı olsun,
    # daha sonra aradaki fark FARK_ORANI_SAT'in altına düştüğünde ve o anda pozisyonda isek sat, pozisyonu boşalt
    if closes[0][2] < closes[0][1]:
        print("Tether kurdan büyük")
        print(now)
        # eğer kur tetherdan büyükse
    elif closes[0][2] > closes[0][1]:

        # aradaki fark oranı
        fark = (closes[0][2] - closes[0][1]) / closes[0][1] * 100
        print(fark)

        # eğer pozisyonda değilsek bu bloğa bakacak
        if in_position == False:
            # eğer kur ile tether arasındaki fark FARK_ORANI_AL den büyükse
            if fark >= FARK_ORANI_AL:
                # ve tether fiyatı emanin üzerine cıkmışsa
                if closes[0][1] > ema:
                    # buy order
                    print("buy")
                    # pozisyonu doldur
                    in_position = True
                else:
                    print("tether fiyatı daha emayı geçemedi")
            else:
                print(f"fark {FARK_ORANI_AL}'den küçük")
        else:
            print("already in position")

        # eğer pozisyonda isek bu bloğa bakacak
        if in_position == True:
            # eğer fark oranı FARK_ORANI_SAT'den küçükse
            if fark <= FARK_ORANI_SAT:
                # sell order
                print("Sell")
                # pozisyonu boşalt
                in_position = False
            else:
                print("not ready to sell")


        print(closes)
