#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from datetime import timedelta,datetime
from statsmodels.tsa.stattools import grangercausalitytests,adfuller

import os

os.chdir("C:/Users/cogus/Documents/seminar2025/SHINSUNG DELTATECH")
print(os.getcwd())


# In[3]:


df = pd.read_csv("DlogPrepData_Shinsung(merged).csv")


# In[7]:


df["date"] = pd.to_datetime(df["date"])
start_date = df.iloc[0]["date"]
dates = [(start_date +i*timedelta(days = 1),start_date +i*timedelta(days = 1)+timedelta(days = 15)) for i in range(1,60)]

max_lag = 1
results = []


# In[9]:


for date in dates:
    # 윈도우 잘라내기
    gdf = df[(df["date"] > date[0]) & (df["date"] < date[1])]
    
    # ADF 테스트
    dftest = adfuller(gdf["dlog_volume"],regression = "c", maxlag = max_lag)
    df_p_vol = dftest[1] #P값
    df_ts_vol = dftest[0] #검정통계량
    
    dftest = adfuller(gdf["dlog_search"],regression = "c", maxlag = max_lag)
    df_p_search = dftest[1]
    df_ts_search = dftest[0]

    # Granger(lag1)
    # 검색량 → 거래량
    #in the second column Granger causes the time series in the first column
    gc_res = grangercausalitytests(gdf[["dlog_volume","dlog_search"]], max_lag,verbose = False,addconst = True)[1]
    gc_p = gc_res[0]["ssr_ftest"][1] #pvalue
    
    res_single = gc_res[1][0] #자기 자신의 과거값만 (제한 모형)
    res_both = gc_res[1][1] # 자기 자신의 과거값 + 검색량 과거값 (전체모형 unrestricted)

    # SSR
    ssr_single = res_single.ssr
    ssr_both = res_both.ssr

    # 제한모형 대비 전체모형에서 얼마나 줄었는지 비율 계산
    gc_index_internet_to_market = np.log10(ssr_single/ssr_both)
    # P값 저장
    p_value_internet_to_market = gc_p

    #### 이하 위와 같음
    # 거래량 → 검색량
    #in the second column Granger causes the time series in the first column
    gc_res = grangercausalitytests(gdf[["dlog_search","dlog_volume"]], max_lag,verbose = False,addconst = True)[1]
    gc_p = gc_res[0]["ssr_ftest"][1]
    
    res_single = gc_res[1][0]
    res_both = gc_res[1][1]
    
    ssr_single = res_single.ssr
    ssr_both = res_both.ssr
    
    gc_index_market_to_internet = np.log10(ssr_single/ssr_both)
    p_value_market_to_internet = gc_p
    
    # save
    results.append({
    "Date": date[1],

    # ADF (정상성 검정)
    "t (Trading Volume)": round(df_ts_vol, 3),
    "p-value (Trading Volume)": round(df_p_vol, 3),
    "t (Search)": round(df_ts_search, 3),
    "p-value (Search)": round(df_p_search, 3),

    # Granger (인과성 검정)
    "GC-index (Search → Trading Volume)": round(gc_index_internet_to_market, 3),
    "p-value (Search → Trading Volume)": round(p_value_internet_to_market, 3),

    "GC-index (Trading Volume → Search)": round(gc_index_market_to_internet, 3),
    "p-value (Trading Volume → Search)": round(p_value_market_to_internet, 3),
})


# In[11]:


df_results = pd.DataFrame(results)
df_results.to_csv("Shinsung_ADF_results.csv", index=False)

