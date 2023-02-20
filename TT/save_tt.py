import os, json, requests
from datetime import datetime, timezone

def dump_data(data_dict, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f)

def node():
    nodeName = os.uname().nodename
    if nodeName == 'raspberrypi' or nodeName == 'acer':
        path = "/home/jpr/TT/"
    elif nodeName == 'iMac-JP.local' or 'MacBook-JP.local':
        path = "/Users/jpr/torn-scripts/TT/"
    else:
        raise Exception('Unknown computer')
    return nodeName, path

APIKEY = "UAVVm2ESN4K2Ypr4"
nodeName, path = node()
#r = requests.get(f"https://api.torn.com/faction/?selections=timestamp,territory&key={APIKEY}").json()
r = requests.get(f"https://api.torn.com/torn/?selections=timestamp,territory&key={APIKEY}").json()
request_date = datetime.fromtimestamp(r["timestamp"], timezone.utc).strftime('%Y-%m-%d-%H-%M')
res_file_name = path + f"TT-{request_date}.json"
dump_data(r, res_file_name)
