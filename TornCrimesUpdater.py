import requests, gspread, string, datetime
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
    r=requests.get('https://api.torn.com/user/?selections=crimes&key={api}'.format(api=APIKEY ) ).json()
    p=requests.get('https://api.torn.com/user/?selections=personalstats&key={api}'.format(api=APIKEY ) ).json()

# Open the specific worksheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
    ws = gc.open_by_key(sheetKey).worksheet('Crimes{}'.format( name ))

# Read crimes names in sheet range 3, columns 2 to 10
# and read their values in torn data r then stock them in L_crimes
    L_crimes=[ ]
    for i in range(2,11):
        name_col = ws.cell(3,i).value
        L_crimes.append(r['criminalrecord'][name_col])
#    print(L_crimes)
    current_row = int(ws.cell(1,2).value) # last row that has already been written
    old_total = int(ws.cell(current_row,10).value)
    new_total = r['criminalrecord']['total']
# Update the google sheet crimes only if something has changed
    if new_total!=old_total:
        current_row+=1
# Update current row, crimes numbers and jailed
        ws.update_cell(1,2,current_row)
        ws.update_cell(2,1,'Updated by ' + nodeName)
        for i in range(len(L_crimes)):
            ws.update_cell(current_row,i+2,int(L_crimes[i]))
        ij = 11
        ws.update_cell(current_row,ij,int(p['personalstats']['jailed']))
        ws.update_cell(current_row,ij+1,int(p['personalstats']['peoplebusted']))
        ws.update_cell(current_row,ij+2,int(p['personalstats']['failedbusts']))
        ws.update_cell(current_row,ij+3,int(p['personalstats']['peoplebought']))
        ws.update_cell(current_row,ij+4,int(p['personalstats']['peopleboughtspent']/1000))
# Write the date
        current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        ws.update_cell(current_row,1,current_date)

for name in ('Kwartz','Kivou'):
    updateCrimes( name , gc, sheetKey, APIKey_dict)
