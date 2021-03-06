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

    # KD args: 14, 1, 3
    df['K'], df['D'] = talib.STOCHRSI(df['收盤價'].round(decimals = 1), timeperiod=14, fastk_period=5, fastd_period=3)
    df['K_T1'] = df['K'].shift(1)
    df['D_T1'] = df['D'].shift(1)

    fastPeriod = 12
    slowPeriod = 26
    signalPeriod = 9

    df["macd"], df["signal"], df["hist"], = talib.MACD(df["收盤價"],
                                                       fastperiod=fastPeriod,
                                                       slowperiod=slowPeriod,
                                                       signalperiod=signalPeriod)

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
        # KD黃金交叉
        buy_condition_1 = (row['K'] > row['K_T1']) and (row['D'] < row['D_T1']) and (row['K'] >= row['D'])
        buy_condition_2 = (row['K'] <= 20) or (row['D'] <= 20)
        ##########----------買進條件----------##########

        ##########----------賣出條件----------##########
        # KD死亡交叉
        sell_condition_1 = (row['K'] < row['K_T1']) and (row['D'] > row['D_T1']) and (row['K'] <= row['D'])
        sell_condition_2 = (row['K'] >= 80) or (row['D'] >= 80)
        ##########----------賣出條件----------##########

        if (buy_condition_1 and buy_condition_2) and hold == 0:
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
    df, result_text = main(2002, '1mo', '5m')
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
