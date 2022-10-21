import requests, gspread, string, datetime, json, pprint
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

def zone_to_be_filled(origin = 'A1', n_row = 1, m_column = 1):
    # return a spreadsheet zone starting at origine including n rows and m column
    # DANGER not valid above 'Z' column
    column_start, row_start = origin[0], int(origin[1])
    row_end = row_start + n_row - 1
    column_end = chr(ord(column_start) + m_column - 1)
    zone = origin + ':' + column_end + str(row_end)
    return zone

pp = pprint.PrettyPrinter(indent=4)

# API eys, sheet keys and lent stocks are saved in files in an external repertory see the readKeysLib module
APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
repertory = sheetKey_dict['rep']
# lentStock_dict = readKeysLib.getLentStocks() # deprecated data in spreadsheet now

# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile = repertory + sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)

##### Open spreadsheet and write update references
sheetKey = sheetKey_dict['TornStats']
ws_All = gc.open_by_key(sheetKey).worksheet('Stocks_All')
ws_Players = gc.open_by_key(sheetKey).worksheet('Stocks_Players')

# Write the date and update current_row # modif Manu

current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
ws_All.update_cell(1,1,'Updated by ' + nodeName)
ws_All.update_cell(1,2,current_date)
ws_Players.update_cell(1,1,'Updated by ' + nodeName)
ws_Players.update_cell(1,2,current_date)

stocks_keys = 'name', 'acronym', 'current_price'
stocks_benefit = 'description', 'frequency', 'requirement', 'type'
stocks_info_array = [list(stocks_keys) + list(stocks_benefit)]
# print(stocks_info_array)
APIKey = APIKey_dict["Kwartz"]
rs = requests.get(f'https://api.torn.com/torn/?selections=stocks&key={APIKey}').json()['stocks']
for stock_num, stock_info in rs.items():
    L1 = [stock_info[name] for name in stocks_keys]
    L2 = [stock_info['benefit'][name] for name in stocks_benefit]
    stocks_info_array.append(L1 +L2)

zone_stocks = zone_to_be_filled('A3', len(stocks_info_array), len(L1 + L2))
# ws_All.update(zone_stocks, stocks_info_array)

for player in ["Kwartz", "Kivou"]:
    total = 0
    APIKey = APIKey_dict[player]
    rp = requests.get(f'https://api.torn.com/user/?selections=stocks&key={APIKey}').json()['stocks']
    stocks_keys = ['name', 'acronym', 'total_shares', 'value', 'increments']
    stocks_perso_array = [stocks_keys]
    for stock_num, stock_data in rp.items():
        stock_info = rs[stock_num]
        value = int(stock_data['total_shares']) * stock_info['current_price']
        total += value
        if stock_info['benefit']['type'] == 'active':
            increments = stock_data['dividend']['increment']
        else:
            increments = stock_data['benefit']['increment']
        L = [stock_info['name'], stock_info['acronym'], int(stock_data['total_shares']), value, increments,stock_info['benefit']['type'] == 'active']
        stocks_perso_array.append(L)
    if player == "Kwartz":
        origin, total_cell = 'A3', 'D2'
    else:
        origin, total_cell = 'G3', 'J2'
    zone_stocks = zone_to_be_filled(origin, len(stocks_perso_array), len(L))
    #print('spreadsheet zone to be filled : ', zone_stocks)
    #pp.pprint(stocks_perso_array)
    ws_Players.update(zone_stocks, stocks_perso_array)
    ws_Players.update(total_cell, total)


# {   'stocks': {   '1': {   'acronym': 'TSB',
#                            'benefit': {   'description': '$50,000,000',
#                                           'frequency': 31,
#                                           'requirement': 3000000,
#                                           'type': 'active'},
#                            'current_price': 1048.65,
#                            'investors': 8272,
#                            'market_cap': 13044681377183,
#                            'name': 'Torn & Shanghai Banking',
#                            'stock_id': 1,
#                            'total_shares': 12439499716},
#                   '10': {   'acronym': 'CNC',
#                             'benefit': {   'description': '$80,000,000',
