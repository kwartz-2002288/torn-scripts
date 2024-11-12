import requests, string
from datetime import time, datetime, timezone, timedelta
import readKeysLib

# script execution start schedule
now_date = datetime.now(timezone.utc)
current_date_str = now_date.strftime("%d/%m/%Y %H:%M:%S")

# limits
trains_alert_limit = 10
hours_to_evaluation_limit = 24

# company evaluation schedule
evaluation_time = now_date.replace(hour=18, minute=0)

# delta hours from evaluation_time
delta_hours_to_evaluation = (evaluation_time - now_date).total_seconds() / 3600

# set_up
APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
repertory = sheetKey_dict['rep']
APIKEY = APIKey_dict["Kwartz"] # API key for torn

# Free mobile API user's informations and error codes
Free_user = APIKey_dict["Free_user"]
Free_APIKEY = APIKey_dict["Free_APIKEY"] # API key for free mobile SMS
Free_errors = {
    200: "SMS sent successfully.",
    400: "Missing parameter. One or more required parameters were not provided.",
    402: "Too many SMS sent in a short period. SMS sending is temporarily blocked.",
    403: "Incorrect credentials. The provided user ID/API key pair is invalid.",
    500: "Server error. A problem occurred on Free Mobile's server."
}

def send_SMS(message):
    url = f"https://smsapi.free-mobile.fr/sendmsg?user={Free_user}&pass={Free_APIKEY}&msg={message}"
    response = requests.get(url)
    check = Free_errors.get(response.status_code, "Unknown error")
    return check

# Get data from API
company_employees = requests.get(f"https://api.torn.com/company/?selections=employees&key={APIKEY}").json()["company_employees"]
company_detailed = requests.get(f"https://api.torn.com/company/?selections=detailed&key={APIKEY}").json()["company_detailed"]
company = requests.get(f"https://api.torn.com/company/?selections=profile&key={APIKEY}").json()["company"]


trains_available = company_detailed["trains_available"]
popularity = company_detailed["popularity"]

employees_hired = company["employees_hired"]
employees_capacity = company["employees_capacity"]
rating = company["rating"]

# Prepare Message
all_good = True
message = f"NNN {rating}* network company\n"

# Calcul de la valeur absolue et de l'orientation temporelle
before_after = "before" if delta_hours_to_evaluation > 0 else "after"
delta_hours_to_evaluation = abs(delta_hours_to_evaluation)

if delta_hours_to_evaluation > 1:
    message += f"{round(delta_hours_to_evaluation)} hrs {before_after} evaluation\n"
else:
    message += f"{round(delta_hours_to_evaluation * 60)} min {before_after} evaluation\n"

if employees_hired < employees_capacity:
    all_good = False
    message += f"ALERT! {employees_hired}/{employees_capacity} hired\n"

#if trains_available > 8 and test_time_slot(start_hour=12, start_minute=5, interval_minute=15):
if trains_available > trains_alert_limit:
    all_good = False
    message += f"ALERT! {trains_available} trains available\n"

activity_message = ""
good_activity = True

for employee_id, employee in company_employees.items():
    # employee informations
    name = employee["name"]
    position = employee["position"]
    wage = employee["wage"]
    merits = employee["effectiveness"].get("merits", 0)
    inactivity = employee["effectiveness"].get("inactivity", 0)
    # afk analysis
    timestamp = employee["last_action"]["timestamp"]
    employee_last_action_date = datetime.fromtimestamp(timestamp, timezone.utc)
    afk_duration = now_date - employee_last_action_date
    afk_days = afk_duration.days
    afk_hours = afk_duration.seconds / 3600
    afk_hours_at_evaluation = afk_days*24 + afk_hours + delta_hours_to_evaluation
    if afk_hours_at_evaluation > hours_to_evaluation_limit:
        good_activity = False
        afk_days_at_evaluation, afk_hours_remainder = divmod(afk_hours_at_evaluation, 24)
        activity_message += f"{name}: "
        if afk_days_at_evaluation > 0:
            activity_message += f"{afk_days_at_evaluation}d "
        activity_message += f"{afk_hours_remainder:.1f}h\n"

if not good_activity:
    activity_message = "Employee inactivity:\n" + activity_message
    message += activity_message

if all_good and good_activity:
    message += "All good"

print(message)
check = send_SMS(message)
print(f"SMS sending report: {check}")
