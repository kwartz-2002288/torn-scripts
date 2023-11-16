import requests, gspread, string, datetime
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib
import csv

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

company = requests.get(f"https://api.torn.com/company/?selections=employees&key={APIKEY}").json()

employees = [["id","name","position","days_in_company","merits","working_stats","intelligence",
            "endurance","manual_labor","stats_sum","wage","addiction","settled_in",
            "dir_educ",
            "effectiveness_total"]]

for employee_id, employee in company["company_employees"].items():
    # employee
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

    # working stats
    stats = [employee[k] for k in ["intelligence", "endurance", "manual_labor"]]
    stats.sort(reverse=True)
    stats_sum = stats[0] + stats[1]/2

    employees.append([
        employee_id,
        name,
        position,
        days_in_company,
        merits,
        working_stats,
        employee["intelligence"],
        employee["endurance"],
        employee["manual_labor"],
        stats_sum,
        wage,
        addiction,
        settled_in,
        director_education,
        effectiveness_total])

current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

ws = gc.open_by_key(sheetKey).worksheet('employees_raw')
ws.update("A1:Z51",employees)
ws2 = gc.open_by_key(sheetKey2).worksheet('employees_raw')
ws2.update("A1:Z51",employees)

ws = gc.open_by_key(sheetKey).worksheet('wages')
ws2 = gc.open_by_key(sheetKey2).worksheet('wages')

for w in [ws, ws2]:
    w.update_cell(1, 1, "Updated by " + nodeName)
    w.update_cell(1, 3, current_date)
