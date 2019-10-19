from handy import getKeys
from handy import apiCall
from handy import getSpreadsheet
from handy import I2A

# read all the keys
keys = getKeys("apiKeys.txt")

# set users you want to see the stocks details
# api key will be looked at api_username in apiKeys.txt
users = ["Kivou", "kwartz"]

# init the dictionary with torn stocks to bind ID with stock name
stocks = apiCall("torn", "stocks", keys["api_{}".format(users[0])])

# add personal stocks to the dictionary
sizeTmp = 0
for user in users:
    stocks[user] = apiCall("user", "stocks", keys["api_{}".format(user)])["stocks"]
    sizeTmp = max(sizeTmp, len(stocks[user]))

# set up connection to spreadsheet
gsJson = keys["gspread_json"]
gsID = keys["gspread_user_items"]
ss = getSpreadsheet(gsJson, gsID)

wsName = "StocksDetails"
ws = ss.worksheet(wsName)

# number of columns and rows
nCol = 3 * len(users)
hRow = 2  # headers
nRow = sizeTmp + hRow

# resize
print(nRow, nCol)
ws.resize(nRow, nCol)

# clean range
rangeString = 'A{}:{}{}'.format(1, I2A[nCol], nRow)
print(rangeString)
cell_list = ws.range(rangeString)
for i in range(len(cell_list)):
    cell_list[i].value = ""
ws.update_cells(cell_list)

# put stocks
i = 0
for user, userStocks in stocks.items():
    print(user)
    if user in users:
        cell_list[3 * i].value = user
        cell_list[nCol + 3 * i + 0].value = "Acronym"
        cell_list[nCol + 3 * i + 1].value = "Shares"
        cell_list[nCol + 3 * i + 2].value = "Bought Price"
        for j, (_, stock) in enumerate(userStocks.items()):
            cell_list[(j + 2) * nCol + 3 * i + 0].value = stocks["stocks"][str(stock["stock_id"])]["acronym"]
            cell_list[(j + 2) * nCol + 3 * i + 1].value = str(stock["shares"])
            cell_list[(j + 2) * nCol + 3 * i + 2].value = str(stock["bought_price"])

        i += 1
ws.update_cells(cell_list)
