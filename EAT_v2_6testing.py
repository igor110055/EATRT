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

apiKey = 'Y3dcAaJ0BtLZdQpk9YTryEaft7wQQNMPZc7UJcZAGLKRbDFbtvw2GkRGVeadkvsL'
secKey = 'DA9aVE2d9fs7QWL6YfDs7Q3mJYHblnhJoPdO4tWjbDw4kGJCXviTSlZNroF99Dk9'


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
        since=None,#int(datetime(2022, 5, 11, 10, 20).timestamp() * 1000),
        limit= int(24*4*3*day+26))

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


# 시가 - 종가 리스트

def mail(text,PN):
    now = datetime.now()
    
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('pedrojang777@gmail.com','mpgzxiggfdjbarqz')

    msg =  MIMEText(text)
    msg['Subject'] = PN + str(now)

    s.sendmail('pedrojang777@gmail.com','peter000520@naver.com',msg.as_string())

    s.quit()

def nownow():
    now = datetime.now().minute

    return now

def nowhour():
    NH = datetime.now().hour

    return NH

# 선물 계좌 구하기 
def BGDF():
    balance = binanceFUTURE.fetch_balance(params={"type": "future"})

    return balance['USDT']['free']
# 현재가 구하기
def getcurrent():
    symbol = "ETH/USDT"
    btc = binanceFR.fetch_ticker(symbol)
    return btc['last']

def amountgetter():
    money = BGDF()
    if BGDF() > 50000:
        money = 50000
    amountget = round(money/getcurrent(),6)*0.985
    return amountget

#롱 - 풀매수 -
def buybit(a):
    order = binanceFR.create_market_buy_order(
    symbol=symbol,
    amount=a*leverage,
)

#숏 - 풀매도 -
def sellbit(a):
    order = binanceFR.create_market_sell_order(
    symbol=symbol,
    amount=a*leverage,
)

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
    # ['entryPrice'] 로 진입가격 알 수 있음 진입한 포지션의 평균가임 () 




def SellMethod(i,n):
    kk = 4
    ST = ls_oclo[i+4]
    Condition1 = ls_high[i+4] > ls_bolhigh3[i+4] # 판포가 bol3 위로 솟았는가 

    while kk > -10:
        if ls_close[i+kk] > ls_opens[i+kk]:
            ST = ls_opens[i+kk]
        else:
            break
        kk = kk - 1
    Condition2 = ls_close[i+4] > ls_opens[i+4] and ls_close[i+5] < ls_opens[i+5] and  SP == False # 판포가 양봉이고 결포가 음봉인가
    Condition3 = ls_ochi[i+4] - (ls_ochi[i+4] - ST)*n > ls_oclo[i+5]  and ST < ls_oclo[i+5] and ls_bolhigh3[i+5] > ls_close[i+5] # 변동성 돌파 전략 사용, 과도한 반대포지션 방지, 결포가 bol3윗봉 아레로 내려왔는가 ls_ochi[i+4] - (ls_ochi[i+4] - ls_oclo[i+4])*n > ls_oclo[i+5]  and ls_oclo[i+4] < ls_oclo[i+5] and ls_bolhigh3[i+5] > ls_close[i+5] # 변동성 돌파 전략 사용, 과도한 반대포지션 방지, 결포가 bol3윗봉 아레로 내려왔는가 
    Condition4 = ls_opens[i+2] < ls_close[i+2] and ls_opens[i+3] < ls_close[i+3] and ls_opens[i+4] < ls_close[i+4] and ls_oclo[i+4] > ls_oclo[i+5] and LP == True
    Final_Condition = Condition1 == True and Condition2 == True and Condition3 == True or (LP == True and ls_bolhigh[i+5] < ls_high[i+5]) #or Condition4
    return Final_Condition

