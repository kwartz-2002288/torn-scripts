import requests, gspread, string
from datetime import datetime, timezone
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

def old_value(ws, column, current_row, N):
    v = ws.acell(column + str(current_row - N)).value
    v = v.replace(",", "").replace(" ", "") # clean spreadsheet chain
    return int(v) # remove ',' in US spreadheet numbers

def delta_t(ws, current_row, N):
    d = ws.cell(current_row - N,1).value
    dt = datetime.strptime(d, '%d/%m/%Y %H:%M:%S') # convert to datetime
    return (datetime.now() - dt).days # use deltatime object

def delta_N(ws, new, column, current_row, N):
    return (new - old_value(ws, column, current_row, N))/delta_t(ws, current_row, N)

def updatePersonalStats(name):
    APIKEY = APIKey_dict[name]

# Get data from TORN in r (dictionnary)
    r=requests.get(f'https://api.torn.com/user/?selections=personalstats&key={APIKEY}').json()["personalstats"]

# Open the google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
    ws = gc.open_by_key(sheetKey).worksheet(f'Stats{name}')
# NEW version
    current_row = ws.cell(1,2).value # last row that has already been written
    current_row = int(current_row.replace(",", "").replace(" ", "")) #clean string and convert to int

    names_col = ["totalstats", "dexterity", "strength", "defense", "speed", "manuallabor", "intelligence", "endurance", "totalworkingstats"]
# Read stats names in sheet range 2, columns 3 to 9
# and read their values in torn data r then stock them in L_stats
    L_stats = [r[name_col] for name_col in names_col]
    # print(L_stats)

    # Compute evolutions on averaged rows
    new_total_stats = r["totalstats"]
    new_total_job = r["totalworkingstats"]
    current_row += 1
    date_now = datetime.now(timezone.utc)
    current_date_str = date_now.strftime("%d/%m/%Y %H:%M:%S")
    current_date_num = readKeysLib.python_date_to_excel_number(date_now)

    old_total_1 = old_value(ws, "B", current_row, 1)
    old_total_job_1 = old_value(ws, "M", current_row, 1)

    delta_1 = new_total_stats - old_total_1
    delta_job_1 = new_total_job - old_total_job_1
    delta_10 = delta_N(ws, new_total_stats, "B", current_row, 10)
    delta_365 = delta_N(ws, new_total_stats, "B", current_row, 365)
    delta_job_50 = delta_N(ws, new_total_job, "M", current_row, 365)
    # print(delta_1, delta_10, delta_365)
    # print(delta_job_1, delta_job_50)
    L_zone = [current_date_num] + L_stats[0:5] \
            + [delta_1, delta_10, delta_365/1000000] \
            + L_stats[5:9] + [delta_job_1, delta_job_50]
    zone_to_be_filled = "A" + str(current_row) + ":O" + str(current_row)
    ws.update(zone_to_be_filled, [L_zone])
    ws.update_cell(2,1,'Updated by ' + nodeName)
    return new_total_stats

L = []
for name in ('Kwartz','Kivou','Quatuor'):
    L.append(updatePersonalStats(name))
delta = L[0] - L[1]
ws = gc.open_by_key(sheetKey).worksheet('StatsKwartz')
current_row = ws.cell(1,2).value # last row that has already been written
current_row = int(current_row.replace(",", "").replace(" ", "")) #clean string and convert to int
ws.update('P'+ str(current_row), delta)
