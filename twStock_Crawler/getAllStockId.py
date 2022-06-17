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

if __name__ == "__main__":
    print(getAllStockId())