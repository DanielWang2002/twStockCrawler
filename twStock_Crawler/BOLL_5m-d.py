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

    # 布林通道 args: close 20 0
    df['upper'], df['middle'], df['lower'] = talib.BBANDS(df['收盤價'], timeperiod=10, nbdevup=2, nbdevdn=2, matype=0)

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
        # 最低價碰到下軌
        buy_condition_1 = row['最低價'] <= row['lower']
        ##########----------買進條件----------##########

        ##########----------賣出條件----------##########
        # 收盤價 <= 布林中軌
        sell_condition_1 = row['最高價'] >= row['upper']
        ##########----------賣出條件----------##########

        if buy_condition_1 and hold == 0:
            # 以下軌價格購買，因為真的交易時不會知道最低點在哪
            df.at[index, "Buy"] = row["lower"]
            print(f'Buy {index}')
            hold = 1
        elif sell_condition_1 and hold == 1:
            # 以上軌價格賣出，理由同上
            df.at[index, "Sell"] = row["upper"]
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
    df, result_text = main('5288', '1mo', '15m')
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
