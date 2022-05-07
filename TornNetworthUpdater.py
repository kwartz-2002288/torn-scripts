import requests, gspread, string, datetime, json, pprint
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

pp = pprint.PrettyPrinter(indent=4)
# API eys, sheet keys and lent stocks are saved in files in an external repertory see the readKeysLib module
APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
repertory = sheetKey_dict['rep']
lentStock_dict = readKeysLib.getLentStocks()

# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile = repertory + sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)

def getFactionDonation( APIKey=''):
# https://api.torn.com/faction/?selections=donations&key=Bge2YspVfryGBRM4
# structure  {"donations":{"2169463":{"name":"PapaAndreas","money_balance":0,"points_balance":0},"2198942":{"name":"nyudhfcue","money_balance":10000000,"points_balance":0}}}
    try:
        rb = requests.get(f'https://api.torn.com/user/?selections=basic&key={APIKey}' ).json()
        r = requests.get(f'https://api.torn.com/faction/?selections=donations&key={APIKey}' ).json()
        faction_cash = r['donations'][str(rb['player_id'])]['money_balance']
        if faction_cash < 0:
            faction_cash = 0
#        print(str(rb['player_id']),' *** ',cash)
        return faction_cash
    except KeyError as exception:
        print('Here is the KeyError :', exception)
        print('API key :', APIKey)
        return 0

def getNetworth( APIKey=''):
# STRUCTURE {"networth":{"pending":0,"wallet":300099,"bank":2270600000,"points":390267606,"cayman":0,"vault":935400000,"piggybank":null,"items":1072792534,"displaycase":88875999,"bazaar":7687,"properties":1087018000,"stockmarket":2004850585,"auctionhouse":0,"company":103827062,"bookie":null,"loan":0,"unpaidfees":0,"total":7953939572,"parsetime":0.06005597114562988}}
        r=requests.get(f'https://api.torn.com/user/?selections=networth&key={APIKey}').json()
        return r['networth']['total'],r['networth']['stockmarket'],r['networth']['company'],r['networth']['vault']

# print("FactionDonation")
# for player_name in ['Kivou','Kwartz']:
#     print(getFactionDonation(APIKey_dict[player_name]))
# print("Dictionnaries")
# pp.pprint(APIKey_dict)
# pp.pprint(sheetKey_dict)
# pp.pprint(lentStock_dict)

###### COMPUTE AND WRITE EXACT STOCKS STATUS
sheetKey = sheetKey_dict['TornStats']
ws = gc.open_by_key(sheetKey).worksheet('Stocks')

# Write the date and update current_row # modif Manu

current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
ws.update_cell(1,2,current_date)

# clean the sheet
cell_list = ws.range('A4:F200')

for cell in cell_list:
    cell.value = ''

ws.update_cells(cell_list)

rs=requests.get('https://api.torn.com/torn/?selections=stocks&key={api}'.format(api=APIKey_dict['Kivou']) ).json()
#print(rs["stocks"])
#for ps,ss in rs["stocks"].items():
#    print(ps,ss["acronym"])

total_stocks = 0
# lin = 3
for player_name in ['Kivou','Kwartz']:
    col = 1
#    lin +=1; ws.update_cell(lin,col,player_name)
#    print(player_name)
    player_total = 0
    rp=requests.get('https://api.torn.com/user/?selections=stocks&key={api}'.format(api=APIKey_dict[player_name]) ).json()
    for p,s in rp["stocks"].items():
        stock_id = str(s["stock_id"])
        acronym = rs["stocks"][stock_id]["acronym"]
        n_shares = s["total_shares"]
        price = float(rs["stocks"][stock_id]["current_price"])
        stock_value = n_shares *  price
        # old test for circulating faction stocks
        # if not ((stock_id == "25" and n_shares == 1000000) or (stock_id == "2" and n_shares == 1500000) or (stock_id == "30" and n_shares == 9000000)):
        player_total += stock_value
#        print(stock_id,acronym,n_shares,stock_value)
            #lin +=1; col=1; ws.update_cell(lin,col,stock_id)
            #col +=1; ws.update_cell(lin,col,acronym)
            #col +=1; ws.update_cell(lin,col,n_shares)
            #col +=1; ws.update_cell(lin,col,price)
            #col +=1; ws.update_cell(lin,col,int(stock_value))
    total_stocks += player_total
#    col +=1; ws.update_cell(lin,col,int(player_total))
#print("TOTAL :",total_stocks)
ws.update_cell(1,4,int(total_stocks))
# Add lent stocks:
other_stocks = readKeysLib.getLentStocks()
#print(other_stocks)
total_lent = 0
for stock_id, player_list in other_stocks.items():
#    print("stock_id",stock_id)
#    print("player_list",player_list)
#    lin+=1; col=1; ws.update_cell(lin,col,player_name)
    acronym = rs["stocks"][stock_id]["acronym"]
    n_shares = rs["stocks"][stock_id]["benefit"]["requirement"]
    price = float(rs["stocks"][stock_id]["current_price"])
#        print(rs["stocks"][stock_id]["acronym"],n_shares,price)
    stock_value = n_shares *  price
    total_stocks += stock_value * len(player_list)
    total_lent += stock_value * len(player_list)
        #lin +=1; col=1; ws.update_cell(lin,col,stock_id)
        #col +=1; ws.update_cell(lin,col,acronym)
        #col +=1; ws.update_cell(lin,col,n_shares)
        #col +=1; ws.update_cell(lin,col,price)
        #col +=1; ws.update_cell(lin,col,int(stock_value))
#col += 1; ws.update_cell(lin,col,int(total_lent))
ws.update_cell(2,4,int(total_stocks))

FactionDonationTotal = getFactionDonation( APIKey_dict['Kivou'] ) + getFactionDonation( APIKey_dict['Kwartz'] )
NetworthKivou,StockKivou,CompanyKivou,VaultKivou = getNetworth( APIKey_dict['Kivou'] )
NetworthKwartz,StockKwartz,CompanyKwartz,VaultKwartz = getNetworth( APIKey_dict['Kwartz'] )
NetworthTotal = NetworthKivou + NetworthKwartz
StockTotal = StockKivou + StockKwartz
CompanyTotal = CompanyKivou + CompanyKwartz
VaultTotal = VaultKivou + VaultKwartz

NetworthNet = NetworthTotal + FactionDonationTotal - StockTotal
Real_Networth = NetworthNet + total_stocks
#print(Real_Networth)
### ADD Oil Rig Participation:
Real_Networth += 5.763E9

#TotalArgozdoc = getArgozdocMoney( sheetKey_dict['ArgozVault'] )

# Open a google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
# Open Tornstats sheet

ws = gc.open_by_key(sheetKey).worksheet('NW')
current_row = int(ws.cell(1,2).value) + 1 # row where we will write new data
current_date = datetime.datetime.now().strftime("%d/%m/%Y")
ws.update_cell(current_row,1,current_date)
ws.update_cell(current_row,2,NetworthTotal)
ws.update_cell(current_row,3,StockTotal)
ws.update_cell(current_row,4,CompanyTotal)
ws.update_cell(current_row,5,FactionDonationTotal)
ws.update_cell(current_row,6,VaultTotal)
ws.update_cell(current_row,7,int(total_stocks))
ws.update_cell(current_row,8,int(Real_Networth))
ws.update_cell(current_row,9,NetworthKwartz/1000000000.)
ws.update_cell(current_row,10,NetworthKivou/1000000000.)
ws.update_cell( 1,2,current_row)
ws.update_cell( 2,2,nodeName)
