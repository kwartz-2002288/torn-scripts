import requests, string
from datetime import time, datetime, timezone, timedelta
import readKeysLib


days_alert_limit = 5


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

def get_properties_info():
    properties_info = requests.get(f"https://api.torn.com/user/?selections=properties&key={APIKEY}").json()["properties"]
    return properties_info

properties_info = get_properties_info()

message = f"{current_date_str} UTC\nAlert from Torn properties\n"

activity_message = ""
all_good = True
not_rented = 0

for property_id, property in properties_info.items():
    if property["status"] == "Owned by them" and property["property"] == "Private Island":

        if property["rented"] is not None: # PI is rented
            days_left = property["rented"]["days_left"]
            if days_left < days_alert_limit:
                all_good = False
                message += f"PI lease ending in {days_left} days\n"
        else: # PI is not rented
            all_good = False
            not_rented += 1

if all_good:
    message += "All good!"
else:
    if not_rented > 0:
        message += f"{not_rented} PI not rented\n"
    check = send_SMS(message)

print(message)
print(f"SMS sending report: {check}")
