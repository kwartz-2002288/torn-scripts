# Modified to write the whole spreadsheet zone in one instruction

import datetime
import requests, gspread, string
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

# CE SCRIPT RECOPIE LES TARGETS EXPORTEES PAR YATA AU FORMAT .json DANS la spreadsheet TornStats (sheet Targets)
# Ce fichier targets.json doit être placé dans le dossier ..../torn/files !

# APIKeys and sheetKeys are saved in files in an external repertory see the module readKeysLib
APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
repertory=sheetKey_dict['rep']
# Get authorization for gspread and open worksheet
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile=repertory+sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)
sheetKey = sheetKey_dict['TornStats']

print('-> opening sheet')
ws = gc.open_by_key(sheetKey).worksheet('Targets')
print('-> sheet opened')
# ws.update_cell(10,1,currentDateGspread)
# ws.update_cell(11,1,currentDateGspread+0.5)
# previousDateGspreadStr = ws.cell(12,1).value


# Lecture du fichier
targets_dict = readKeysLib.getYATAtargets()
print(f'-> {len(targets_dict)} targets found')
# print(targets_dict)
#print(f'total_ws : {total_ws:.2f}, model: {total_ws_model:.2f}, delta: {delta:.2f} %')
# for id,player in targets_dict.items():
# {"133606":{"name":"WhiteHart","life_current":1902,"life_maximum":6337,"status_description":"Okay","status_details":"","status_color":"green","status_state":"Okay","status_until":0,"level":87,"last_action_relative":"43 days ago","last_action_timestamp":1612282620,"last_action_status":"Offline","update_timestamp":1616014627,"last_attack_attacker":true,"last_attack_timestamp":1614477375,"note":"*****","color":1,"result":"Attacked","fair_fight":2.97,"flat_respect":4.070588235294117,"base_respect":1.3705684293919587,"win":1},

L = []
for id,player in targets_dict.items():
    L.append([id,player["name"],player["color"],player["fair_fight"],player["flat_respect"],player["last_action_relative"],player["note"]])
print(L[0])
print('...')
print(L[-1])
zone = 'A2:'+'G'+str(1+len(L))
print('zone spreadsheet to be filled : ',zone)
ws.update(zone,L)
# print(L)
# ws.update_cell(10,1,currentDateGspread)
# ws.update_cell(11,1,currentDateGspread+0.5)
# previousDateGspreadStr = ws.cell(12,1).value
# ws.update('A'+str(currentRow+1),[newRow])
