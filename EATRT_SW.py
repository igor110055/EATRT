from numpy.core.einsumfunc import _einsum_path_dispatcher
from numpy.core.fromnumeric import trace
import pandas as pd
import ccxt
import numpy as np
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
from pyparsing import conditionAsParseAction

apiKey = 'jq6mhX7fCpNHy1hlOH8dZH1ZAVPfaDnwmIz1cuXUTtASlccBwMIjlSyTj4mkxp0p'
secKey = 'mFzlgrPkYay1LYZK0OdQV3KgwtIC1ghkxZRFGQ9Dek3uAYQCdVpWb9NzGRwTBXZt'


lastBol_low = 0.0
lastBol_high = 0.0
binanceFUTURE = ccxt.binance(config={
    'apiKey': apiKey,
    'secret': secKey,
    'enableRateLimit': True, 
})

binanceFR = ccxt.binance(config={
    'apiKey': apiKey, 
    'secret': secKey,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

markets = binanceFR.load_markets()
symbol = "ETH/USDT"
market = binanceFR.market(symbol)
leverage = 20

resp = binanceFR.fapiPrivate_post_leverage({
    'symbol': market['id'],
    'leverage': leverage
})


balance = binanceFUTURE.fetch_balance(params={"type": "future"})

# 
def btcc(day):
    btc = binanceFR.fetch_ohlcv(
        symbol="ETH/USDT", 
        timeframe='5m', 
        since=None,
        limit= int(24*4*3*day+26))

    return btc

def btcc_1h():
    btc = binanceFR.fetch_ohlcv(
        symbol="ETH/USDT", 
        timeframe='1h', 
        since=None, 
        limit=61)


    return btc

def GetPD(day):
    dff = pd.DataFrame(btcc(day), columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    dff['datetime'] = pd.to_datetime(dff['datetime'], unit='ms')
    dff['datetime1'] = dff['datetime']
    dff['dec'] = dff['high'] - dff['low']
    dff['RD'] = dff['close'] - dff['open']
    dff['GS'] = dff['dec']/dff['volume']
    dff['uptail'] = dff['high'] - ((dff['open'] + dff['close'])/2 + abs(dff['RD'])/2)
    dff['downtail'] = ((dff['open'] + dff['close'])/2 - abs(dff['RD'])/2) - dff['low']
    dff['open1'] = dff['open'].shift(1)
    dff['high1'] = dff['high'].shift(1)
    dff['low1'] = dff['low'].shift(1)
    dff['close1'] = dff['close'].shift(1)
    dff['volume1'] = dff['volume'].shift(1)
    dff['dec1'] = dff['dec'].shift(1)
    dff['RD1'] = dff['RD'].shift(1)
    dff['uptail1'] = dff['uptail'].shift(1)
    dff['downtail1'] = dff['downtail'].shift(1)
    dff['GS1'] = dff['GS'].shift(1)
    dff['chg_vol'] = (dff['close']-dff['open'])/dff['volume']
    dff['chg_vol1'] = dff['chg_vol'].shift(1)
    dff['chg_vol1_0'] = dff['chg_vol'] - dff['chg_vol1']
    dff['chg_vol_MA'] = dff['chg_vol'].rolling(window=20).mean()
    dff.set_index('datetime', inplace=True)
    dff['tMA1'] = dff['close1'].rolling(window=20).mean()
    dff['tMA1'] = dff['tMA1'].round(2)
    dff['std1'] = dff['close1'].rolling(window=20).std()
    dff['tMA2'] = dff['tMA1'].shift(1)
    dff['ttMA1'] = dff['close1'].rolling(window=10).mean()
    dff['ttMA1'] = dff['ttMA1'].round(2)
    dff['ttMA2'] = dff['ttMA1'].shift(1)
    dff['mid'] = dff['open']/2 + dff['close']/2
    dff['mid1'] = dff['mid'].shift(1)
    dff['tend1'] = dff['ttMA1'] - dff['ttMA2']
    dff['tend2'] = dff['tend1'].shift(1)
    dff['mMm'] = dff['mid'] - dff['mid1']
    dff1= dff.dropna()
    dff1['bollow1'] = dff1['tMA1'] - 1.8*dff1['std1']
    dff1['bollow1'] = dff1['bollow1'].round(2)
    dff1['bolhigh1'] = dff1['tMA1'] + 1.8*dff1['std1']
    dff1['bolhigh1'] = dff1['bolhigh1'].round(2)
    dff1['bollow1_3'] = dff1['tMA1'] - 2.7*dff1['std1']
    dff1['bollow1_3'] = dff1['bollow1_3'].round(2)
    dff1['bolhigh1_3'] = dff1['tMA1'] + 2.7*dff1['std1']
    dff1['bolhigh1_3'] = dff1['bolhigh1_3'].round(2)
    dff1['bollow1_4'] = dff1['tMA1'] - 3.6*dff1['std1']
    dff1['bollow1_4'] = dff1['bollow1_4'].round(2)
    dff1['bolhigh1_4'] = dff1['tMA1'] + 3.6*dff1['std1']
    dff1['bolhigh1_4'] = dff1['bolhigh1_4'].round(2)
    dff1.isnull().sum()
    return dff1

def GetPD1h():
    dff = pd.DataFrame(btcc_1h(), columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    dff['datetime'] = pd.to_datetime(dff['datetime'], unit='ms')
    dff['dec'] = dff['high'] - dff['low']
    dff['RD'] = dff['close'] - dff['open']
    dff['GS'] = dff['dec']/dff['volume']
    dff['uptail'] = dff['high'] - ((dff['open'] + dff['close'])/2 + abs(dff['RD'])/2)
    dff['downtail'] = ((dff['open'] + dff['close'])/2 - abs(dff['RD'])/2) - dff['low']
    dff['open1'] = dff['open'].shift(1)
    dff['high1'] = dff['high'].shift(1)
    dff['low1'] = dff['low'].shift(1)
    dff['close1'] = dff['close'].shift(1)
    dff['volume1'] = dff['volume'].shift(1)
    dff['dec1'] = dff['dec'].shift(1)
    dff['RD1'] = dff['RD'].shift(1)
    dff['uptail1'] = dff['uptail'].shift(1)
    dff['downtail1'] = dff['downtail'].shift(1)
    dff['GS1'] = dff['GS'].shift(1)
    dff.set_index('datetime', inplace=True)
    dff['tMA1'] = dff['close1'].rolling(window=20).mean()
    dff['tMA1'] = dff['tMA1'].round(2)
    dff['std1'] = dff['close1'].rolling(window=20).std()
    dff['tMA2'] = dff['tMA1'].shift(1)
    dff['ttMA1'] = dff['close1'].rolling(window=10).mean()
    dff['ttMA1'] = dff['ttMA1'].round(2)
    dff['ttMA2'] = dff['ttMA1'].shift(1)
    dff['mid'] = dff['open']/2 + dff['close']/2
    dff['mid1'] = dff['mid'].shift(1)
    dff['tend1'] = dff['ttMA1'] - dff['ttMA2']
    dff['tend2'] = dff['tend1'].shift(1)
    dff1= dff.dropna()
    dff1['bollow1'] = dff1['tMA1'] - 1.8*dff1['std1']
    dff1['bollow1'] = dff1['bollow1'].round(2)
    dff1['bolhigh1'] = dff1['tMA1'] + 1.8*dff1['std1']
    dff1['bolhigh1'] = dff1['bolhigh1'].round(2)
    dff1['mMm'] = dff1['mid'] - dff1['mid1']
    dff1.isnull().sum()
    return dff1


# ?????? - ?????? ?????????
def getRD():
    lst = GetPD().RD.tolist()
    return lst

def mail(text,PN):
    now = datetime.now()
    
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('pedrojang777@gmail.com','mpgzxiggfdjbarqz')

    msg =  MIMEText(text)
    msg['Subject'] = PN + str(now)

    s.sendmail('pedrojang777@gmail.com','gangkihun@daum.net',msg.as_string())

    s.quit()

def nownow():
    now = datetime.now().minute

    return now

def nowhour():
    NH = datetime.now().hour

    return NH

# ?????? ?????? ????????? 
def BGDF():
    balance = binanceFUTURE.fetch_balance(params={"type": "future"})

    return balance['USDT']['free']
# ????????? ?????????
def getcurrent():
    symbol = "ETH/USDT"
    btc = binanceFR.fetch_ticker(symbol)
    return btc['last']

def amountgetter():
    money = BGDF()
    if BGDF() < 5000:
        money = BGDF()/2
    if BGDF() >= 5000 and BGDF() < 20000:
        money = 5000
    if BGDF() >= 20000 and BGDF() < 40000:
        money = 10000
    if BGDF() >= 40000 and BGDF() < 80000:
        money = 20000
    if BGDF() >= 80000 and BGDF() < 160000:
        money = 40000
    if BGDF() >=160000:
        money = 100000
    amountget = round(money/getcurrent(),6)*0.985
    return amountget

def timechecker_15min():
    now = datetime.now().minute
    hour = datetime.now().hour
    count_15min = now//15 + hour*4
    return count_15min

def timefinder_15min(a):
    day = 0
    if a < 0:
        while a < 0:
            a = a + 96
            day = day - 1
    t = a//4
    tt = a%4
    thattime = str(t)+ ':' + str(tt*15) + '  day from now...' +str(day)
    return thattime

def timechecker_5min():
    now = datetime.now().minute
    hour = datetime.now().hour
    count_15min = now//5 + hour*12
    return count_15min

def timefinder_5min(a):
    day = 0
    if a < 0:
        while a < 0:
            a = a + (96*3)
            day = day - 1
    t = a//12
    tt = a%12
    thattime = str(t)+ ':' + str(tt*5) + '  day from now...' +str(day)
    return thattime

def getpossition():

    balance = binanceFR.fetch_balance()
    positions = balance['info']['positions']

    for position in positions:
        if position['symbol'] == 'ETHUSDT':
            RP = position['entryPrice']
    return RP
    # ['entryPrice'] ??? ???????????? ??? ??? ?????? ????????? ???????????? ???????????? () 



#??? - ????????? -
def buybit(a):
    order = binanceFR.create_market_buy_order(
    symbol=symbol,
    amount=a*leverage,
)

#??? - ????????? -
def sellbit(a):
    order = binanceFR.create_market_sell_order(
    symbol=symbol,
    amount=a*leverage,
)


def SellMethod(i,n):
    kk = 4
    ST = ls_oclo[i+4]
    Condition1 = ls_high[i+4] > ls_bolhigh3[i+4] # ????????? bol3 ?????? ???????????? 
    while kk > -10:
        if ls_close[i+kk] > ls_opens[i+kk]:
            ST = ls_opens[i+kk]
        else:
            break
        kk = kk - 1
    Condition2 = ls_close[i+4] > ls_opens[i+4] and ls_close[i+5] < ls_opens[i+5] and  SP == False # ????????? ???????????? ????????? ????????????
    Condition3 = ls_ochi[i+4] - (ls_ochi[i+4] - ST)*n > ls_oclo[i+5]  and ST < ls_oclo[i+5] and ls_bolhigh3[i+5] > ls_close[i+5] # ????????? ?????? ?????? ??????, ????????? ??????????????? ??????, ????????? bol3?????? ????????? ??????????????? ls_ochi[i+4] - (ls_ochi[i+4] - ls_oclo[i+4])*n > ls_oclo[i+5]  and ls_oclo[i+4] < ls_oclo[i+5] and ls_bolhigh3[i+5] > ls_close[i+5] # ????????? ?????? ?????? ??????, ????????? ??????????????? ??????, ????????? bol3?????? ????????? ??????????????? 
    Condition4 = ls_opens[i+2] < ls_close[i+2] and ls_opens[i+3] < ls_close[i+3] and ls_opens[i+4] < ls_close[i+4] and ls_oclo[i+4] > ls_oclo[i+5] and LP == True
    Final_Condition = Condition1 == True and Condition2 == True and Condition3 == True or (LP == True and ls_bolhigh[i+5] < ls_high[i+5]) #or Condition4
    return Final_Condition

# ?????? ???
def BuyMethod(i,n):
    kk = 4
    ST = ls_ochi[i+4]
    Condition1 = ls_low[i+4] < ls_bollow3[i+4] # ????????? bol3????????? ???????????????
    while kk > -10:
        if ls_close[i+kk] < ls_opens[i+kk]:
            ST = ls_opens[i+kk]
        else:
            break
        kk = kk - 1
    Condition2 = ls_close[i+4] < ls_opens[i+4] and ls_close[i+5] > ls_opens[i+5] and LP == False # ????????? ???????????? ????????? ???????????? 
    Condition3 = ls_oclo[i+4] + (ST - ls_oclo[i+4])*n < ls_ochi[i+5]  and ST > ls_ochi[i+5] and ls_bollow3[i+5] < ls_close[i+5] # ????????? ?????? ?????? ??????, ????????? ?????? ???????????? ?????? ????????? ??????, ????????? bol3 ????????? ?????? ??????????????? 
    Condition4 = ls_opens[i+2] > ls_close[i+2] and ls_opens[i+3] > ls_close[i+3] and ls_opens[i+4] > ls_close[i+4] and ls_ochi[i+4] < ls_ochi[i+5] and SP == True
    Final_Condition = Condition1 == True and Condition2 == True and Condition3 == True or (SP == True and ls_bollow[i+5] > ls_low[i+5]) #or Condition4
    return Final_Condition 

# ?????? ???
def BD_StatusDetector(i):
    Condition1 = (ls_close[i+4] > ls_opens[i+4] and (ls_close[i+4] - ls_opens[i+4])/ls_opens[i+4] > 0.01) or (ls_close[i+4] < ls_opens[i+4] and (ls_opens[i+4] - ls_close[i+4])/ls_opens[i+4] > 0.01) # ????????? 1% ????????? ???????????? ?????? ??? 
    Condition2 = (ls_close[i+5] - ls_opens[i+5] > 0 and ls_close[i+4] - ls_opens[i+4] > 0 and ls_oclo[i+4] > ls_ma[i+4]) or (ls_close[i+5] - ls_opens[i+5] < 0 and ls_close[i+4] - ls_opens[i+4] < 0 and ls_ochi[i+4] < ls_ma[i+4] )
    Condition3 = (ls_bolhigh[i+4] - ls_bollow[i+4])/3 < (ls_ochi[i+4] - ls_oclo[i+4])
    Final_Condition = Condition1 and Condition2 and Condition3
    return Final_Condition
# ????????? ??????????????? 
def BD_BM(i,StartNumber):
    Condition1 = ls_close[i+4] - ls_opens[i+4] < 0 and ls_close[i+5] - ls_opens[i+5] > 0 and (ls_close[i+5] - ls_opens[i+5])/ls_opens[i+5] > 0.002
    Condition2 = (StartNumber - ls_oclo[i+5])*0.33 + ls_oclo[i+5] > ls_ochi[i+5]
    Final_Condition = Condition1, Condition2
    return Final_Condition
# ????????? ????????? ??? 
def BD_SM(i,StartNumber):
    Condition1 = ls_close[i+4] - ls_opens[i+4] > 0 and ls_close[i+5] - ls_opens[i+5] < 0 and (ls_close[i+5] - ls_opens[i+5])/ls_opens[i+5] + 1< 0.998
    Condition2 = ls_ochi[i+5] - (ls_ochi[i+5] - StartNumber)*0.33 < ls_oclo[i+5]
    Final_Condition = Condition1, Condition2
    return Final_Condition
# ????????? ????????? ???
def BD_BM_END(i,TargetNumber):
    Condition1 = ls_high[i+5] > TargetNumber
    #Condition2 = 
    Final_Condition = Condition1
    return Final_Condition
# ????????? ?????? ???????????? ?????? 
def BD_SM_END(i,TargetNumber):
    Condition1 = ls_low[i+5] < TargetNumber
    Final_Condition = Condition1
    return Final_Condition
# ????????? ?????? ???????????? ?????? ---- ????????? ?????? ?????? (?????? ???????????? ???????????? ) ?????? ??????????????? ?????? ????????? ??? ???????????? ?????? ????????? ?????? (???????????? ????????? ???????????? ?????? ????????? ??? ?????? ?????? ???????????? ???????????? (?????? ?????? close??? 10%?????? ????????? ?????? ?????? ??? ??????????????? ?????? ???????????? ??????????????? ))
ENDtime = datetime(1,1,1,9,30)
actiontime = nownow()
etherinfo = GetPD(2)
ls_mids = etherinfo.mid.tolist()
ls_opens = etherinfo.open.tolist()
ls_close = etherinfo.close.tolist()
ls_mMm = etherinfo.mMm.tolist()
ls_bollow = etherinfo.bollow1.tolist()
ls_bolhigh = etherinfo.bolhigh1.tolist()
ls_bollow3 = etherinfo.bollow1_3.tolist()
ls_bolhigh3 = etherinfo.bolhigh1_3.tolist()
ls_bollow4 = etherinfo.bollow1_4.tolist()
ls_bolhigh4 = etherinfo.bolhigh1_4.tolist()
ls_ma = etherinfo.tMA1.tolist()
ls_ma2 = etherinfo.tMA2.tolist()
ls_tend1 = etherinfo.tend1.tolist()
ls_tend2 = etherinfo.tend2.tolist()
ls_high = etherinfo.high.tolist()
ls_low = etherinfo.low.tolist()
ls_vol =etherinfo.volume.tolist()
ls_volchg = etherinfo.chg_vol_MA.tolist()
ls_DT = etherinfo.datetime1.tolist()
CTF = -1
while CTF > -1*len(ls_DT):
    asdf = datetime.now() - ls_DT[CTF] - (datetime(1,1,1,9) - datetime(1,1,1))
    if asdf < (datetime(1,1,1,9,30) - datetime(1,1,1,9)) and asdf >= (datetime(1,1,1,9,5) - datetime(1,1,1,9)):
        CorrectTime = CTF
        break
    else :
        CTF = CTF - 1
ls_ochi = []
ls_oclo = []
ki = 0
while ki < len(ls_opens):
    if ls_opens[ki] <= ls_close[ki]:
        ls_ochi.append(ls_close[ki])
        ls_oclo.append(ls_opens[ki])
    else:
        ls_ochi.append(ls_opens[ki])
        ls_oclo.append(ls_close[ki])
    ki = ki + 1
ENDtime = datetime(1,1,1,9,30) - datetime(1,1,1,9,30)
i = 0
BDT = datetime(1,1,1,9,30) - datetime(1,1,1,9,30)
BDCT = datetime(1,1,1,9,30) - datetime(1,1,1,9,30)
BDET = datetime(1,1,1,9,30) - datetime(1,1,1,9,30) 
proF = 1
proFP = 1
MLT = -3
SP = False
LP = False
BD = False


text = 'Good Luck!!'
title = 'Program started!!'
mail(text,title)
print('Program started!! \n Good Luck!!')
while True:
    try:
        if nownow()%5 == 0 :
            time.sleep(3)  # 15????????? ????????? ???????????? ??? (15????????? ????????? ???????????? ?????? ??? ???????????? ??????)
            if not(actiontime == nownow()):
                actiontime = nownow()
                etherinfo = GetPD(9)
                ls_mids = etherinfo.mid.tolist()
                ls_opens = etherinfo.open.tolist()
                ls_close = etherinfo.close.tolist()
                ls_mMm = etherinfo.mMm.tolist()
                ls_bollow = etherinfo.bollow1.tolist()
                ls_bolhigh = etherinfo.bolhigh1.tolist()
                ls_bollow3 = etherinfo.bollow1_3.tolist()
                ls_bolhigh3 = etherinfo.bolhigh1_3.tolist()
                ls_bollow4 = etherinfo.bollow1_4.tolist()
                ls_bolhigh4 = etherinfo.bolhigh1_4.tolist()
                ls_ma = etherinfo.tMA1.tolist()
                ls_ma2 = etherinfo.tMA2.tolist()
                ls_tend1 = etherinfo.tend1.tolist()
                ls_tend2 = etherinfo.tend2.tolist()
                ls_high = etherinfo.high.tolist()
                ls_low = etherinfo.low.tolist()
                ls_vol =etherinfo.volume.tolist()
                ls_volchg = etherinfo.chg_vol_MA.tolist()
                ls_DT = etherinfo.datetime1.tolist()
                ls_ochi = []
                ls_oclo = []
                ki = 0
                while ki < len(ls_opens):
                    if ls_opens[ki] <= ls_close[ki]:
                        ls_ochi.append(ls_close[ki])
                        ls_oclo.append(ls_opens[ki])
                    else:
                        ls_ochi.append(ls_opens[ki])
                        ls_oclo.append(ls_close[ki])
                    ki = ki + 1

                CTF = -1
                while CTF > -1*len(ls_DT):
                    asdf = datetime.now() - ls_DT[CTF] - (datetime(1,1,1,9) - datetime(1,1,1))
                    if asdf < (datetime(1,1,1,9,10) - datetime(1,1,1,9)) and asdf >= (datetime(1,1,1,9,5) - datetime(1,1,1,9)):
                        CorrectTime = CTF
                        break
                    else :
                        CTF = CTF - 1
                ls_ochi = []
                ls_oclo = []
                ki = 0
                while ki < len(ls_opens):
                    if ls_opens[ki] <= ls_close[ki]:
                        ls_ochi.append(ls_close[ki])
                        ls_oclo.append(ls_opens[ki])
                    else:
                        ls_ochi.append(ls_opens[ki])
                        ls_oclo.append(ls_close[ki])
                    ki = ki + 1
                if BD == True:
                    if LP == True or SP == True:
                        if (BD_BM_END(CorrectTime - 5,TargetNumber) == True or datetime.now() > BDCT*3 + BDT) and LP == True:
                            LP = False 
                            sellbit(PN)
                            sellnum = getcurrent()
                            time.sleep(1)
                            aftertrade = BGDF()
                            text = 'After trade: ' + str(aftertrade) + '\n' + 'sellnum: ' + str(sellnum) + '\n' + 'Profit: ' + str(aftertrade/beforetrade)
                            title = 'BD_Long possition Endded'
                            mail(text,title)
                            BDET = datetime.now()

                        if (BD_SM_END(CorrectTime - 5,TargetNumber) == True or datetime.now() > BDCT*3 + BDT) and SP == True:
                            SP = False
                            buybit(PN)
                            buynum = getcurrent()
                            time.sleep(1)
                            aftertrade = BGDF()
                            text = 'After trade: ' + str(aftertrade) + '\n' + 'buynum: ' + str(buynum) + '\n' + 'Profit: ' + str(aftertrade/beforetrade)
                            title = 'BD_Short possition Endded'
                            mail(text,title)
                            BDET = datetime.now()

                    if BD_BM(CorrectTime - 5,StartNumber)[0] == True and LP == False and BD == True:
                        if BD_BM(CorrectTime - 5,StartNumber)[1] == False:
                            BD = False
                            ENDtime = datetime.now()
                        else:
                            beforetrade = BGDF()
                            TargetNumber = (StartNumber - ls_oclo[CorrectTime-1])*0.75 + ls_oclo[CorrectTime-1]
                            LP = True
                            PN = amountgetter()
                            buybit(PN)
                            time.sleep(2)
                            buynum = getpossition()
                            text = 'Before trade: ' + str(beforetrade) + '\n' + 'buynum: ' + str(buynum)
                            title = 'BD_Long possiton started'
                            mail(text,title)
                            BDCT = datetime.now() - BDT

                    if BD_SM(CorrectTime - 5,StartNumber)[0] == True and SP == False and BD == True:
                        if BD_SM(CorrectTime - 5,StartNumber)[1] == False:
                            BD = False
                            ENDtime = datetime.now()
                        else:
                            beforetrade = BGDF()
                            TargetNumber = ls_ochi[CorrectTime-1] - (ls_ochi[CorrectTime-1] - StartNumber)*0.75
                            SP = True
                            PN = amountgetter()
                            sellbit(PN)
                            time.sleep(2)
                            sellnum = getpossition()
                            text = 'Before trade: ' + str(beforetrade) + '\n' + 'sellnum: ' + str(sellnum)
                            title = 'BD_Short possiton started'
                            BDCT = datetime.now() - BDT
                            mail(text,title)

                if BD == False:
                    if BD_StatusDetector(CorrectTime - 5) == True and LP == False and SP == False:
                        BD = True
                        StartNumber = ls_opens[CorrectTime] 
                        BDT = datetime.now()
                        text = 'BD START'
                        title = 'BD'
                        mail(text,title)
                        if LP == True:
                            LP = False 
                            sellbit(PN)
                            sellnum = getcurrent()
                            time.sleep(1)
                            aftertrade = BGDF()
                            text = 'After trade: ' + str(aftertrade) + '\n' + 'sellnum: ' + str(sellnum) + '\n' + 'Profit: ' + str(aftertrade/beforetrade)
                            title = 'Long possition Endded for BD'
                            mail(text,title)
                        if SP == True:
                            SP = False
                            buybit(PN)
                            buynum = getcurrent()
                            time.sleep(1)
                            aftertrade = BGDF()
                            text = 'After trade: ' + str(aftertrade) + '\n' + 'buynum: ' + str(buynum) + '\n' + 'Profit: ' + str(aftertrade/beforetrade)
                            title = 'Short possition Endded for BD'
                            mail(text,title)
                            ENDtime = datetime.now()
                    if BuyMethod(CorrectTime - 5,0.3) and BD == False and (SP == True or ENDtime + (datetime(1,1,1,10) - datetime(1,1,1,9)) <= datetime.now()) and BD == False and (BDET-BDT)*5+BDT<datetime.now():
                        if LP == False and SP == False:
                            beforetrade = BGDF()
                            LP = True
                            PN = amountgetter()
                            buybit(PN)
                            time.sleep(2)
                            buynum = getpossition()
                            text = 'Before trade: ' + str(beforetrade) + '\n' + 'buynum: ' + str(buynum)
                            title = 'Long possiton started'
                            mail(text,title)
                            STARTtime = datetime.now()
                        if SP == True:
                            SP = False
                            buybit(PN)
                            buynum = getcurrent()
                            time.sleep(1)
                            aftertrade = BGDF()
                            text = 'After trade: ' + str(aftertrade) + '\n' + 'buynum: ' + str(buynum) + '\n' + 'Profit: ' + str(aftertrade/beforetrade)
                            title = 'Short possition Endded'
                            mail(text,title)
                            ENDtime = datetime.now()
                    if SellMethod(CorrectTime - 5,0.3) and BD == False and (LP == True or ENDtime + (datetime(1,1,1,10) - datetime(1,1,1,9)) <= datetime.now()) and BD == False and (BDET-BDT)*5+BDT<datetime.now():
                        if LP == False and SP == False:
                            beforetrade = BGDF()
                            SP = True
                            PN = amountgetter()
                            sellbit(PN)
                            time.sleep(2)
                            sellnum = getpossition()
                            text = 'Before trade: ' + str(beforetrade) + '\n' + 'sellnum: ' + str(sellnum)
                            title = 'Short possiton started'
                            STARTtime = datetime.now()
                            mail(text,title)
                        if LP == True:
                            LP = False 
                            sellbit(PN)
                            sellnum = getcurrent()
                            time.sleep(1)
                            aftertrade = BGDF()
                            text = 'After trade: ' + str(aftertrade) + '\n' + 'sellnum: ' + str(sellnum) + '\n' + 'Profit: ' + str(aftertrade/beforetrade)
                            title = 'Long possition Endded'
                            mail(text,title)
                            ENDtime = datetime.now()
                
        if (LP == True or SP == True) and getpossition() == 0.0:
            LP = False 
            SP = False
            text = 'Your position had been liquidated\n' +'LP:'+str(LP)+'\n'+'SP:'+str(SP)
            title = 'Liquidation Alert'
            mail(text,title)
        time.sleep(0.5)
    except Exception as e:
       print(e)
       time.sleep(1)

       
       
       