# 일반 숏
def BuyMethod(i,n):
    kk = 4
    ST = ls_ochi[i+4]
    Condition1 = ls_low[i+4] < ls_bollow3[i+4] # 판포가 bol3아래로 내려갔는가
    
    while kk > -10:
        if ls_close[i+kk] < ls_opens[i+kk]:
            ST = ls_opens[i+kk]
        else:
            break
        kk = kk - 1
    Condition2 = ls_close[i+4] < ls_opens[i+4] and ls_close[i+5] > ls_opens[i+5] and LP == False # 판포가 음봉이고 결포가 양봉인가 
    Condition3 = ls_oclo[i+4] + (ST - ls_oclo[i+4])*n < ls_ochi[i+5]  and ST > ls_ochi[i+5] and ls_bollow3[i+5] < ls_close[i+5] # 변동성 돌파 전략 사용, 과도한 반대 봉에서의 반대 포지션 방지, 결포가 bol3 아래봉 위로 올라왔는가 
    Condition4 = ls_opens[i+2] > ls_close[i+2] and ls_opens[i+3] > ls_close[i+3] and ls_opens[i+4] > ls_close[i+4] and ls_ochi[i+4] < ls_ochi[i+5] and SP == True
    Final_Condition = Condition1 == True and Condition2 == True and Condition3 == True or (SP == True and ls_bollow[i+5] > ls_low[i+5]) #or Condition4
    return Final_Condition 

# 일반 롱
def BD_StatusDetector(i):
    Condition1 = (ls_close[i+4] > ls_opens[i+4] and (ls_close[i+4] - ls_opens[i+4])/ls_opens[i+4] > 0.01) or (ls_close[i+4] < ls_opens[i+4] and (ls_opens[i+4] - ls_close[i+4])/ls_opens[i+4] > 0.01) # 전봉이 1% 이상의 변동성을 보일 때 
    Condition2 = (ls_close[i+5] - ls_opens[i+5] > 0 and ls_close[i+4] - ls_opens[i+4] > 0 and ls_oclo[i+4] > ls_ma[i+4]) or (ls_close[i+5] - ls_opens[i+5] < 0 and ls_close[i+4] - ls_opens[i+4] < 0 and ls_ochi[i+4] < ls_ma[i+4] )
    Condition3 = (ls_bolhigh[i+4] - ls_bollow[i+4])/3 < (ls_ochi[i+4] - ls_oclo[i+4])
    Final_Condition = Condition1 and Condition2 and Condition3
    return Final_Condition
# 붓다빔 상황판독기 
def BD_BM(i,StartNumber):
    Condition1 = ls_close[i+4] - ls_opens[i+4] < 0 and ls_close[i+5] - ls_opens[i+5] > 0 and (ls_close[i+5] - ls_opens[i+5])/ls_opens[i+5] > 0.002
    Condition2 = (StartNumber - ls_oclo[i+5])*0.33 + ls_oclo[i+5] > ls_ochi[i+5]
    Final_Condition = Condition1, Condition2
    return Final_Condition
# 붓다빔 반동시 롱 
def BD_SM(i,StartNumber):
    Condition1 = ls_close[i+4] - ls_opens[i+4] > 0 and ls_close[i+5] - ls_opens[i+5] < 0 and (ls_close[i+5] - ls_opens[i+5])/ls_opens[i+5] + 1< 0.998
    Condition2 = ls_ochi[i+5] - (ls_ochi[i+5] - StartNumber)*0.33 < ls_oclo[i+5]
    Final_Condition = Condition1, Condition2
    return Final_Condition
# 붓다빔 반동시 숏
def BD_BM_END(i,TargetNumber):
    Condition1 = ls_high[i+5] > TargetNumber
    #Condition2 = 
    Final_Condition = Condition1
    return Final_Condition
# 붓다빔 반동 롱포지션 정리 
def BD_SM_END(i,TargetNumber):
    Condition1 = ls_low[i+5] < TargetNumber
    Final_Condition = Condition1
    return Final_Condition
