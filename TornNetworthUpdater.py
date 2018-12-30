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

def getNetworthTotal( APIKEY=''):
# STRUCTURE {'networth': {'cayman': 0, 'piggybank': None, 'points': 124727894, 'parsetime': 0.046871185302734375, 'properties': 1087018000, 'stockmarket': 1696621715, 'bazaar': 3292880, 'pending': 0, 'vault': 294600000, 'auctionhouse': 0, 'loan': 0, 'bank': 0, 'items': 654838365, 'bookie': None, 'company': 0, 'displaycase': None, 'total': 3861167646, 'unpaidfees': 0, 'wallet': 68792}}
        r=requests.get('https://api.torn.com/user/?selections=networth&key={api}'.format(api=APIKEY ) ).json()
        return (r['networth']['total']-r['networth']['stockmarket'])
    
def getCompanyBank(APIKEY='',ID=''):
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

def getArgozdocMoney( sheetKey ):
    # Open Argozdoc's Vault sheet
    ws = gc.open_by_key(sheetKey).worksheet('Vault')
    return int(ws.cell(2,5).value)

TotalCompany = getCompanyBank( APIKEY=APIKey_dict['Kivou'],ID=53416 )
TotalKivou = getNetworthTotal( APIKey_dict['Kivou'] )
TotalKwartz = getNetworthTotal( APIKey_dict['Kwartz'] )
TotalArgozdoc=getArgozdocMoney( sheetKey_dict['ArgozVault'] )

Total = TotalKivou + TotalKwartz - TotalArgozdoc

# Open a google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
# Open Tornstats sheet

sheetKey = sheetKey_dict['TornStats']
ws = gc.open_by_key(sheetKey).worksheet('Networth')
current_row = int(ws.cell(1,2).value) + 1 # row where we will write new data

# Write the date and update current_row # modif Manu

current_date = datetime.datetime.now().strftime("%d/%m/%Y")
ws.update_cell( current_row,1,current_date)
ws.update_cell(current_row,2,TotalKivou)
ws.update_cell(current_row,3,TotalKwartz)
ws.update_cell(current_row,4,TotalCompany)
ws.update_cell(current_row,5,TotalArgozdoc)
ws.update_cell(current_row,6,Total)
ws.update_cell( 1,2,current_row)

