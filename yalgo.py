import pandas as pd
import numpy as np
import json
import sys
import requests
import glob, os
from pyti.exponential_moving_average import exponential_moving_average as ema

import talib

rows = 5 #150
pd.set_option("display.max_rows", rows, "display.min_rows", rows)

#pd.options.display.max_rows = 70

print("Loading last week's trading data (1m period) for TSLA from Yahoo...")


#os.chdir("/mydir")
frames = []
for file in glob.glob("*.pick"):
    df = pd.read_pickle(file)
    frames.append(df)
#    df = df.from_pickle(file)
    #print(df)

df = pd.concat(frames)
df = df.sort_index()
print(df)
sys.exit()

url = 'https://query1.finance.yahoo.com/v8/finance/chart/TSLA?region=US&lang=en-US&includePrePost=false&interval=1m&range=7d&corsDomain=finance.yahoo.com&.tsrc=finance'

response = requests.get(url,
                             headers = {
                                 'User-Agent': 'request',
                                 'Accept': 'application/json'
                             })
closes = response.json().get('chart').get('result')[0].get('indicators').get('quote')[0].get('close')
times = response.json().get('chart').get('result')[0].get('timestamp')
#print(closes)

df = pd.DataFrame({'closes': closes, 'times': times})
df['times'] = pd.to_datetime(df['times'], unit='s')
df = df.set_index('times')

# is_NaN = df.isnull()
# row_has_NaN = is_NaN.any(axis=1)
# rows_with_NaN = df[row_has_NaN]

# print(rows_with_NaN)

df = df.interpolate()

# trade when:
# a. EMA's cross
# b. RSI >70 = overbought: do not buy
#    RSI <30 = oversold: sell

def trade(ema_fast, ema_slow, rsi, rsi_max, num_shares):
    df['ema_fast'] = ema(df['closes'], ema_fast)
    df['ema_slow'] = ema(df['closes'], ema_slow)
    df['rsi'] = talib.RSI(df['closes'], rsi) # try 2 to 6; 14 is normal
    #print(df)

    df['position'] = np.where(df['ema_fast'] > df['ema_slow'], 1, 0)
    df['signal'] = df['position'].diff()

    returns = 0
    boughtAt = 0
    profit = 0
    numTrades = 0
    commission = 0.35
    CountPL = False
    initialInvestment = 0

    for i, row in df.iterrows():
        if row['signal'] == 1.0 and row['rsi'] < rsi_max:
            boughtAt = row['closes']
            initialInvestment = num_shares * boughtAt
        elif row['signal'] == -1.0 and boughtAt > 0:
            soldAt = row['closes']
            priceDiff = num_shares * (soldAt - boughtAt)
            print("Bought: "+str(boughtAt)+"  Sold:  "+str(soldAt)+"  Diff: "+str(priceDiff))
            numTrades += 1
            if not np.isnan(priceDiff):
                profit += (priceDiff - 2*commission)
    print("initialInvestment: "+str(initialInvestment))
    print("ema_fast: "+str(ema_fast)+" ema_slow: "+str(ema_slow)+" rsi: "+str(rsi)+" trades: "+str(numTrades)+" profit: "+str(profit))

# trade(5, 8)
# trade(5, 12)
# trade(5, 20)

# trade(12, 12)
# trade(12, 20)
trade(12, 50, 2, 65, 100)

# ema_fast: 12 ema_slow: 50 rsi: 12 trades: 39 profit: 1867.0598388671897
# ema_fast: 12 ema_slow: 50 rsi: 12 trades: 38 profit: 2735.4701416015646
# ema_fast: 12 ema_slow: 50 rsi: 8 trades: 38 profit: 3318.2612792968707
# ema_fast: 12 ema_slow: 50 rsi: 6 trades: 37 profit: 2215.126171874995
# ema_fast: 12 ema_slow: 50 rsi: 2 trades: 37 profit: 7608.0857666015545
# ema_fast: 12 ema_slow: 50 rsi: 2 trades: 37 profit: 8048.185864257803
# ema_fast: 12 ema_slow: 50 rsi: 2 rsi_max: 65 trades: 37 profit: 10420.295849609367

#print(df)
