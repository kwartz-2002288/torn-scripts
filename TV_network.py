import requests, gspread, string
from datetime import datetime, timezone
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

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
company_employees = requests.get(f"https://api.torn.com/company/?selections=employees&key={APIKEY}").json()["company_employees"]
company_detailed = requests.get(f"https://api.torn.com/company/?selections=detailed&key={APIKEY}").json()["company_detailed"]
company_profile = requests.get(f"https://api.torn.com/company/?selections=profile&key={APIKEY}").json()["company"]


now_date = datetime.now(timezone.utc)
current_date_str = now_date.strftime("%d/%m/%Y %H:%M:%S")
current_date_num = readKeysLib.python_date_to_excel_number(now_date)

# parsing company data
company_funds = company_detailed["company_funds"]
popularity = company_detailed["popularity"]
efficiency = company_detailed["efficiency"]
environment = company_detailed["environment"]
advertising_budget = company_detailed["advertising_budget"]
value = company_detailed["value"]
company_name = company_profile["name"]
rating = company_profile["rating"]
daily_income = company_profile["daily_income"]
daily_customers = company_profile["daily_customers"]
weekly_income = company_profile["weekly_income"]
weekly_customers = company_profile["weekly_customers"]

# print("company_funds, popularity ", company_funds, popularity)
# print("rating, daily_income", rating, daily_income)

# parsing employee data
employees = []
director_wage = 4_000_000
kivou_wage = 1_100_000
SYS_stock_price = 1_850_000_000
total_investment = 27_500_000_000 + SYS_stock_price
KK_investment = 17_500_000_000 + SYS_stock_price
wages_total = director_wage
working_stats_eff_total = 0
settle_total = 0
EE_total = 0
director_education_total = 0
addiction_total = 0
inactivity_total = 0
company_effectiveness_total = 0

for employee_id, employee in company_employees.items():
    # employee data
    name = employee["name"]
    position = employee["position"]
    wage = employee["wage"]
    wages_total += wage
    days_in_company = employee["days_in_company"]
    working_stats = employee["effectiveness"].get("working_stats", 0)
    working_stats_eff_total += working_stats
    merits = employee["effectiveness"].get("merits", 0)
    EE_total += merits
    addiction = employee["effectiveness"].get("addiction", 0)
    addiction_total += addiction
    settled_in = employee["effectiveness"].get("settled_in", 0)
    settle_total += settled_in
    director_education = employee["effectiveness"].get("director_education", 0)
    director_education_total += director_education
    effectiveness_total = employee["effectiveness"].get("total", 0)
    company_effectiveness_total += effectiveness_total
    inactivity = employee["effectiveness"].get("inactivity", 0)
    inactivity_total += inactivity

    # afk analysis
    timestamp = employee["last_action"]["timestamp"]
    employee_date = datetime.fromtimestamp(timestamp, timezone.utc)
    afk_duration = now_date - employee_date
    afk_days = afk_duration.days
    afk_hours, remainder = divmod(afk_duration.seconds, 3600)

    # working stats combo analysis
    stats = [employee[k] for k in ["intelligence", "endurance", "manual_labor"]]
    stats.sort(reverse=True)
    stats_combo = stats[0] + stats[1]
    INT, END, MAN = employee["intelligence"], employee["endurance"], employee["manual_labor"]
    employees.append([
        employee_id, name, position,
        days_in_company, merits, working_stats,
        INT, END, MAN,
        stats_combo, wage, addiction,
        settled_in, director_education, effectiveness_total,
        afk_days, afk_hours, inactivity])

employees_header = [
        "id","name","position",
        "days_in","merits","ws",
        "INT", "END", "MAN",
        "stats_combo","wage","addiction",
        "settled_in", "dir_educ", "eff_tot",
        "afk_d", "afk_h", "inactivity"]

#sorting employee list
criterion = "position"
sort_index = employees_header.index(criterion)
employees.sort(key=lambda x: x[sort_index], reverse=False)
employees = [employees_header] + employees

#writing in spreadsheet

ws = gc.open_by_key(sheetKey).worksheet('employees_raw')
ws.clear()
ws.update("A1:Z51",employees)
ws2 = gc.open_by_key(sheetKey2).worksheet('employees_raw')
ws2.clear()
ws2.update("A1:Z51",employees)

ws = gc.open_by_key(sheetKey).worksheet('wages')
ws2 = gc.open_by_key(sheetKey2).worksheet('wages')

for w in [ws, ws2]:
    w.update_cell(1, 1, "Updated by " + nodeName + " " + current_date_str + " TCT")
#    w.update_cell(1, 4, current_date_str + " TCT")

#evolution spreadsheet
daily_profit = daily_income - wages_total - advertising_budget
minimum_funds = 7 * (wages_total - director_wage + advertising_budget)
ROI = daily_profit * 365 / total_investment
ROI2 = ROI + (director_wage + kivou_wage) * 365 / KK_investment
company_effectiveness_max = (company_effectiveness_total -
                            inactivity_total - addiction_total)
efficiency_loss = (-inactivity_total-addiction_total)/company_effectiveness_max
L_zone = [current_date_num, company_name, rating, popularity, efficiency, environment,
    working_stats_eff_total, settle_total, EE_total, director_education_total,
    addiction_total, inactivity_total,
    company_effectiveness_total, company_effectiveness_max, efficiency_loss,
    weekly_customers, daily_customers, value/1000000000,
    company_funds/1000000, minimum_funds/1000000,
    weekly_income/1000000, daily_income/1000000,
    wages_total/1000000, advertising_budget/1000000,
    daily_profit/1000000, ROI, ROI2]

ws_evo = gc.open_by_key(sheetKey).worksheet('Evolution')
current_row = ws_evo.cell(1,3).value # last row that has already been written
current_row = 1 + int(''.join(current_row.split())) #clean string and convert to int
zone_to_be_filled = "A" + str(current_row) + ":ZZ" + str(current_row)
ws_evo.update(zone_to_be_filled, [L_zone])
