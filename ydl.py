import pandas as pd
import json
import requests
import time
import calendar

pd.set_option("display.max_rows", 150, "display.min_rows", 150)

symbol = "TSLA"

print("Scraping data for "+symbol+" from Yahoo...")

def download_period(symbol, t1, t2):
  t2 = t2-1
  url = 'https://query1.finance.yahoo.com/v8/finance/chart/'+symbol+'?region=US&lang=en-US&includePrePost=false&interval=1m&corsDomain=finance.yahoo.com&.tsrc=finance'
  if t1 != None and t2 != None:
    url = url + '&period1='+str(t1)+'&period2='+str(t2)

  print(url)

  response = requests.get(url,
                             headers = {
                                 'User-Agent': 'request',
                                 'Accept': 'application/json'
                             })
  closes = response.json().get('chart').get('result')[0].get('indicators').get('quote')[0].get('close')
  times = response.json().get('chart').get('result')[0].get('timestamp')

  if closes[-1] == None:
    times.pop()
    closes.pop()

  df = pd.DataFrame({'closes': closes, 'times': times})
  df['times'] = pd.to_datetime(df['times'], unit='s')
  df = df.set_index('times')
  
  df = df.interpolate()
  t1 = times[0]
  t2 = times[-1]
  c1 = closes[0]
  c2 = closes[-1]
  print("t1: "+str(t1)+" t2: "+str(t2)+" c1: "+str(c1)+" c2: "+str(c2))
  df.to_pickle(symbol+"_"+str(t1)+"_"+str(t2)+".pick")
  return t1

seven_days_in_s = 60*60*24*7
time_ago_in_past = seven_days_in_s * 4
start_time_in_s = calendar.timegm(time.gmtime())

for t in range(start_time_in_s - time_ago_in_past, start_time_in_s, seven_days_in_s):
  download_period(symbol, t, t+seven_days_in_s)
