from pytz import timezone
import time
import pyupbit
import datetime
import requests
import schedule

Kval = 0.61
access = ""
secret = ""
CoinN = "SAND"
loFrame = "min240"
myToken = ""
slChannel = "#eehaesand"
 
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(response)
 
 
post_message(myToken,slChannel,"Cry Connected!")

def get_ma15(ticker):
    """15 이동 평균선 조회"""
    df1 = pyupbit.get_ohlcv(ticker, interval="minute240", count=15)
    df = df1.tz_localize(None)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df1 = pyupbit.get_ohlcv(ticker, interval="minute240", count=2)
    df = df1.tz_localize(None)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df1 = pyupbit.get_ohlcv(ticker, interval="minute240", count=1)
    df = df1.tz_localize(None)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


# target_price = get_target_price("KRW-" + CoinN, Kval)*1.0005
# currentP = get_current_price("KRW-" + CoinN)
# ma15 = get_ma15("KRW-" + CoinN)
# start_time = get_start_time("KRW-" + CoinN)
# end_time = start_time + datetime.timedelta(hours=4) - datetime.timedelta(seconds=10)
# print(str(start_time) + " to " + str(end_time))
# print("TP: " + str(target_price) + " MA: " + str(ma15) + " CP: " + str(currentP))


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
post_message(myToken,slChannel, "CryT logged on. Autotrade start")

# 자동매매 시작
while True:
    try:
        now1 = datetime.datetime.now(timezone('Asia/Seoul'))
        now = now1.replace(tzinfo=None)
        start_time = get_start_time("KRW-" + CoinN)
        end_time = start_time + datetime.timedelta(hours=4) - datetime.timedelta(seconds=10)
        schedule.run_pending()
        

        if start_time < now < end_time:
            target_price = get_target_price("KRW-" + CoinN, Kval)*1.0005
            currentP = get_current_price("KRW-" + CoinN)
            ma15 = get_ma15("KRW-" + CoinN)
            print(str(start_time) + " to " + str(end_time) + " Now: " + str(now))
            print("TP: " + str(target_price) + " MA: " + str(ma15) + " CP: " + str(currentP))
            
            if target_price < currentP and ma15 < currentP:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-" + CoinN, krw*0.9995)
                    post_message(myToken,slChannel, CoinN + " buy result: \n" + str(buy_result))
        else:
            crypt = get_balance(CoinN)
            num_coin = 4
            if crypt > num_coin:
                sell_result = upbit.sell_market_order("KRW-" + CoinN, crypt*0.9995)
                post_message(myToken,slChannel, CoinN + " sell result: \n" + str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,slChannel, "Cry: Error!")
        time.sleep(1)