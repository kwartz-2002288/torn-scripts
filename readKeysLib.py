import os, json
from datetime import datetime, timezone

# create an APIkey dictionnary {user:APIkey, ... }
# from a textfile data
# name1 APIkey1
# name2 APIkey2 etc...

nodeName = os.uname().nodename
if nodeName == 'raspberrypi' or nodeName == 'acer':
    repertory = '/home/jpr/torn-data/DATA/' # Rapsberry or acer path
elif nodeName == 'iMac-JP.local' or 'MacBook-JP.local':
    repertory = '/Users/jpr/torn-data/DATA/' # Mac path
else:
    raise Exception('Unknown computer')

def getDicts():
    " get the dictionnaries needed from editable json files"
    with open(repertory+'APIKeys.txt') as f:
        APIKeys = json.load(f)
    with open(repertory+'sheetKeys.txt') as f:
        sheetKeys = json.load(f)
    sheetKeys['rep']=repertory
    return APIKeys, sheetKeys, nodeName

def getYATAtargets():
    " get the targets exported by YATA"
    with open(repertory+'target_list.json','r') as f:
        dict = json.load(f)
    return dict

def python_date_to_excel_number(date):
    "Convert a python date (utc datetime format) to a google sheet compatible number"
    # Define the reference date for Google Sheets (December 30, 1899)"
    reference_date = datetime(1899, 12, 30, tzinfo=timezone.utc)
    # Calculate the difference in days
    days_difference = (date - reference_date).days
    # Calculate the fraction of the day
    fraction_of_day = (date - datetime(date.year, date.month, date.day,
        tzinfo=timezone.utc)).total_seconds() / 86400.0  # 86400 seconds in a day
    # Calculate the total number
    date_number = days_difference + fraction_of_day
    return date_number
