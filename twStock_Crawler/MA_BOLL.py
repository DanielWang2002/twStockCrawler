import talib
import pandas as pd
import yF_Kbar

import getKPI


def get_TA(stock_id, period="12mo", interval='1d'):
    # get Data
    df = yF_Kbar.get_data(stock_id, period, interval)

    df.rename(columns={
        "Open": "開盤價",
        "High": "最高價",
        "Low": "最低價",
        "Close": "收盤價",
        "Volume": "交易量"
    }, inplace=True)

    df["Buy"] = None
    df["Sell"] = None

    # 今日、前一日、前二日 MA5
    df['MA5'] = talib.MA(df['收盤價'], 5)
    df['MA5_T1'] = df['MA5'].shift(1)
    df['MA5_T2'] = df['MA5'].shift(2)

    # 今日、前一日、前二日 MA10
    df['MA10'] = talib.MA(df['收盤價'], 10)
    df['MA10_T1'] = df['MA10'].shift(1)
    df['MA10_T2'] = df['MA10'].shift(2)

    # 今日、前一日、前二日 MA20
    df['MA20'] = talib.MA(df['收盤價'], 20)
    df['MA20_T1'] = df['MA20'].shift(1)
    df['MA20_T2'] = df['MA20'].shift(2)

    # 今日、前一日、前二日 MA60
    df['MA60'] = talib.MA(df['收盤價'], 60)
    df['MA60_T1'] = df['MA60'].shift(1)
    df['MA60_T2'] = df['MA60'].shift(2)

    # 布林通道 args: close 20 0
    df['upper'], df['middle'], df['lower'] = talib.BBANDS(df['收盤價'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

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

        ##########----------買進條件----------##########
        # 今日MA5 > 昨日MA5 > 前日MA5
        buy_condition_1 = row['MA5'] > row['MA5_T1'] > row['MA5_T2']

        # 今日MA10 > 昨日MA10 > 前日MA10
        buy_condition_2 = row['MA10'] > row['MA10_T1'] > row['MA10_T2']

        # 今日MA20 > 昨日MA20 > 前日MA20
        buy_condition_3 = row['MA20'] > row['MA20_T1'] > row['MA20_T2']

        # 突破布林上軌
        buy_condition_5 = row['收盤價'] >= row['upper']
        ##########----------買進條件----------##########

        ##########----------賣出條件----------##########
        # 收盤價 <= 布林中軌
        sell_condition_1 = row['收盤價'] <= row['middle']

        # 今日MA5 <= 昨日MA5 <= 前日MA5
        sell_condition_2 = row['MA5'] <= row['MA5_T1']
        ##########----------賣出條件----------##########

        # (buy_condition_1 and buy_condition_2 and buy_condition_3 and buy_condition_4 and buy_condition_5)
        if (buy_condition_1 and buy_condition_2 and buy_condition_3 and buy_condition_5) and hold == 0:
            df.at[index, "Buy"] = row["收盤價"]
            print(f'Buy {index}')
            hold = 1
        elif (sell_condition_1 and sell_condition_2) and hold == 1:
            df.at[index, "Sell"] = row["收盤價"]
            print(f'Sell {index}')
            hold = 0

    return df

def main(stock_id, period="12mo", interval='1d'):
    df = get_TA(stock_id, period, interval)
    df = trade(df)

    # 取得KPI文字
    KPI_df = getKPI.get_KPI(df)

    return df, KPI_df


if __name__ == "__main__":
    # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    df, result_text = main(2317, '36mo', '1d')
    print(df)
    print(result_text)

    # for i in range(1100, 10000, 1):
    #     try:
    #         df, result_text = main(i, "36mo", '15m')
    #         if result_text['數值']['交易次數'] > 10:
    #             print('--------------------')
    #             print(f"股票代號 {i}")
    #             print(f"交易次數: {result_text['數值']['交易次數']}")
    #             print(f"總報酬: {result_text['數值']['總報酬']}")
    #             print(f"勝率: {result_text['數值']['勝率']}")
    #             print('--------------------')
    #
    #     except :
    #         print(f"股票代號 {i} 不存在或非上市股票")
