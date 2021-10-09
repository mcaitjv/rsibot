
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

FARK_ORANI_AL = 0.7
FARK_ORANI_SAT = 0.1
ORDER_TYPE_MARKET = "MARKET"
SIDE_BUY = "BUY"
TRADE_SYMBOL = "USDTTRY"
TRADE_QUANTITY = 3
EMA_LENGTH = 8

API_KEY = "ClXIvMPkI1jEXxvJDU4e6HbCTO8yIlJ1Rf7WSNhIIpCR3vM1v8gGPe0BbBXAIijJ"
API_SECRET = "Gk8Z6w6unVHXRpfyov9YcLlGkGR0A3fxQzSHoApzccH7XITB7k1CIO6kSjYFUQfB"

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
client = Client(API_KEY, API_SECRET, tld="com")


# random time determining for not beeing banned from altin.in
n = random.randint(3, 5)


# to determine if in position or not
in_position = False

# ema hesaplaması için boş array(array çünkü talip paketi array istiyor)
ema_array = np.array([])


while True:
    closes = []
    fark = []
    sleep(n - time() % n)
    # binanceden tether fiyatı çekiyor
    usdttry_price = client.get_symbol_ticker(symbol="USDTTRY")
    # time
    now = datetime.datetime.now().strftime("%H:%M")

    # anlık dolar kuru çekimi ve format düzenlemesi
    response = requests.get("https://kurlar.altin.in/guncel.asp")
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

    # eğer kur tetherdan büyükse
    if closes[0][2] > closes[0][1]:

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
