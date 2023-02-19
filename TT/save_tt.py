import os, json, requests
from datetime import datetime, timezone


# all terts
# https://api.torn.com/torn/?selections=timestamp,territory&key=UAVVm2ESN4K2Ypr4
# faction terts
# https://api.torn.com/faction/?selections=territory&key=UAVVm2ESN4K2Ypr4

def dump_data(data_dict, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f)

def node():
    nodeName = os.uname().nodename
    if nodeName == 'raspberrypi' or nodeName == 'acer':
        repertory = '/home/jpr/Documents/torn/files/' # Rapsberry or acer path
        path = "/home/jpr/Documents/TT/"
    elif nodeName == 'iMac-JP.local' or 'MacBook-JP.local':
        repertory = '/Users/jpr/Dropbox/torn/files/' # Mac path
        path = "/Users/jpr/torn-scripts/TT/"
    else:
        raise Exception('Unknown computer')
    return nodeName, repertory, path

APIKEY = "UAVVm2ESN4K2Ypr4"
nodeName, repertory, path = node()
print(path)
r = requests.get(f"https://api.torn.com/faction/?selections=timestamp,territory&key={APIKEY}").json()
#r = requests.get(f"https://api.torn.com/torn/?selections=timestampterritory&key={APIKEY}").json()
request_date = datetime.fromtimestamp(r["timestamp"], timezone.utc).strftime('%Y-%m-%d-%H-%M')
res_file_name = path + f"TT-{request_date}.txt"
print(res_file_name)
dump_data(r, res_file_name)
