#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import os

os.chdir("C:/Users/cogus/Documents/seminar2025")
print(os.getcwd())


# In[3]:


# 검색량 데이터 불러오기 및 처리

search_trim = pd.read_excel("SearchVolume_HLB.xlsx", sheet_name="개요", header=6)
search_trim = search_trim.rename(columns={"날짜": "date", "HLB": "search_raw"})

search_trim["date"] = pd.to_datetime(search_trim["date"])
search_trim["search_raw"] = pd.to_numeric(search_trim["search_raw"], errors="coerce")

print(search_trim.head())


# In[5]:


# 주가 데이터 불러오기 및 처리
stock_raw = pd.read_excel("StockPrice_HLB.xlsx", sheet_name="Sheet1")
stock_trim = stock_raw.rename(columns={"일자": "date", "거래량": "volume", "종가": "close"}).copy()

stock_trim["date"] = pd.to_datetime(stock_trim["date"], format="%Y/%m/%d", errors="coerce")
stock_trim["volume"] = (
    stock_trim["volume"].astype(str).str.replace(",", "", regex=False)
    .astype(float).astype("Int64")
)
stock_trim["close"] = pd.to_numeric(stock_trim["close"], errors="coerce")

stock_trim = stock_trim.dropna(subset=["date", "volume"]).sort_values("date")
print(stock_trim.head())  


# In[7]:


# 거래일 기준으로 데이터 병합
merged = (
    stock_trim[["date", "close", "volume"]]
    .merge(search_trim, on="date", how="inner")
    .sort_values("date").reset_index(drop=True)
)

# 로그차분 (Granger용)
eps = 1e-9
merged["log_volume"] = np.log(merged["volume"] + eps)
merged["log_search"] = np.log(merged["search_raw"] + eps)
merged["dlog_volume"] = merged["log_volume"].diff()
merged["dlog_search"] = merged["log_search"].diff()

granger_ready = merged.dropna(subset=["dlog_volume", "dlog_search"]).reset_index(drop=True)


# In[9]:


# 전처리 데이터 최종 확인
print(merged.head())
print(granger_ready.head())


# In[11]:


# 데이터 저장

merged.to_csv("PrepData_HLB(merged).csv", index=False)
granger_ready.to_csv("DlogPrepData_HLB(merged).csv", index=False)

