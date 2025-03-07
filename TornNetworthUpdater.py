import requests, gspread, string, json, pprint
from datetime import datetime, timezone
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

pp = pprint.PrettyPrinter(indent=4)

# API eys, sheet keys and lent stocks are saved in files in an external repertory see the readKeysLib module
APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
repertory = sheetKey_dict['rep']
# lentStock_dict = readKeysLib.getLentStocks() # no more useful

# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile = repertory + sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)

def col_name(col_idx):
# Transforms a column index (integer starting from 1) to a spreadsheet string description A-Z-AA-AZ...AAA etc
    name = ""
    while col_idx > 0:
        mod = (col_idx - 1) % 26
        name = chr(65 + mod) + name
        col_idx = (col_idx - mod) // 26
    return name

def getFactionDonation(APIKey=''):
    try:
        rb = requests.get(f'https://api.torn.com/user/?selections=basic&key={APIKey}').json()
        r = requests.get(f'https://api.torn.com/faction/?selections=donations&key={APIKey}').json()
        faction_cash = r['donations'][str(rb['player_id'])]['money_balance']
        if faction_cash < 0:
            faction_cash = 0
        return faction_cash
    except KeyError as exception:
        print('Here is the KeyError :', exception)
        print('API key :', APIKey)
        return 0

def getNetworth(APIKey=''):
# STRUCTURE {"networth":{"pending":0,"wallet":300099,"bank":2270600000,"points":390267606,"cayman":0,"vault":935400000,"piggybank":null,"items":1072792534,"displaycase":88875999,"bazaar":7687,"properties":1087018000,"stockmarket":2004850585,"auctionhouse":0,"company":103827062,"bookie":null,"loan":0,"unpaidfees":0,"total":7953939572,"parsetime":0.06005597114562988}}
        r=requests.get(f'https://api.torn.com/user/?selections=networth&key={APIKey}').json()
        return r['networth']['total'],r['networth']['stockmarket'],r['networth']['company'],r['networth']['vault']

def getRacket(APIKey=''):
    r = requests.get(f'https://api.torn.com/torn/?selections=rackets&key={APIKey}').json()
    return r["rackets"]

def racket_evolution(APIKey=''):
    # racket evolution
    ws_R = gc.open_by_key(sheetKey).worksheet('R')
    territoryNameList = []
    col = 4
    territoryName = ws_NW_data.cell(1,col).value
    while len(territoryName) == 3:
        territoryNameList.append(territoryName)
        col += 1
        territoryName = ws_NW_data.cell(1,col).value
#    territoryNameList = [ws_NW_data.acell("D1").value, ws_NW_data.acell("E1").value]
    racket_dict = getRacket(APIKey)
    for indice, territoryName in enumerate(territoryNameList):
        old_row = ws_R.cell(1, 2+indice*5).value
        old_row = int(old_row.replace(",", "").replace(" ", ""))
        current_row = old_row + 1 # row where we will eventually write new data
        if territoryName in racket_dict:
            old_level = ws_R.cell(old_row, 3+indice*5).value
            old_level = int(old_level.replace(",", "").replace(" ", ""))
            new_level = int(racket_dict[territoryName]["level"])
            old_faction_name = ws_R.cell(old_row, 5+indice*5).value
            faction_ID = racket_dict[territoryName]["faction"]
            faction_name = requests.get(
                    f"https://api.torn.com/faction/{str(faction_ID)}\
                    ?selections=&key={APIKey}").json()["name"]
            if old_level != new_level or old_faction_name != faction_name:
                # racket level or racket owner has changed
                racket_name = racket_dict[territoryName]["name"]
                reward = racket_dict[territoryName]["reward"]
                L = [[current_date_num, racket_name, new_level, reward, faction_name]]
                zone_to_be_filled = ( col_name(1+indice*5) + str(current_row) + ":"
                                    + col_name(5+indice*5) + str(current_row) )
                ws_R.update(zone_to_be_filled, L)
        else:
            L = [[current_date_num, "THE END :("]]
            zone_to_be_filled = ( col_name(1+indice*5) + str(current_row) + ":"
                                + col_name(2+indice*5)+ str(current_row) )
            ws_R.update(zone_to_be_filled, L)
    ws_R.update_cell(2,2,nodeName)
    ws_R.update_cell(3,1,current_date_num)

