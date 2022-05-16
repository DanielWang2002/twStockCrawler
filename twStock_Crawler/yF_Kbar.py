import yfinance as yf
import mplfinance as fplt

def get_data(stock_id, period):
    stock_id = f"{stock_id}.TW"
    data = yf.Ticker(stock_id)

    # 1mo = 1 month
    # max 可以下載所有期間的資料
    ohlc = data.history(period=period)

    ohlc = ohlc.loc[:, ["Open", "High", "Low", "Close", "Volume"]]

    return ohlc


def draw_candle_chart(stock_id, df):
    # 配合程式更改欄位名稱
    df.rename(columns={"開盤價": "Open",
                       "最高價": "High",
                       "最低價": "Low",
                       "收盤價": "Close",
                       "交易量": "Volume"}
              , inplace=True)

    # 調整圖表標示顏色
    mc = fplt.make_marketcolors(
        up='tab:red', down='tab:green',  # 上漲為紅，下跌為綠
        wick={'up': 'red', 'down': 'green'},  # 影線上漲為紅，下跌為綠
        volume='tab:green',  # 交易量顏色
    )

    s = fplt.make_mpf_style(marketcolors=mc)  # 定義圖表風格

    fplt.plot(
        df,  # 開高低收量的資料
        type='candle',  # 類型為蠟燭圖，也就是 K 線圖
        style=s,  # 套用圖表風格
        title=str(stock_id),  # 設定圖表標題
        ylabel='Price ($)',  # 設定 Y 軸標題
        volume=True,
        savefig='stock_Kbar.png',  # 儲存檔案
    )

if __name__ == "__main__":
    df = get_data(1101)
    # 配合程式更改欄位名稱
    df.rename(columns = {"Open" : "開盤價",
               "High" : "最高價",
               "Low" : "最低價",
               "Close" : "收盤價",
               "Volume" : "交易量"}
              , inplace = True)
    df["Buy"] = None
    df["Sell"] = None

    draw_candle_chart(1101, df)