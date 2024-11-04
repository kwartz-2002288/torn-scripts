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

id_Nikeh = "111"
id_Boxing_Gloves = "330"
def get_shop_info():
    Nikeh_shop = requests.get(f" https://api.torn.com/torn/?selections=cityshops&&key={APIKEY}").json()["cityshops"][id_Nikeh]
    return Nikeh_shop

Nikeh_shop_inventory = get_shop_info()["inventory"]

message = f"{current_date_str} UTC\nAlert from Nikeh Shop\n"

if id_Boxing_Gloves in Nikeh_shop_inventory:
    N_items = Nikeh_shop_inventory[id_Boxing_Gloves]["in_stock"]
    print(N_items)
    message += f"{N_items} boxing gloves here!"
    print(message)
    check = send_SMS(message)
    print(f"SMS sending report: {check}")
else:
    print("No boxing gloves available!")
