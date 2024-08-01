import requests, gspread, string
from datetime import datetime, timezone
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib


def get_name(id):
    try:
        return members[id]["name"]
    except KeyError:
        return "***Kicked"

def get_rank(id):
    try:
        return CE_ranks[id]
    except KeyError:
        return 99

APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
APIKEY = APIKey_dict['Kwartz']

crimeexp = requests.get(f"https://api.torn.com/faction/?selections=crimeexp&key={APIKEY}").json()["crimeexp"]
members = requests.get(f"https://api.torn.com/faction/?selections=basic&key={APIKEY}").json()["members"]
crimes = requests.get(f"https://api.torn.com/faction/?selections=crimes&key={APIKEY}").json()["crimes"]

CE_ranks = {str(id): r+1 for r, id in enumerate(crimeexp)}

# Ask for search time window
print("Indicate the UTC date from which the PAs will be searched")
day1 = int(input("Enter the day (1-31): "))
month1 = int(input("Enter the month (1-12): "))
year1 = 2024
year1 = int(input("Enter the year (four digits): "))
print("Indicate the UTC date before which the PAs will be searched")
day2 = int(input("Enter the day (1-31): "))
month2 = int(input("Enter the month (1-12): "))
year2 = 2024
year2 = int(input("Enter the year (four digits): "))
# Create the datetime objects
user_date1 = datetime(year1, month1, day1, tzinfo=timezone.utc)
user_date2 = datetime(year2, month2, day2, tzinfo=timezone.utc)
# user_date1 = datetime(2024 , 3, 28, tzinfo=timezone.utc)
# user_date2 = datetime(2024, 4, 2, tzinfo=timezone.utc)

# Calculate the corresponding timestamps
timestamp1 = user_date1.timestamp()
timestamp2 = user_date2.timestamp()

# Initialisations
money_total, nPA , nPA_OK = 0, 0, 0
organized_data = []
# Loop on crimes dictionnary
for k, crime in crimes.items():
    timestamp_completed = crime["time_completed"]
    date_completed = datetime.fromtimestamp(timestamp_completed)
    formatted_date = date_completed.strftime("%Y/%m/%d %H:%M:%S")
# test if crime is initiated, is a PA and is in the time interval
    if crime["initiated"] and crime["crime_id"] == 8 \
                          and timestamp1 < timestamp_completed < timestamp2 :
        if crime["success"]:
            result = "Success"
            nPA_OK +=1
        else:
            result = "Failure"
        nPA += 1
        money_gain = int(crime["money_gain"]/1_000_000)
        money_total += money_gain
        participants_id = [list(d.keys())[0] for d in crime["participants"]]
        participants_names = [get_name(id) for id in participants_id]
        participants_ranks = [get_rank(id) for id in participants_id]
        names_ranks = [n + "_" + str(r) for n, r
                    in zip(participants_names, participants_ranks)]
        team = min(participants_ranks)
        organized_data.append([result] + [team] + [money_gain] + names_ranks)

success_rate = int(100*nPA_OK/nPA)
organized_data.sort(key=lambda x: x[1])
# Print the results
print(f"From {user_date1.strftime('%Y/%m/%d')}" +\
        f" to {user_date2.strftime('%Y/%m/%d')}")
print("Result  Team   Money  Members")
for s, r, m, *t in organized_data:
    print(f"{s}  #{r:02d}  {m:3d} m$  ({','.join(t)})")
print(f"Total money  {money_total} m$  Successes: {nPA_OK}/{nPA} = {success_rate}%")
