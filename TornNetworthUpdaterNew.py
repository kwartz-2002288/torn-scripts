import requests, gspread, string, datetime
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

# APIKeys and sheetKeys are saved in files in an external repertory see the readKeysLib module
APIKey_dict,sheetKey_dict = readKeysLib.getDicts()
repertory=sheetKey_dict['rep']

# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile=repertory+sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)

def getFactionDonation( APIKEY=''):
# https://api.torn.com/faction/?selections=donations&key=
# structure  {"donations":{"2169463":{"name":"PapaAndreas","money_balance":0,"points_balance":0},"2198942":{"name":"nyudhfcue","money_balance":10000000,"points_balance":0}}}

    rb=requests.get('https://api.torn.com/user/?selections=basic&key={api}'.format(api=APIKEY ) ).json()
    r=requests.get('https://api.torn.com/faction/?selections=donations&key={api}'.format(api=APIKEY ) ).json()
    return r['donations'][str(rb['player_id'])]['money_balance']

def getNetworth( APIKEY=''):
# STRUCTURE {'networth': {'cayman': 0, 'piggybank': None, 'points': 124727894, 'parsetime': 0.046871185302734375, 'properties': 1087018000, 'stockmarket': 1696621715, 'bazaar': 3292880, 'pending': 0, 'vault': 294600000, 'auctionhouse': 0, 'loan': 0, 'bank': 0, 'items': 654838365, 'bookie': None, 'company': 0, 'displaycase': None, 'total': 3861167646, 'unpaidfees': 0, 'wallet': 68792}}

        r=requests.get('https://api.torn.com/user/?selections=networth&key={api}'.format(api=APIKEY ) ).json()
        return r['networth']['total'],r['networth']['stockmarket'],r['networth']['company']
    
def getCompanyBank(APIKEY='',ID=''): # no more used, see getNetworth above
# STRUCTURE {
	#"company_detailed": {
		#"ID": 53416,
		#"company_bank": 11595336,
		#"popularity": 73,
		#"efficiency": 100,
		#"environment": 95,
		#"trains_available": 0,
		#"advertising_budget": 500000,
		#"upgrades": {
			#"company_size": 10,
			#"staffroom_size": "Colossal staff room",
			#"storage_size": "No storage room",
			#"storage_space": 10000
		#}
	#}
#}
        r = requests.get('https://api.torn.com/company/{id}?selections=detailed&key={api}'.format(api=APIKEY,id=ID ) ).json()
        return r["company_detailed"]["company_bank"]

#def getArgozdocMoney( sheetKey ): # In case we play the bank for another player
    ## Open Argozdoc's Vault sheet
    #ws = gc.open_by_key(sheetKey).worksheet('Vault')
    #return int(ws.cell(2,5).value)

FactionDonationTotal = getFactionDonation( APIKey_dict['Kivou'] ) + getFactionDonation( APIKey_dict['Kwartz'] )
NetworthKivou,StockKivou,CompanyKivou = getNetworth( APIKey_dict['Kivou'] )
NetworthKwartz,StockKwartz,CompanyKwartz = getNetworth( APIKey_dict['Kwartz'] )
NetworthTotal = NetworthKivou + NetworthKwartz
StockTotal = StockKivou + StockKwartz
CompanyTotal = CompanyKivou + CompanyKwartz
NetworthNet = NetworthTotal + FactionDonationTotal - StockTotal
#TotalArgozdoc = getArgozdocMoney( sheetKey_dict['ArgozVault'] )

# Open a google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
# Open Tornstats sheet

sheetKey = sheetKey_dict['TornStats']
ws = gc.open_by_key(sheetKey).worksheet('NW')
current_row = int(ws.cell(1,2).value) + 1 # row where we will write new data

# Write the date and update current_row # modif Manu

current_date = datetime.datetime.now().strftime("%d/%m/%Y")
ws.update_cell(current_row,1,current_date)
ws.update_cell(current_row,2,NetworthTotal)
ws.update_cell(current_row,3,StockTotal)
ws.update_cell(current_row,4,CompanyTotal)
ws.update_cell(current_row,5,FactionDonationTotal)
ws.update_cell(current_row,6,NetworthNet)
ws.update_cell( 1,2,current_row)

