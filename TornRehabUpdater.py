import requests, gspread, string, datetime
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib
# COUCOU
# APIKeys and sheetKeys are saved in files in an external repertory see the module readKeysLib
APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
repertory = sheetKey_dict['rep']

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
        new_lsdtaken=r['personalstats']['lsdtaken']
        new_opitaken=r['personalstats']['opitaken']
        new_pcptaken=r['personalstats']['pcptaken']
        new_victaken=r['personalstats']['victaken']

        xan_market_value=x['items']['206']['market_value']
        lsd_market_value=x['items']['199']['market_value']
        opi_market_value=x['items']['200']['market_value']
        pcp_market_value=x['items']['201']['market_value']
        vic_market_value=x['items']['205']['market_value']

# Open the google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
        ws = gc.open_by_key(sheetKey).worksheet('Drugs{}'.format( name ))

# Read current_row and old_xantaken in current_row
        current_row = int(ws.cell(1,2).value)
        old_xantaken = int(ws.cell(current_row,2).value)
        old_lsdtaken = int(ws.cell(current_row,3).value)
        old_opitaken = int(ws.cell(current_row,4).value)
        old_pcptaken = int(ws.cell(current_row,5).value)
        old_victaken = int(ws.cell(current_row,6).value)

# Update the sheet only if xantaken has changed
        if new_xantaken!=old_xantaken or new_lsdtaken!=old_lsdtaken or new_opitaken!=old_opitaken or new_pcptaken!=old_pcptaken or new_victaken!=old_victaken:
                current_row+=1
                ws.update_cell(1,2,current_row)
                ws.update_cell(2,1,"updated by " + nodeName)
                current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                ws.update_cell(current_row,1,current_date)
                ws.update_cell(current_row,2,new_xantaken)
                ws.update_cell(current_row,3,new_lsdtaken)
                ws.update_cell(current_row,4,new_opitaken)
                ws.update_cell(current_row,5,new_pcptaken)
                ws.update_cell(current_row,6,new_victaken)
                if new_xantaken!=old_xantaken:
                        ws.update_cell(current_row,7,xan_market_value)
                elif new_lsdtaken!=old_lsdtaken:
                        ws.update_cell(current_row,7,lsd_market_value)
                elif new_opitaken!=old_opitaken:
                        ws.update_cell(current_row,7,opi_market_value)
                elif new_pcptaken!=old_pcptaken:
                        ws.update_cell(current_row,7,pcp_market_value)
                elif new_victaken!=old_victaken:
                        ws.update_cell(current_row,7,vic_market_value)
        return


for name in ('Kwartz','Kivou'):
   updateRehab( name , gc, sheetKey, APIKey_dict)
