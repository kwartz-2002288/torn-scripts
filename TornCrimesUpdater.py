import requests, gspread, string
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

# APIKeys and sheetKeys are saved in files in an external repertory see the module readKeysLib
APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
repertory=sheetKey_dict['rep']

# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile=repertory+sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)

# Open the google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
sheetKey = sheetKey_dict['TornStats']

def updateCrimes(name, gc, sheetKey, APIKey_dict):
    APIKEY = APIKey_dict[name]
# Get data from TORN in r (dictionnary)
    r=requests.get(f'https://api.torn.com/user/?selections=crimes&key={APIKEY}').json()
    p=requests.get(f'https://api.torn.com/user/?selections=personalstats&key={APIKEY}').json()

# Open the specific worksheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
    ws = gc.open_by_key(sheetKey).worksheet(f'Crimes{name}')

# Read crimes names in sheet range 3, columns 2 to 10
# and read their values in torn data r then stock them in L_crimes
    current_row = ws.cell(1,2).value # last row that has already been written
    current_row = int(''.join(current_row.split()))
    names_col = ws.row_values(3)[1:10]
    L_crimes=[r['criminalrecord'][name_col] for name_col in names_col]

    old_total = ws.cell(current_row,10).value
    old_total = int(''.join(old_total.split()))
    new_total = r['criminalrecord']['total']

# Update the google sheet crimes only if something has changed

    if new_total != old_total:
        for n in ['jailed', 'peoplebusted', 'failedbusts', 'peoplebought', 'peopleboughtspent']:
            L_crimes.append(int(p['personalstats'][n]))
        L_crimes[-1]//=1000

        # Compute evolutions on N_average rows
        current_row += 1
        current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        N_average = 21

        old_busts = ws.acell("L" + str(current_row - N_average)).value
        old_busts = int(''.join(old_busts.split())) # remove spaces
        new_busts = int(p['personalstats']['peoplebusted'])

        old_crimes = ws.acell("J" + str(current_row - N_average)).value
        old_crimes = int(''.join(old_crimes.split()))

        old_date = ws.cell(str(current_row - N_average),1).value
        old_date_dt = datetime.strptime(old_date, '%d/%m/%Y %H:%M:%S') # convert to datetime
        delta_days = (datetime.now() - old_date_dt).days # use deltatime object

        busts_per_day = (new_busts - old_busts) / delta_days
        crimes_per_day = (new_total - old_crimes) / delta_days
        L_crimes += [busts_per_day, crimes_per_day]
        zone_to_be_filled = "B" + str(current_row) + ":Q" + str(current_row)
        ws.update(zone_to_be_filled, [L_crimes])
        ws.update_cell(current_row,1,current_date)
        ws.update_cell(1,2,current_row)
        ws.update_cell(2,1,'Updated by ' + nodeName)


for name in ('Kwartz','Kivou'):
    updateCrimes( name , gc, sheetKey, APIKey_dict)
