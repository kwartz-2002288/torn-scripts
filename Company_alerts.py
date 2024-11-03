import requests, string
from datetime import time, datetime, timezone, timedelta
import readKeysLib


trains_alert_limit = 11
afk_alert_limit = 12 # (hours)


# script execution start schedule
now_date = datetime.now(timezone.utc)
current_date_str = now_date.strftime("%d/%m/%Y %H:%M:%S")

# Set_up
APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
repertory=sheetKey_dict['rep']
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

def get_company_info():
    company_employees = requests.get(f"https://api.torn.com/company/?selections=employees&key={APIKEY}").json()["company_employees"]
    company_detailed = requests.get(f"https://api.torn.com/company/?selections=detailed&key={APIKEY}").json()["company_detailed"]
    return company_detailed["trains_available"], company_employees

trains_available, company_employees = get_company_info()

message = f"{current_date_str} UTC\nMessage from NNN company\n"
#if trains_available > 8 and test_time_slot(start_hour=12, start_minute=5, interval_minute=15):
if trains_available > trains_alert_limit:
    message += f"ALERT! {trains_available} trains available\n"
else:
    message += f"{trains_available} trains available\n"

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
    employee_date = datetime.fromtimestamp(timestamp, timezone.utc)
    afk_duration = now_date - employee_date
    afk_days = afk_duration.days
    afk_hours = afk_duration.seconds // 3600
    if afk_days*24 + afk_hours > afk_alert_limit:
        good_activity = False
        activity_message += f"{position} {name}\n"
        if afk_days > 0:
            activity_message += f"{afk_days}d "
        activity_message += f"{afk_hours}h\n"
if not good_activity:
    activity_message = "Employee inactivity:\n" + activity_message
    message += activity_message
else:
    message +="Good Employee Activity !!!\n"
print(message)
check = send_SMS(message)
print(f"SMS sending report: {check}")
