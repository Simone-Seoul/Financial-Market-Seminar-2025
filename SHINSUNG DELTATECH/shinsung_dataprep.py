#!/usr/bin/env python
# coding: utf-8

# In[23]:


import pandas as pd, numpy as np

# 파일 불러오기
file_search = "C:/Users/cogus/Documents/seminar2025/datalab_HLB.xlsx"
file_stock  = "C:/Users/cogus/Documents/seminar2025/신성델타테크.xlsx"

# 파일 읽기
search_raw = pd.read_excel(file_search, sheet_name="개요")
stock_raw  = pd.read_excel(file_stock,  sheet_name="Sheet1")


# In[29]:


# 검색량 날짜/볼륨 필터링
search_trim = pd.read_excel("datalab_신성.xlsx", sheet_name="개요", header=6)
search_trim = search_trim.rename(columns={"날짜":"date", "신성델타테크":"search_raw"})
search_trim["date"] = pd.to_datetime(search_trim["date"])
search_trim["search_raw"] = pd.to_numeric(search_trim["search_raw"], errors="coerce")
print(search_trim.head())


# In[31]:


# 주가/거래량 필터링
stock_trim = stock_raw.rename(columns={"일자":"date","거래량":"volume","종가":"close"}).copy()
stock_trim["date"] = pd.to_datetime(stock_trim["date"], format="%Y/%m/%d", errors="coerce")
stock_trim["volume"] = (
    stock_trim["volume"].astype(str).str.replace(",", "", regex=False)
    .astype(float).astype("Int64")
)
stock_trim["close"] = pd.to_numeric(stock_trim["close"], errors="coerce")
stock_trim = stock_trim.dropna(subset=["date","volume"]).sort_values("date")


# In[33]:


print(stock_trim.head())


# In[35]:


# 거래일 기준으로 데이터 병합
merged = (stock_trim[["date","close","volume"]]
          .merge(search_trim, on="date", how="inner")
          .sort_values("date").reset_index(drop=True))

# 로그차분 (Granger용)
eps = 1e-9
merged["log_volume"] = np.log(merged["volume"] + eps)
merged["log_search"] = np.log(merged["search_raw"] + eps)
merged["dlog_volume"] = merged["log_volume"].diff()
merged["dlog_search"] = merged["log_search"].diff()

granger_ready = merged.dropna(subset=["dlog_volume","dlog_search"]).reset_index(drop=True)


# In[39]:


print(merged.head())
print(granger_ready.head())


# In[43]:


# 데이터 저장~ 했는데 어디갔지 ㅅㅂ
merged.to_csv("신성델타테크_검색량_거래량_머지_raw.csv", index=False)
granger_ready.to_csv("신성델타테크_검색량_거래량_Granger용_dlog.csv", index=False)


# In[41]:


# (번외)디렉토리 설정만 잘 해도 뭔가 해결이 되는 경우가 많음
import os
os.getcwd()


# In[17]:


os.chdir("C:/Users/cogus/Documents/seminar2025")
print(os.getcwd())