# Open Tornstats sheets for NW update
sheetKey = sheetKey_dict['TornStats']
ws = gc.open_by_key(sheetKey).worksheet('NW')
ws_NW_data = gc.open_by_key(sheetKey).worksheet('NW_data')
# Current date in various format
date_now = datetime.now(timezone.utc)
current_date_str = date_now.strftime("%d/%m/%Y %H:%M:%S")
current_date_num = readKeysLib.python_date_to_excel_number(date_now)

# New feature, racket evolution
racket_evolution(APIKey_dict['Kwartz'])

# Get our networth informations and combine.
FactionDonationTotal = (getFactionDonation( APIKey_dict['Kivou'] ) +
                            getFactionDonation( APIKey_dict['Kwartz'] ) )
NetworthKivou,StockKivou,CompanyKivou,VaultKivou = getNetworth( APIKey_dict['Kivou'] )
NetworthKwartz,StockKwartz,CompanyKwartz,VaultKwartz = getNetworth( APIKey_dict['Kwartz'] )
NetworthTotal = NetworthKivou + NetworthKwartz
NetworthNet = NetworthTotal + FactionDonationTotal
StockTotal = StockKivou + StockKwartz
CompanyTotal = CompanyKivou + CompanyKwartz
VaultTotal = VaultKivou + VaultKwartz
Cash = VaultTotal + FactionDonationTotal

###### Add lent stocks and other investments
# Read lent stock information from NW_Data sheet in a dictionnary

LentStocks = {}
row = 4
stock_id = ws_NW_data.cell(row,1).value
while int(stock_id): # stop reading at first 0 in column "A"
    LentStocks[stock_id] = int(ws_NW_data.cell(row,2).value)
    row += 1
    stock_id = ws_NW_data.cell(row,1).value

# Compute lent stocks value
rs=requests.get(f'https://api.torn.com/torn/?selections=stocks&key={APIKey_dict["Kivou"]}').json()
LentStocksTotal = 0
for stock_id, n_increments in LentStocks.items():
    n_shares = rs["stocks"][stock_id]["benefit"]["requirement"]
    price = float(rs["stocks"][stock_id]["current_price"])
    stock_value = n_shares *  price
    LentStocksTotal += stock_value * n_increments

RealStocks = int(StockTotal + LentStocksTotal)

### ADD Oil Rig/TV network Participation
### cell B1 CAREFUL to number format in spreadsheet
Oil_Rig_Part = ws_NW_data.acell("B1").value
Oil_Rig_Part = int(Oil_Rig_Part.replace(",", "").replace(" ", ""))

### update TV networth value
Nub_TV_Part = ws_NW_data.acell("B2").value
Nub_TV_Part = int(Nub_TV_Part.replace(",", "").replace(" ", ""))

RealNetworth = int(NetworthNet + LentStocksTotal) + Oil_Rig_Part + Nub_TV_Part

current_row = int(ws.cell(1,2).value) + 1 # row where we will write new data

# Compute evolutions on N_average rows
N_average = 30
old_NW = ws.acell("H" + str(current_row - N_average)).value
old_NW =  int(old_NW.replace(",", "").replace(" ", "")) # remove trailing and inside spaces
old_date = ws.cell(current_row - N_average,1).value
old_date_dt = datetime.strptime(old_date, '%d/%m/%Y %H:%M:%S') # convert to datetime

delta_days = (datetime.now() - old_date_dt).days # use deltatime object
Delta_averaged = int((RealNetworth  - old_NW) / delta_days)

old_NW_1 = ws.acell("H" + str(current_row - 1)).value
old_NW_1 = int(old_NW_1.replace(",", "").replace(" ", ""))
Delta = int(RealNetworth  - old_NW_1)

L = [[current_date_num, NetworthTotal, StockTotal, CompanyTotal, FactionDonationTotal, VaultTotal, RealStocks, RealNetworth, NetworthKwartz/1000000000., NetworthKivou/1000000000., Cash, Delta, Delta_averaged]]
zone_to_be_filled = "A" + str(current_row) + ":M" + str(current_row)
#ws.update(zone_to_be_filled, L)
ws.update(range_name=zone_to_be_filled, values=L)
# ws.update_cell(1,2,current_row) (now done by MATCH fonction in spreadsheet)
ws.update_cell(2,2,nodeName)
