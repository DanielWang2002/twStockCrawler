def getAllStockId():
    import requests
    import pandas as pd
    link = 'https://quality.data.gov.tw/dq_download_json.php?nid=11549&md5_url=bb878d47ffbe7b83bfc1b41d0b24946e'
    r = requests.get(link)
    data = pd.DataFrame(r.json())
    stockList = []
    for i in data['證券代號']:
        stockList.append(i)
    return stockList

def backtestingAllStock(strategy):
    # 獲取所有股票代號
    stockId = getAllStockId()

    trade_count = -1
    total_profit = -1
    win_rate = -1
    profit_rate = -1

    bestResult = None
    bestStockId = ''

    #  and (
    #                     result_text['數值']['勝率'] > 0.5 > win_rate) and (
    #                     result_text['數值']['賺賠比'] >= 1 > profit_rate)
    print('開始回測')
    for id in stockId:
        try:
            print(f'當前回測代號: {id}')
            df, result_text = strategy.main(id, '36mo', '1d')
            if (result_text['數值']['交易次數'] > trade_count) and (
                    result_text['數值']['總報酬'] > 0 > total_profit):
                trade_count = result_text['數值']['交易次數']
                total_profit = result_text['數值']['總報酬']
                win_rate = result_text['數值']['勝率']
                profit_rate = result_text['數值']['賺賠比']

                bestResult = result_text
                bestStockId = id

                print('--------------------')
                print(f"股票代號: {id}")
                print(f"交易次數: {result_text['數值']['交易次數']}")
                print(f"總報酬: {result_text['數值']['總報酬']}")
                print(f"勝率: {result_text['數值']['勝率']}")
                print(f"賺賠比: {result_text['數值']['賺賠比']}")
                print('--------------------')
        except:
            print('')

    print(f'績效最好的股票是: {bestStockId}')
    print(bestResult)


if __name__ == "__main__":
    print(getAllStockId())