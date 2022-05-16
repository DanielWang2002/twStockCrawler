import talib
import pandas as pd
import yF_Kbar


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

    df["RSI_5"] = talib.RSI(df["收盤價"], 5)
    df["RSI_5_T1"] = df["RSI_5"].shift(1)
    df["RSI_5_T2"] = df["RSI_5"].shift(2)

    df["SMA_20"] = talib.SMA(df["收盤價"], 20)
    df["SMA_20_T1"] = df["SMA_20"].shift(1)

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

        buy_condition_1 = (row["RSI_5_T1"] <= row["RSI_5_T2"]) and (row["RSI_5_T1"] < row["RSI_5"])
        buy_condition_2 = row["SMA_20"] > row["SMA_20_T1"]

        sell_condition_1 = (row["RSI_5_T1"] >= row["RSI_5_T2"]) and (row["RSI_5_T1"] > row["RSI_5"])
        sell_condition_2 = row["macd"] < 0 and row["signal"] < 0

        if (buy_condition_1 and buy_condition_2) and hold == 0:
            df.at[index, "Buy"] = row["收盤價"]
            hold = 1
        elif (sell_condition_1 and sell_condition_2) and hold == 1:
            df.at[index, "Sell"] = row["收盤價"]
            hold = 0

    return df


def get_KPI(df):
    # 將買賣價格配對
    record_df = pd.DataFrame()
    record_df["Buy"] = df["Buy"].dropna().to_list()
    record_df["Sell"] = df["Sell"].dropna().to_list()
    record_df["Buy_fee"] = record_df["Buy"] * 0.001425
    record_df["Sell_fee"] = record_df["Sell"] * 0.001425
    record_df["Sell_tax"] = record_df["Sell"] * 0.003

    # 交易次數
    trade_time = record_df.shape[0]

    # 總報酬
    record_df["profit"] = (record_df["Sell"] - record_df["Buy"] - record_df["Buy_fee"] - record_df["Sell_fee"] -
                           record_df["Sell_tax"]) * 1000
    total_profit = record_df["profit"].sum()

    # 成敗次數
    win_times = (record_df["profit"] >= 0).sum()
    loss_times = (record_df["profit"] < 0).sum()

    # 勝率
    if trade_time > 0:
        win_rate = win_times / trade_time
    else:
        win_rate = 0

    # 獲利/虧損金額
    win_profit = record_df[record_df["profit"] >= 0]["profit"].sum()
    loss_profit = record_df[record_df["profit"] < 0]["profit"].sum()

    # 獲利因子
    if loss_profit == 0:
        profit_factor = 0
    else:
        profit_factor = abs(win_profit / loss_profit)

    # 平均獲利金額
    if win_times > 0:
        avg_win_profit = win_profit / win_times
    else:
        avg_win_profit = 0

    # 平均虧損金額
    if loss_times > 0:
        avg_loss_profit = loss_profit / loss_times
    else:
        avg_loss_profit = 0

    # 賺賠比
    if avg_loss_profit > 0:
        profit_rate = abs(avg_win_profit / avg_loss_profit)
    else:
        profit_rate = 0

    # 最大單筆獲利
    max_profit = record_df["profit"].max()

    # 最大單筆虧損
    max_loss = record_df["profit"].min()

    # 最大回落MDD
    record_df["acu_profit"] = record_df["profit"].cumsum()  # 累積報酬
    MDD = 0
    peak = 0
    for i in record_df["acu_profit"]:
        if i > peak:
            peak = i
        diff = peak - i
        if diff > MDD:
            MDD = diff

    # KPI文字
    result_txt = f"\
     交易次數：{trade_time} \n \
    總報酬：{total_profit} \n \
    成功次數：{win_times} \n \
    虧損次數：{loss_times} \n \
    勝率：{win_rate} \n \
    獲利總金額：{win_profit}  \n \
    虧損總金額：{loss_profit} \n \
    獲利因子：{profit_factor} \n \
    平均獲利金額：{avg_win_profit} \n \
    平均虧損金額：{avg_loss_profit} \n \
    賺賠比：{profit_rate} \n \
    最大單筆獲利：{max_profit} \n \
    最大單筆虧損：{max_loss} \n \
    MDD：{MDD}"

    return result_txt


def main(stock_id, period="12mo"):
    df = get_TA(stock_id, period)
    df = trade(df)

    # 取得KPI文字
    result_text = get_KPI(df)

    return df, result_text


if __name__ == "__main__":
    df, result_text = main(2330)
    print(df, result_text)