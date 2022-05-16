import yfinance as yf
import mplfinance as fplt

stock_id = "2330.TW"
data = yf.Ticker(stock_id)

ohlc = data.history(period='2mo')

df = ohlc.loc[: , ["Open", "High", "Low", "Close", "Volume"]]
print(df)

df.rename(columns = {"開盤價" : "Open", 
                     "最高價" : "High",
                     "最低價" : "Low",
                     "收盤價" : "Close",
                     "交易量" : "Volume"},
                     inplace = True)

mc = fplt.make_marketcolors(
                            up = 'tab:red', down = 'tab:green', 
                            wick = {'up':'red', 'down':'green'},
                            volume = 'tab:green'
                            )

s = fplt.make_mpf_style(marketcolors = mc)

fplt.plot(
        df,
        type = 'candle',
        style = s,
        title = stock_id,
        ylabel = 'Price ($)',
        volume = True,
        savefig = f"stock_kbar{stock_id}.png"
    )