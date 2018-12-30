import requests, gspread, string, datetime
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

# APIKeys and sheetKeys are saved in files in an external repertory see the module readKeysLib
APIKey_dict,sheetKey_dict = readKeysLib.getDicts()
repertory=sheetKey_dict['rep']

# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile=repertory+sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)

sheetKey = sheetKey_dict['TornStats']

def updateSpecialGym ( name , gc, sheetKey, APIKey_dict ):
        APIKEY = APIKey_dict[name]

# Get data from TORN in r (dictionnary)
        r=requests.get('https://api.torn.com/user/?selections=battlestats&key={api}'.format( api=APIKEY ) ).json()

# Open the google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
        ws = gc.open_by_key(sheetKey).worksheet('Gym{}'.format( name ))

# Get stats, convert in millions and update sheet
        therow = 1
        thecol = 1
        thename=['dexterity','defense','speed','strength']
        for i in range(0,4):
                thecol+=1
                stat_int=int(float(r[thename[i]]))
                ws.update_cell(therow,thecol,stat_int)

# Write the date
        current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        ws.update_cell( 2,2,current_date)
        return

for name in ('Kwartz','Kivou'):
    updateSpecialGym( name , gc, sheetKey, APIKey_dict)




