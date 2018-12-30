import requests, gspread, string, datetime
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

def getInfos( APIKEY='', EXT='' ): # Get data from TORN in r (dictionnary)
    r=requests.get('https://api.torn.com/user/?selections=education,stocks&key={api}'.format(api=APIKEY ) ).json()
    t_educ_seconds=r['education_timeleft']
    user_stocks=r['stocks']
    return t_educ_seconds, user_stocks

# APIKeys and sheetKeys are saved in files in an external repertory see the module readKeysLib
APIKey_dict,sheetKey_dict = readKeysLib.getDicts()
repertory=sheetKey_dict['rep']

# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile=repertory+sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)

# Open the "time_left" google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
sheetKey = sheetKey_dict['WSSB']
ws = gc.open_by_key(sheetKey).worksheet('time_left')

# search for players with a WSSB stock
users_list = [ ]
for i,name in enumerate(APIKey_dict):  
    API_k = APIKey_dict[name]
    t_educ,user_stocks = getInfos( APIKEY=API_k, EXT=name )
    ws.update_cell(i+2,1,name)
    ws.update_cell(i+2,2,t_educ)
    if user_stocks is not None:
        for k in user_stocks:
            if user_stocks[k]['stock_id'] == 25:
                users_list.append(name)
                
# Open the WSSB sheet
ws = gc.open_by_key(sheetKey).worksheet('WSSB')
# Write the date
current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
ws.update_cell( 1,1,"Last update : " + current_date)
# Cleaning writing zone (in case several players have had the stock previously!)
for i in range(3):
    ws.update_cell(i+3,2,'')
# Writing 
if len(users_list) > 0 :
    for i,name in enumerate(users_list):
        if i<3:
            ws.update_cell(i+3,2,name)
else:
    ws.update_cell(3,2,'Nobody has WWSB stock !')
    

    


