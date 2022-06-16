import talib
import pandas as pd
import yF_Kbar

import getKPI

def get_MA(stock_id, period = "12mo"):
    df = yF_Kbar.get_data(stock_id, period)

    # 配合程式更改欄位名稱
    df.rename(columns={"Open": "開盤價",
                       "High": "最高價",
                       "Low": "最低價",
                       "Close": "收盤價",
                       "Volume": "交易量"}
              , inplace=True)

    df["Buy"] = pd.NA
    df["Sell"] = pd.NA
    df["MA5"] = talib.SMA(df["收盤價"], 5)
    df["MA20"] = talib.SMA(df["收盤價"], 20)

    # MA5與MA20的交叉
    df["diff"] = df["MA5"] - df["MA20"]

    # df = df.dropna() # 去除空值
    df["upper_lower"] = df["diff"] > 0  # MA5是否超過MA20
    df["last_upper_lower"] = df["upper_lower"].shift(-1)  # 前一天的狀態
    df["sign"] = df["last_upper_lower"] != df["upper_lower"]  # 判斷是否與前一天狀態一樣
    return df


def trade(df):
    df["Buy"] = None
    df["Sell"] = None

    last_index = df.index[-1]
    hold = 0  # 是否持有
    for index, row in df.copy().iterrows():
        # 最後一天不交易，並將部位平倉
        if index == last_index:
            if hold == 1:  # 若持有部位，平倉
                df.at[index, "Sell"] = row["收盤價"]  # 紀錄賣價
                hold = 0
            break  # 跳出迴圈

        # 與前一天的狀態不一樣，今天的MA5比MA10高，沒有持有股票，符合以上條件買入
        if not (row["sign"]) and row["upper_lower"] and hold == 0:
            df.at[index, "Buy"] = row["收盤價"]  # 記錄買價
            hold = 1
        # 與前一天的狀態不一樣，今天的MA5比MA10低，有持有股票，符合以上條件賣出
        elif not (row["sign"]) and not (row["upper_lower"]) and hold == 1:
            df.at[index, "Sell"] = row["收盤價"]  # 紀錄賣價
            hold = 0

    return df



def main(stock_id, period = "12mo"):
    df = get_MA(stock_id, period)
    df = trade(df)

    # 取得KPI文字
    KPI_df = getKPI.get_KPI(df)

    return df, KPI_df

if __name__ == "__main__":
    df, result_text = main(3583)
    print(df, result_text)