# 붓다빔 반동 숏포지션 정리 ---- 시간적 조건 추가 (밑에 반복문에 추가할것 ) 반동 처리시조건 도달 못했을 때 처리하는 방법 고민해 보기 (반대봉이 조건을 도달하지 못한 상태일 때 일정 부분 이상으로 넘어가면 (예를 들어 close가 10%이상 손실을 볼것 같을 때 정리하거나 하는 방법으로 시도해보기 ))

dd = 0.02
ddd = 0.01
ddddd = 0.28
nforBDS = 0.3
# GetPD().to_excel("Aloha09-08.xlsx")
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

i = 0
PET = 0
BDT = 0
BDET = 0
proF = 1
proFP = 1
MLT = -3
SP = False
LP = False
leverF = 25
MTG = False
MTGS = False
MTGG = False
BD = False
print('start')
while i < len(ls_close)-5:
    answer = 'NaN '

    if BD == True:
        if LP == True or SP == True:
            if (BD_BM_END(i,TargetNumber) == True or (i > BDCT*3 + BDT )) and LP == True:
                answer = 'BDLP-E'
                sellnum = ls_close[i+5]
                LP = False
                BD = False
                proF = proF * ((((sellnum/buynum)-1.0006)*leverF)+1)
                proFP = round(proFP + (((((sellnum/buynum)-1.0006)*leverF)+1)-1),4)
                PET = i
                BDET = i

            if (BD_SM_END(i,TargetNumber) == True or (i > BDCT*3 + BDT)) and SP == True:
                answer = 'BDSP-E'
                buynum = ls_close[i+5]
                SP = False
                BD = False
                proF = proF * ((((sellnum/buynum)-1.0006)*leverF)+1)
                proFP = round(proFP + (((((sellnum/buynum)-1.0006)*leverF)+1)-1),4)
                PET = i
                BDET = i
            if i > 30 + BDT and LP == False and SP == False:
                BD = False
        if BD_BM(i,StartNumber)[0] == True and LP == False and SP == False and BD == True:
            if BD_BM(i,StartNumber)[1] == False:
                BD = False
                PET = i
            else:
                answer = 'BDLP'
                TargetNumber = (StartNumber - ls_oclo[i+4])*0.75 + ls_oclo[i+4]
                buynum = ls_close[i+5] 
                BDCT = i - BDT
                LP = True

        if BD_SM(i,StartNumber)[0] == True and SP == False and LP == False and BD == True:
            if BD_SM(i,StartNumber)[1] == False:
                BD = False
                PET = i
            else:
                answer = 'BDSP'
                TargetNumber = ls_ochi[i+4] - (ls_ochi[i+4] - StartNumber)*0.75
                sellnum = ls_close[i+5] 
                BDCT = i - BDT
                SP = True
    
    if MTG == False and MTGG == False and BD == False:
        if BD_StatusDetector(i) == True: #and LP == False and SP == False:
            answer = 'BDBD'
            BD = True
            StartNumber = ls_opens[i+4] 
            BDT = i
            if LP == True:
                LP = False
                sellnum = ls_close[i+5]
                if buynum*(1+dd) < ls_high[i+5] or ls_high[i+5] > ls_bolhigh[i+5]*(1+ddd):
                    sellnum = buynum*(1+dd)
                    if ls_high[i+5] > ls_bolhigh[i+5]*(1+ddd):
                        sellnum = ls_bolhigh[i+5]*(1+ddd)
                proF = proF * ((((sellnum/buynum)-1.0006)*leverF)+1)
                proFP = round(proFP + (((((sellnum/buynum)-1.0006)*leverF)+1)-1),4)
            if SP == True:
                SP = False
                buynum = ls_close[i+5]
                if sellnum*(1-dd) > ls_low[i+5] or ls_low[i+5] < ls_bollow[i+5]*(1-ddd):
                    buynum = sellnum*(1-dd)
                    if ls_low[i+5] < ls_bollow[i+5]*(1-ddd):
                        buynum = ls_bollow[i+5]*(1-ddd)
                proF = proF * ((((sellnum/buynum)-1.0006)*leverF)+1)
                proFP = round(proFP + (((((sellnum/buynum)-1.0006)*leverF)+1)-1),4)


        if BuyMethod(i,nforBDS) == True and (SP == True or PET + 12 < i) and BD == False and (BDET - BDT)*5 +BDT < i and BD == False and MTG == False or (SP == True and sellnum*0.995 > ls_close[i+5] and i - MLT < 10):
            answer = 'BUY '
            if LP == False and SP == False:
                LP = True
                buynum = ls_close[i+5]
                MLL = ls_oclo[i+4] 
                MLT = i
            if SP == True:
                SP = False
                buynum = ls_close[i+5]
                if sellnum*(1-dd) > ls_low[i+5] or ls_low[i+5] < ls_bollow[i+5]*(1-ddd):
                    buynum = sellnum*(1-dd)
                    if ls_low[i+5] < ls_bollow[i+5]*(1-ddd):
                        buynum = ls_bollow[i+5]*(1-ddd)
                proF = proF * ((((sellnum/buynum)-1.0006)*leverF)+1)
                proFP = round(proFP + (((((sellnum/buynum)-1.0006)*leverF)+1)-1),4)
                PET = i
        if SellMethod(i,nforBDS) == True and (LP == True or PET + 12 < i) and BD == False and (BDET - BDT)*5 +BDT < i and BD == False and MTG == False or (LP == True and buynum*1.005 < ls_close[i+5] and i - MLT < 10):
            answer = 'SELL'
            if LP == False and SP == False :
                SP = True
                sellnum = ls_close[i+5]
                MLS = ls_ochi[i+5]
                MLT = i
            if LP == True:
                LP = False
                sellnum = ls_close[i+5]
                if buynum*(1+dd) < ls_high[i+5] or ls_high[i+5] > ls_bolhigh[i+5]*(1+ddd):
                    sellnum = buynum*(1+dd)
                    if ls_high[i+5] > ls_bolhigh[i+5]*(1+ddd):
                        sellnum = ls_bolhigh[i+5]*(1+ddd)
                proF = proF * ((((sellnum/buynum)-1.0006)*leverF)+1)
                proFP = round(proFP + (((((sellnum/buynum)-1.0006)*leverF)+1)-1),4)
                PET = i
    

    # 구형 MTG 자리 
        
    
    
    if LP == True and buynum*(1-(1/leverF)) > ls_low[i+5]:
        proF = 0
        proFP = 1
        LP = False
        #answer = 'liquidated'
    if SP == True and sellnum*(1+(1/leverF)) < ls_high[i+5]:
        proF = 0
        proFP = 1
        SP = False
        #answer = 'liquidated'
    if not(answer == 'NaN '):
        a = ''
        print(answer,'|',SP,'|',LP,'|',str(proF),'|',ls_DT[i+5]+(datetime(1,1,1,10) - datetime(1,1,1,1)),'|', str(proFP),'||',ls_bollow[i+5],'|',ls_oclo[i+5],'|',ls_bolhigh[i+5],'|',ls_ochi[i+5])#,'|', ls_tend1[i+5] - ls_tend2[i+5], '---',ls_ma[i+5]-ls_ma2[i+5],'---',ls_close[i+5])
        #print(answer,'|',SP,'|',LP,'|',str(proF),'|',timefinder_5min(timechecker_5min()-(len(ls_close)-(i+6))),'|', str(proFP),'||',ls_bollow[i+5],'|',ls_bollow[i+5],'|',ls_bollow4[i+5],'|',ls_oclo[i+5],'|',ls_bolhigh[i+5],'|',ls_bolhigh[i+5],'|',ls_bolhigh4[i+5],'|',ls_ochi[i+5])#,'|', ls_tend1[i+5] - ls_tend2[i+5], '---',ls_ma[i+5]-ls_ma2[i+5],'---',ls_close[i+5])
    i = i + 1
    