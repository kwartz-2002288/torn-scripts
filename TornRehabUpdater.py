import requests, gspread, string
from datetime import datetime, timezone
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

def convert_date_in_spreadsheet_number(date):
    # Convert a python date (typically utc datetime format) to a google sheet compatible number
    # Define the reference date for Google Sheets (December 30, 1899)
    reference_date = datetime(1899, 12, 30, tzinfo=timezone.utc)
    # Calculate the difference in days
    days_difference = (date - reference_date).days
    # Calculate the fraction of the day
    fraction_of_day = (date - datetime(date.year, date.month, date.day,
        tzinfo=timezone.utc)).total_seconds() / 86400.0  # 86400 seconds in a day
    # Calculate the total number
    date_number = days_difference + fraction_of_day
    return date_number

def updateRehab(name, gc, sheetKey, APIKey_dict):
        APIKEY = APIKey_dict[name]
#        print ("updating {}'s Drugs History ({})".format( EXT, APIKEY ))
# Get data from TORN in r (dictionnary)
        r=requests.get('https://api.torn.com/user/?selections=personalstats&key={api}'.format(api=APIKEY ) ).json()
        x=requests.get('https://api.torn.com/torn/?selections=items&key={api}'.format(api=APIKEY ) ).json()

        new_xantaken=r['personalstats']['xantaken']
        new_lsdtaken=r['personalstats']['lsdtaken']
        new_opitaken=r['personalstats']['opitaken']
        new_cantaken=r['personalstats']['cantaken']
        new_victaken=r['personalstats']['victaken']

        xan_market_value=x['items']['206']['market_value']
        lsd_market_value=x['items']['199']['market_value']
        opi_market_value=x['items']['200']['market_value']
        can_market_value=x['items']['196']['market_value']
        vic_market_value=x['items']['205']['market_value']

# Open the google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
        ws = gc.open_by_key(sheetKey).worksheet('Drugs{}'.format( name ))

# Read current_row and old_xantaken in current_row
        current_row = int(ws.cell(1,2).value)
        old_xantaken = int(ws.cell(current_row,2).value)
        old_lsdtaken = int(ws.cell(current_row,3).value)
        old_opitaken = int(ws.cell(current_row,4).value)
        old_cantaken = int(ws.cell(current_row,5).value)
        old_victaken = int(ws.cell(current_row,6).value)

# Update the sheet only if  a number has changed
        if new_xantaken!=old_xantaken or new_lsdtaken!=old_lsdtaken or new_opitaken!=old_opitaken or new_cantaken!=old_cantaken or new_victaken!=old_victaken:
                current_row+=1
#                ws.update_cell(1,2,current_row)   # Done in spreadsheet now !
                ws.update_cell(2,1,"updated by " + nodeName)
                date_now = datetime.now(timezone.utc)
                current_date_str = date_now.strftime("%d/%m/%Y %H:%M:%S")
                current_date_num = convert_date_in_spreadsheet_number(date_now)
                L = [current_date_num, new_xantaken, new_lsdtaken, new_opitaken,
                    new_cantaken, new_victaken, xan_market_value]
                zone_to_be_filled = "A" + str(current_row) + ":G" + str(current_row)
                # ws.update(zone_to_be_filled, [L])
                ws.update(range_name=zone_to_be_filled, values=[L])
                # ws.update_cell(current_row,1,current_date_num)
                # ws.update_cell(current_row,2,new_xantaken)
                # ws.update_cell(current_row,3,new_lsdtaken)
                # ws.update_cell(current_row,4,new_opitaken)
                # ws.update_cell(current_row,5,new_cantaken)
                # ws.update_cell(current_row,6,new_victaken)
                if new_lsdtaken!=old_lsdtaken:
                        ws.update_cell(current_row,7,lsd_market_value)
                elif new_opitaken!=old_opitaken:
                        ws.update_cell(current_row,7,opi_market_value)
                elif new_cantaken!=old_cantaken:
                        ws.update_cell(current_row,7,can_market_value)
                elif new_victaken!=old_victaken:
                        ws.update_cell(current_row,7,vic_market_value)
        return


for name in ('Kwartz','Kivou'):
   updateRehab( name , gc, sheetKey, APIKey_dict)
