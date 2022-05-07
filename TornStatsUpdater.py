import requests, gspread, string, datetime
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

# APIKeys and sheetKeys are saved in files in an external repertory see the module readKeysLib
APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
repertory = sheetKey_dict['rep']
# print(f"APIKey_dict {APIKey_dict}")
# print(f"sheetKey_dict {sheetKey_dict}")
# print(f"repertory {repertory}")

# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile=repertory+sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)
sheetKey = sheetKey_dict['TornStats']

def updatePersonalStats( name , gc, sheetKey, APIKey_dict ):
    APIKEY = APIKey_dict[name]

# Get data from TORN in r (dictionnary)
    r=requests.get('https://api.torn.com/user/?selections=battlestats,workstats&key={api}'.format( api=APIKEY ) ).json()

# Open the google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
    ws = gc.open_by_key(sheetKey).worksheet('Stats{}'.format( name ))

# Read stats names in sheet range 2, columns 3 to 9
# and read their values in torn data r then stock them in L_stats
    L_stats=[]
    for i in range(3,10):
        name_col = ws.cell(2,i).value
        if isinstance(r[name_col],str):
            L_stats.append(float(r[name_col].replace(',','')))
        else:
            L_stats.append(float(r[name_col]))
    old_row = int(ws.cell(1,2).value.replace(' ',''))
    current_row = old_row +1 # row where we will write new data

# Update the google sheet
    for i in range(len(L_stats)):
        ws.update_cell(current_row,i+3,int(L_stats[i]))
# Sum the stats and update
    tot_stats=0
    for i in range(4):
        tot_stats+=L_stats[i]
    ws.update_cell(current_row,2,int(tot_stats))
# Calculate and update daily stat increment
        #if (current_row > 3) :
                #previous_tot_stats=int(ws.cell(current_row-1,2).value)
                #increment_averaged=int((tot_stats-previous_tot_stats))
                #ws.update_cell( current_row,11,increment_averaged)
# Calculate and update daily stat increment averaged on nd days
        #nd = 7
        #if (current_row-nd > 2) :
                #previous_tot_stats=int(ws.cell(current_row-nd,2).value)
                #increment_averaged=int((tot_stats-previous_tot_stats)/nd)
                #ws.update_cell( current_row,10,increment_averaged)
# Write the date and update current_row # modif Manu
        # current_date = ws.cell(1,4).value
    current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ws.update_cell( current_row,1,current_date)
    ws.update_cell( 1,2,current_row)
    ws.update_cell( 2,1,"updated by " + nodeName)
#        print('update done: new current row =',current_row)
    return

for name in ('Kwartz','Kivou','Quatuor'):
    updatePersonalStats( name , gc, sheetKey, APIKey_dict )
