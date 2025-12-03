import xarray as xr
import pandas as pd
import os
from read import read_nc_files

df = pd.read_parquet("data/rawtimeseries.parquet")

print(df.columns.tolist())
print(df.head(25))

df["prWeek"] = df["prAdjust"].rolling(window=7,   min_periods=1).sum()
df["prMonth"] = df["prAdjust"].rolling(window=31,  min_periods=1).sum()
df["prYear"] = df["prAdjust"].rolling(window=365, min_periods=1).sum()

df["tasWeekAverage"] = df["tasAdjust"].rolling(window=7,   min_periods=1).mean()
df["tasWeekMax"] = df["tasAdjust"].rolling(window=7,   min_periods=1).max()
df["tasWeekMin"] = df["tasAdjust"].rolling(window=7,   min_periods=1).min()

df["tasMonthAverage"] = df["tasAdjust"].rolling(window=31,   min_periods=1).mean()
df["tasYearAverage"] = df["tasAdjust"].rolling(window=365,   min_periods=1).mean()

df["tasLag_1"] = df["tasAdjust"].shift(1)
df["tasLag_2"] = df["tasAdjust"].shift(2)
df["tasLag_3"] = df["tasAdjust"].shift(3)

df["prLag_1"] = df["prAdjust"].shift(1)
df["prLag_2"] = df["prAdjust"].shift(2)
df["prLag_3"] = df["prAdjust"].shift(3)

print(df.columns.tolist()) 
print(df.head(25))

df.to_parquet("data/feature_engineering_V1.parquet")