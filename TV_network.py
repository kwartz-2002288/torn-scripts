import requests, gspread, string
from datetime import datetime, timezone
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib
import csv

# Set_up
APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
repertory=sheetKey_dict['rep']
APIKEY = APIKey_dict["Kwartz"]

# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile = repertory + sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)
sheetKey = sheetKey_dict['NubTV']
sheetKey2  = sheetKey_dict['WagesNubTV']

# call API
company = requests.get(f"https://api.torn.com/company/?selections=employees&key={APIKEY}").json()

now_date = datetime.now(timezone.utc)
current_date = now_date.strftime("%d/%m/%Y %H:%M:%S")

# parsing data
employees = []
for employee_id, employee in company["company_employees"].items():
    # employee data
    name = employee["name"]
    position = employee["position"]
    wage = employee["wage"]
    days_in_company = employee["days_in_company"]
    working_stats = employee["effectiveness"].get("working_stats", 0)
    merits = employee["effectiveness"].get("merits", 0)
    addiction = employee["effectiveness"].get("addiction", 0)
    settled_in = employee["effectiveness"].get("settled_in", 0)
    director_education = employee["effectiveness"].get("director_education", 0)
    effectiveness_total = employee["effectiveness"].get("total", 0)

    # afk analysis
    timestamp = employee["last_action"]["timestamp"]
    employee_date = datetime.fromtimestamp(timestamp, timezone.utc)
    afk_duration = now_date - employee_date
    afk_days = afk_duration.days
    afk_hours, remainder = divmod(afk_duration.seconds, 3600)

    # working stats combo analysis
    stats = [employee[k] for k in ["intelligence", "endurance", "manual_labor"]]
    stats.sort(reverse=True)
    stats_combo = stats[0] + stats[1]/2
    INT, END, MAN = employee["intelligence"], employee["endurance"], employee["manual_labor"]
    employees.append([
        employee_id, name, position,
        days_in_company, merits, working_stats,
        INT, END, MAN,
        stats_combo, wage, addiction,
        settled_in, director_education, effectiveness_total,
        afk_days, afk_hours])

employees_header = [
        "id","name","position",
        "days_in_company","merits","working_stats",
        "INT", "END", "MAN",
        "stats_combo","wage","addiction",
        "settled_in", "dir_educ", "eff_total",
        "afk_days", "afk_hours"]

#sorting employee list
criterion = "position"
sort_index = employees_header.index(criterion)
employees.sort(key=lambda x: x[sort_index], reverse=False)
employees = [employees_header] + employees

ws = gc.open_by_key(sheetKey).worksheet('employees_raw')
ws.clear()
ws.update("A1:Z51",employees)
ws2 = gc.open_by_key(sheetKey2).worksheet('employees_raw')
ws2.clear()
ws2.update("A1:Z51",employees)

ws = gc.open_by_key(sheetKey).worksheet('wages')
ws2 = gc.open_by_key(sheetKey2).worksheet('wages')

for w in [ws, ws2]:
    w.update_cell(1, 1, "Updated by " + nodeName)
    w.update_cell(1, 3, current_date + " TCT")
