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

def updateRehab(name, gc, sheetKey, APIKey_dict):
        APIKEY = APIKey_dict[name]
#        print ("updating {}'s Drugs History ({})".format( EXT, APIKEY ))
# Get data from TORN in r (dictionnary)
        r=requests.get('https://api.torn.com/user/?selections=personalstats&key={api}'.format(api=APIKEY ) ).json()
        x=requests.get('https://api.torn.com/torn/?selections=items&key={api}'.format(api=APIKEY ) ).json()
        
        new_xantaken=r['personalstats']['xantaken']
        new_exttaken=r['personalstats']['exttaken']

        xan_market_value=x['items']['206']['market_value']
        ecs_market_value=x['items']['197']['market_value']
        
# Open the google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
        ws = gc.open_by_key(sheetKey).worksheet('Drugs{}'.format( name ))

# Read current_row and old_xantaken in current_row
        current_row = int(ws.cell(1,2).value)
        old_xantaken = int(ws.cell(current_row,2).value)
        old_exttaken = int(ws.cell(current_row,3).value)

# Update the sheet only if xantaken has changed
        if new_xantaken!=old_xantaken or new_exttaken!=old_exttaken:
                current_row+=1
                ws.update_cell(1,2,current_row)
                current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                ws.update_cell(current_row,1,current_date)
                ws.update_cell(current_row,2,new_xantaken)
                ws.update_cell(current_row,3,new_exttaken)
                if new_xantaken!=old_xantaken:
                        ws.update_cell(current_row,4,xan_market_value)
                else:
                        ws.update_cell(current_row,4,ecs_market_value)
#                print('update done: new current row =',current_row)   
        return

for name in ('Kwartz','Kivou'):
    updateRehab( name , gc, sheetKey, APIKey_dict)

