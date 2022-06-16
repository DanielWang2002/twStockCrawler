import talib
import pandas as pd
import yF_Kbar

import getKPI

def get_TA(stock_id, period="12mo"):
    # get Data
    df = yF_Kbar.get_data(stock_id, period)

    df.rename(columns={
        "Open": "開盤價",
        "High": "最高價",
        "Low": "最低價",
        "Close": "收盤價",
        "Volume": "交易量"
    }, inplace=True)

    df["Buy"] = None
    df["Sell"] = None

    # Absolute Price Oscillator
    df["OSC_5"] = talib.APO(df["收盤價"], 5)
    df["OSC_5_T1"] = df["OSC_5"].shift(1)
    df["OSC_5_T2"] = df["OSC_5"].shift(2)

    # DI
    df["DI_5"] = talib.PLUS_DI(df["最高價"], df["最低價"], df["收盤價"])
    df["DI_5_T1"] = df["DI_5"].shift(1)
    df["DI_5_T2"] = df["DI_5"].shift(2)

    df["SMA_20"] = talib.SMA(df["收盤價"], 20)
    df["SMA_20_T1"] = df["SMA_20"].shift(1)

    fastPeriod = 12
    slowPeriod = 26
    signalPeriod = 9

    df["macd"], df["signal"], df["hist"], = talib.MACD(df["收盤價"],
                                                       fastperiod=fastPeriod,
                                                       slowperiod=slowPeriod,
                                                       signalperiod=signalPeriod)
    # df["OSC_5"] = df['macd'] - df['signal']
    # df["OSC_5_T1"] = df["OSC_5"].shift(1)
    # df["OSC_5_T2"] = df["OSC_5"].shift(2)

    return df


def trade(df):
    df["Buy"] = None
    df["Sell"] = None

    last_index = df.index[-1]
    hold = 0

    for index, row in df.copy().iterrows():

        if index == last_index:
            if hold == 1:
                df.at[index, "Sell"] = row["收盤價"]
                hold = 0
            break

        buy_condition_1 = (row["DI_5_T1"] < row["DI_5_T2"]) and (row["DI_5_T1"] < row["DI_5"])
        buy_condition_2 = row["SMA_20"] > row["SMA_20_T1"]

        sell_condition_1 = (row["OSC_5_T1"] >= row["OSC_5_T2"]) and (row["OSC_5_T1"] > row["OSC_5"])
        sell_condition_2 = row["SMA_20"] < row["SMA_20_T1"]

        if (buy_condition_1 and buy_condition_2) and hold == 0:
            df.at[index, "Buy"] = row["收盤價"]
            hold = 1
        elif (sell_condition_1 and sell_condition_2) and hold == 1:
            df.at[index, "Sell"] = row["收盤價"]
            hold = 0

    return df


def main(stock_id, period="12mo"):
    df = get_TA(stock_id, period)
    df = trade(df)

    # 取得KPI文字
    KPI_df = getKPI.get_KPI(df)

    return df, KPI_df


if __name__ == "__main__":
    df, result_text = main(2330, "1mo")
    print(df, result_text)
