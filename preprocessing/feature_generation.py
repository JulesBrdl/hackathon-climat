import pandas as pd
import os
from read import read_nc_files

if not os.path.exists("./data/feature_engineering_V1_2004_2024.parquet"):
    print("2004-2024")

    df = pd.read_parquet("data/raw_2004_2024.parquet")

    print(df.columns.tolist())
    print(df.head(25))

    df["prWeek"] = df["prAdjust"].rolling(window=7, min_periods=1).sum()
    df["prMonth"] = df["prAdjust"].rolling(window=31, min_periods=1).sum()

    df["tasWeekAverage"] = df["tasAdjust"].rolling(window=7, min_periods=1).mean()
    df["tasWeekMax"] = df["tasAdjust"].rolling(window=7, min_periods=1).max()
    df["tasWeekMin"] = df["tasAdjust"].rolling(window=7, min_periods=1).min()

    df["tasMonthAverage"] = df["tasAdjust"].rolling(window=31, min_periods=1).mean()

    print(df.columns.tolist()) 
    print(df.head(25))

    df.to_parquet("data/feature_engineering_V1_2004_2024.parquet")

if not os.path.exists("./data/feature_engineering_V1_2025_2050.parquet"):
    print("2025-2050")

    df2 = pd.read_parquet("data/raw_2025_2050.parquet")

    print(df2.columns.tolist())
    print(df2.head(25))

    df2["prWeek"] = df2["prAdjust"].rolling(window=7, min_periods=1).sum()
    df2["prMonth"] = df2["prAdjust"].rolling(window=31, min_periods=1).sum()

    df2["tasWeekAverage"] = df2["tasAdjust"].rolling(window=7, min_periods=1).mean()
    df2["tasWeekMax"] = df2["tasAdjust"].rolling(window=7, min_periods=1).max()
    df2["tasWeekMin"] = df2["tasAdjust"].rolling(window=7, min_periods=1).min()

    df2["tasMonthAverage"] = df2["tasAdjust"].rolling(window=31, min_periods=1).mean()

    print(df2.columns.tolist()) 
    print(df2.head(25))

    df2.to_parquet("data/feature_engineering_V1_2025_2050.parquet")