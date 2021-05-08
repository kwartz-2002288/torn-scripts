import requests, gspread, string, datetime
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

# constant used to translate POSIX date to gspread date (2 days pb!)
originStr = '1899-12-30 00:00:00'
origin = datetime.datetime.strptime(originStr,'%Y-%m-%d %H:%M:%S')

# APIKeys and sheetKeys are saved in files in an external repertory see the module readKeysLib
APIKey_dict,sheetKey_dict = readKeysLib.getDicts()
repertory=sheetKey_dict['rep']

# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile=repertory+sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)
sheetKey = sheetKey_dict['TornStats']

def updatePersonalStats( name , gc, sheetKey, APIKey_dict ):
    APIKey = APIKey_dict[name]
# Get data from TORN in r (dictionnary)
    r=requests.get('https://api.torn.com/user/?selections=battlestats,workstats&key={api}'.format(api=APIKey)).json()
# Open the google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
    ws = gc.open_by_key(sheetKey).worksheet('Stats{n}'.format(n=name))

    currentDateTime = datetime.datetime.now()
    currentDateGspread = (currentDateTime - origin).total_seconds()/24/3600 # date (days number format gspread)
    currentRow = int(ws.cell(1,2).value.replace("\u202f",""))

# Read stats names in sheet range 2, columns 2 to 9
# and read their values in torn data r then stock them in L_stats
    L_stats=[]
    for i in range(2,10):
        name_col = ws.cell(2,i).value
        L_stats.append(r[name_col])
    currentTotStats = L_stats[0]
# Calculate and update last stat increment
    previousTotStats = int(ws.cell(currentRow,2).value.replace("\u202f",""))
    previousDateGspreadStr = ws.cell(currentRow,1).value
    previousDateTime = datetime.datetime.strptime(previousDateGspreadStr,"%d/%m/%Y %H:%M:%S") # convert to datetime
    previousDateGspread = (previousDateTime - origin).total_seconds()/24/3600 # gs date in days
    dailyIncrement = (currentTotStats - previousTotStats) / (currentDateGspread - previousDateGspread)
# Calculate and update daily stat increment averaged on nd days
    nd = 30
    oldTotStats = int(ws.cell(currentRow -nd +1, 2).value.replace("\u202f",""))
    oldDateGspreadStr = ws.cell(currentRow -nd +1,1).value
    oldDateTime = datetime.datetime.strptime(oldDateGspreadStr,"%d/%m/%Y %H:%M:%S")
    oldDateGspread = (oldDateTime - origin).total_seconds()/24/3600 # gs date in days
    averagedIncrement = (currentTotStats - oldTotStats) / (currentDateGspread - oldDateGspread)
# job Stats
    totalJobStats = sum(L_stats[5:8])
    previousJobStats = int(ws.cell(currentRow,12).value.replace("\u202f",""))
    oldJobStats = int(ws.cell(currentRow -nd +1,12).value.replace("\u202f",""))
    jobStatsDelta = (totalJobStats - previousJobStats)
    jobStatsAveragedIncrement = (totalJobStats - oldJobStats) / (currentDateGspread - oldDateGspread)

# Update
    newRow = [currentDateGspread] + L_stats + [averagedIncrement,dailyIncrement,totalJobStats,jobStatsDelta,jobStatsAveragedIncrement]
    ws.update('A'+str(currentRow+1),[newRow])
    ws.update_cell(1,2,currentRow+1)

    return

for name in ('Kwartz','Kivou','Quatuor'):
    updatePersonalStats( name , gc, sheetKey, APIKey_dict )
#updatePersonalStats( 'Kwartz' , gc, sheetKey, APIKey_dict )
