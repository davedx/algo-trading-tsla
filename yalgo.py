import pandas as pd
import numpy as np
import json
import sys
import requests
import glob, os
import math
from pyti.exponential_moving_average import exponential_moving_average as ema
import talib

rows = 25 #150
pd.set_option("display.max_rows", rows, "display.min_rows", rows)

#pd.options.display.max_rows = 70

print("Loading trading data...")

#os.chdir("/mydir")
df = pd.DataFrame()
for file in glob.glob("TSLA*.pick"):
    tdf = pd.read_pickle(file)
    df = df.combine_first(tdf)

df = df.sort_index()

vix = pd.DataFrame()
for file in glob.glob("%5EVIX*.pick"):
    tdf = pd.read_pickle(file)
    vix = vix.combine_first(tdf)

vix = vix.sort_index()
#print(str(vix['closes'].max()))
#print(str(vix['closes'].min()))
#print(df)
# print(vix.loc[df)
# print(vix['closes'][0])
#print(123)
#sys.exit(1)

# trade when:
# a. EMA's cross
# b. RSI < rsi_max = not overbought
# c. VIX < vix_max

def trade(ema_fast, ema_slow, rsi, rsi_max, roc_min):
    df['ema_fast'] = talib.EMA(df['closes'], timeperiod=ema_fast)
    df['ema_slow'] = talib.EMA(df['closes'], timeperiod=ema_slow)
    #df['roc'] = talib.ROC(df['closes'], timeperiod=4)
    # df['pyti_ema_fast'] = ema(df['closes'], ema_fast)
    # df['pyti_ema_slow'] = ema(df['closes'], ema_slow)
    df['rsi'] = talib.RSI(df['closes'], rsi) # try 2 to 6; 14 is normal
    # print(df)

    df['position'] = np.where(df['ema_fast'] > df['ema_slow'], 1, 0)
    df['signal'] = df['position'].diff()

    returns = 0
    bought_at = 0
    profit = 0
    num_trades = 0
    commission = 0.35
    balance = 50000
    initial_investment = balance
    moves_up = 0
    moves_down = 0
    last_price = df['closes'][0]
    max_shares = math.floor(balance / last_price)

    # int_idx = 0
    for idx, row in df.iterrows():
        price = row['closes']
        if price >= last_price:
            moves_up += price - last_price
        else:
            moves_down += price - last_price
        last_price = price

        if row['signal'] == 1.0 and row['rsi'] < rsi_max: # and row['roc'] > roc_min:
            # if row['signal'] == 1.0 and row['roc'] > roc_min:
            vix_price = 15
            try:
                vix_price = vix.loc[idx]['closes']
            except:
                #print("no entry for "+str(idx))
                vix_price = 15
            vix_confidence = (60 - min(60, vix_price)) / 60 # 0-60/60 = 0-1
            rsi_confidence = (100 - row['rsi']) / 100 # 0-1

            num_shares = math.floor(balance / price) #* vix_confidence #* rsi_confidence # vix_confidence * rsi_confidence
            bought_at = price
            balance -= num_shares * bought_at
            #print(str(idx) + " vix: "+str(vix_price)+" Buy: "+str(num_shares)+" at "+str(bought_at)+" bal: "+str(balance))
        elif row['signal'] == -1.0 and bought_at > 0:
            sold_at = price
            price_diff = num_shares * (sold_at - bought_at)
            num_trades += 1

            balance += num_shares * sold_at
            profit += (price_diff - 2*commission)

            #print(str(idx) + " Sell: "+str(sold_at)+" Diff: "+str(price_diff)+" Bal: "+str(balance))
            bought_at = 0
        #int_idx += 1
    roi = balance/initial_investment
    #print("initial_investment: "+str(initial_investment)+" balance: "+str(balance)+" roi: "+str(roi))
    if profit > 5000:
        print("ema_fast: "+str(ema_fast)+" ema_slow: "+str(ema_slow)+" rsi: "+str(rsi)+" rsi_max: "+str(rsi_max)+" trades: "+str(num_trades)+" profit: "+str(profit)+" roi: "+str(roi))
    return profit
    #print("moves_up: "+str(moves_up * max_shares)+" moves_down: "+str(moves_down * max_shares))

max_profit = 0

# restart at 7/12
def grid_search():
    for ema_f in range(3, 12):
        for ema_s in range(8, 20):
            print("ema f/s: "+str(ema_f)+"/"+str(ema_s))
            for rsi in range(4, 8):
                for rsi_max in range(60, 80):
                    profit = trade(ema_f, ema_s, rsi, rsi_max, 1)
                    if profit > max_profit:
                        max_profit = profit
    print("max profit: "+str(max_profit))

for rsi in range(3, 9):
    for rsi_max in range(65, 95):
        profit = trade(5, 8, rsi, rsi_max, 1)
        if profit > max_profit:
            max_profit = profit
print("max profit: "+str(max_profit))

#trade(5, 12, 6, 74, 0.3)
# trade(5, 12, 6, 74, 0.4)

# Explore higher rsi_max

# 2020-09-22 - 2020-10-29
# ema_fast: 3 ema_slow: 10 rsi: 5 rsi_max: 74 trades: 528 profit: 5950.521826171954 roi: 1.1264024365234375
# ema_fast: 3 ema_slow: 10 rsi: 7 rsi_max: 79 trades: 551 profit: 6669.009869384853 roi: 1.1410941973876954
# ema_fast: 4 ema_slow: 9 rsi: 7 rsi_max: 79 trades: 501 profit: 7705.01838378914 roi: 1.1611143676757814
# ema_fast: 4 ema_slow: 10 rsi: 7 rsi_max: 79 trades: 485 profit: 7716.867782592837 roi: 1.1611273556518555
# ema_fast: 4 ema_slow: 12 rsi: 7 rsi_max: 79 trades: 434 profit: 7572.473223877014 roi: 1.157525464477539
# ema_fast: 5 ema_slow: 8 rsi: 7 rsi_max: 79 trades: 479 profit: 8293.1877929688 roi: 1.172569755859375
# ema_fast: 5 ema_slow: 8 rsi: 7 rsi_max: 85 trades: 481 profit: 9116.030804443286 roi: 1.189054616088867
