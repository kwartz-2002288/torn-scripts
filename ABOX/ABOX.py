from datetime import datetime, timezone
import os, json, pprint
import requests, gspread, string
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib


def time_refs(APIKEY):
    start_date = datetime.now(timezone.utc)
    print(f"script starts at : {start_date.strftime('%Y/%m/%d %H:%M:%S')} UTC")
    r=requests.get(f"https://api.torn.com/user/?selections=timestamp&key={APIKEY}").json()
    timestamp = r["timestamp"]
    request_date = datetime.fromtimestamp(timestamp, timezone.utc)
    print(f"API request date : {request_date.strftime('%Y/%m/%d %H:%M:%S')} UTC")
    return timestamp, request_date

def col_name(col_idx):
# Transforms a column index (integer starting from 1) to a spreadsheet string description A-Z-AA-AZ...AAA etc
    name = ""
    while col_idx > 0:
        mod = (col_idx - 1) % 26
        name = chr(65 + mod) + name
        col_idx = (col_idx - mod) // 26
    return name

def ex_aequo(scores, symbol = '"'):
    # Replaces ex_aequo ranks by symbol
    N = 0 # previous score
    R = 0 # previous rank
    for L in scores:
        if L[2] == N:
            L[0] = symbol
        else:
            N = L[2]
            R = L[0]
    return scores

def zone_fill(row_min, col_min, data, ws):
# Fills a gspread sheey rectangular zone from row_min, to col_min with data (list of lists)
    n_row, n_col = len(data), len(data[0])
    zone_to_be_filled = ( col_name(col_min) + str(row_min) + ":" +
                        col_name(col_min + n_col -1) + str(row_min + n_row - 1))
    ws.update(zone_to_be_filled, data)
    return

def get_members(APIKEY):
    r = requests.get(f"https://api.torn.com/faction/?selections=basic&key={APIKEY}").json()
    return r["members"]

def dump_members(members, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(members, f)

def load_members(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return json.load(f)

def dump_selected_data(members, file_name, APIKEY):
    # possible data to look at
    # L = ["name", "level", "position", "days_in_faction", "fraud_crimes",
    #      "xantaken", "peoplebusted", "overdosed", "revives", "rankedwarhits", "territoryclears"]
    data_requested = {}
    print("*** Reading players data")
    i = 0
    for id in members.keys():
        r = requests.get(f"https://api.torn.com/user/{id}?selections=crimes,personalstats&key={APIKEY}").json()
        data_requested[id] = r
        i += 1
        print(i, members[id]["name"])
    data_dict = {}
    i = 0
    for id, v in members.items():
        i += 1
        print('***', i, members[id]["name"])
        data_dict[id] = {"name":v["name"],
                         "level":v["level"],
                         "position":v["position"],
                         "days_in_faction":v["days_in_faction"]}
        data_dict[id]["fraud_crimes"] = data_requested[id]["criminalrecord"]["fraud_crimes"]
        drp = data_requested[id]["personalstats"]
        data_dict[id]["xantaken"] = drp["xantaken"]
        data_dict[id]["cantaken"] = drp["cantaken"]
        data_dict[id]["peoplebusted"] = drp["peoplebusted"]
        data_dict[id]["overdosed"] = drp["overdosed"]
        data_dict[id]["revives"] = drp["revives"]
        data_dict[id]["awards"] = drp["awards"]

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f)
    return data_dict

def write_gspread_data(data_dict, request_date_s, ws, nodeName):
    # ABOX dictionnary reconfiguration in list of lists for gspread sheet update
    # Column titles are read on first dictionnary player
    k_id0 = list(data_dict.keys())[0]
    column_titles = ["id"] + list(data_dict[k_id0].keys())
    data = [column_titles]
    # Now we add each player data
    for k_id in data_dict:
        L = [k_id]
        for key, val in data_dict[k_id].items():
            L.append(val)
        data.append(L)
    ws.update_cell(1, 1, "Updated by " + nodeName)
    ws.update_cell(2, 1, request_date_s)
    zone_fill(3, 1, data, ws)

def write_gspread_score(scores, request_date_s, ws, nodeName, column_key):
    ws.update_cell(1, 2, "Status updated by " + nodeName + " on")
    ws.update_cell(2, 2, request_date_s)
    zone_fill(5, 2+4*column_key, scores, ws)

def get_score(file0, file1, members_f0, members_f1, res_file, key_name_list,
            request_date_s, ws_score, nodeName, n_rank):
# Compare two data file at two different time
# Create a text file and arrays to be written as block in spreadsheets
    with open(file0,'r') as f0, open(file1,'r') as f1, open(members_f0,'r') as fm0, open(members_f1,'r') as fm1:
        D0, D1, members0, members1 = (json.load(f0), json.load(f1),
                                      json.load(fm0), json.load(fm1))
        column_key = 0
        for key_name in key_name_list:
            res_file.write(f"\n*** contest : {key_name}\n")
            res_file.write(f"rank;name;delta_{key_name}\n")
            print(f"\n*** contest : {key_name}")
            print(f"rank;name;delta_{key_name}")
            scores = [["rank","name",key_name]]
            result_dict = {}
            total = 0
            for id in members1:
                if id in D0 and id in D1:
                    if D1[id][key_name] > D0[id][key_name]:
                        delta = D1[id][key_name] - D0[id][key_name]
                        result_dict[id] = delta
                        total += delta
            rank = 0
            for id, v in sorted(result_dict.items(),
                                key=lambda x: x[1], reverse = True)[0:n_rank]:
                rank += 1
                res_file.write(f"{rank};{members1[id]['name']};{result_dict[id]}\n")
                print(f"{rank:>2};{members1[id]['name']:^20};{result_dict[id]:>4}")
                scores.append([rank,members1[id]['name'],result_dict[id]])
            res_file.write(f"\n{key_name} faction total = {total}\n")
            print(f"\n{key_name} faction total = {total}")
            ex_aequo(scores)
            scores.insert(0,[" ","faction total", total])
            write_gspread_score(scores, request_date_s, ws_score, nodeName, column_key)
            column_key += 1
        for id in members1:
            if id not in members0:
                res_file.write(f"\nWARNING {members1[id]['name']} was not in faction when the competition started")
        for id in members0:
            if id not in members1:
                res_file.write(f"\nWARNING {members0[id]['name']} is no more in faction")

def competition_analysis(initial_datafile_name, new_datafile_name,initial_membersfile_name,
                    new_membersfile_name, res_file_name, request_date_s,
                    APIKEY, ws_D1, ws_score, nodeName):
# create new results file
    res_file = open(res_file_name, 'w')
    # get competition start time using initial data file
    stat = os.stat(initial_datafile_name)
    print(f"file {initial_datafile_name} os.stat: {stat}")
    c_timestamp = stat.st_birthtime # to be changed in Linux ???
    c_time = datetime.fromtimestamp(c_timestamp, timezone.utc)
    start_date = c_time.strftime('%Y/%m/%d %H:%M:%S') + ' UTC'
    ws_score.update_cell(1, 6, "Competition started on")
    ws_score.update_cell(2, 6, start_date)
    print(f"All contests started at {c_time}")
    res_file.write(f"All contests started at {c_time}\n")
    print(f"leaderboard analysis at {request_date_s}")
    res_file.write(f"Leaderboard analysis at {request_date_s}\n")
    # collect members
    members = get_members(APIKEY)
    n_rank = len(members)
    print(f"\nFaction has currently {n_rank} members\n")
    dump_members(members, new_membersfile_name)

# collect and save new data
# For debugging purpose (not to have to read API data again and again
#    with open(new_datafile_name, 'r', encoding='utf-8') as f:
#        data_dict = json.load(f)
    data_dict = dump_selected_data(members, new_datafile_name, APIKEY)

    # write data on spreadsheet
    write_gspread_data(data_dict, request_date_s, ws_D1, nodeName)
    # ABOX contests
    get_score(initial_datafile_name, new_datafile_name,
            initial_membersfile_name, new_membersfile_name, res_file,
           ["peoplebusted", "overdosed", "xantaken", "cantaken", "fraud_crimes", "revives"],
           request_date_s, ws_score, nodeName, n_rank)
    res_file.close()

def competition_start(initial_datafile_name, initial_membersfile_name,
                        request_date_s, APIKEY, ws_D0, nodeName):
    print(f"All contests started at {request_date_s}")
    # collect members
    members = get_members(APIKEY)
    n_rank = len(members)
    print(f"\nFaction has currently {n_rank} members\n")
    dump_members(members, initial_membersfile_name)
    # collect and save initial data
    data_dict = dump_selected_data(members, initial_datafile_name, APIKEY)
    # write data on spreadsheet
    write_gspread_data(data_dict, request_date_s, ws_D0,  nodeName)

def initialisation():
    # get API keys and sheet key. get computer name
    APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
    repertory=sheetKey_dict['rep']
    APIKEY = APIKey_dict["HectorBerlioz"]
    # Get authorization for gspread
    scope = ['https://spreadsheets.google.com/feeds']
    json_keyfile=repertory+sheetKey_dict['jsonKey']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    gc = gspread.authorize(credentials)
    # Open the google sheet (don't forget to share it with the gspread mail adress)
    ###   projettorn@appspot.gserviceaccount.com   ###
    sheetKey = sheetKey_dict['ABOX']
    # Get worsheets references
    ws_score = gc.open_by_key(sheetKey).worksheet('score')
    ws_D0 = gc.open_by_key(sheetKey).worksheet('D0')
    ws_D1 = gc.open_by_key(sheetKey).worksheet('D1')

    # create execution date
    request_date = datetime.now(timezone.utc)
    #timestamp, request_date = time_refs(APIKEY)
    request_date_f = request_date.strftime('%Y-%m-%d-%H-%M')
    request_date_s = request_date.strftime('%Y/%m/%d %H:%M:%S') + ' UTC'
    print(f"Script starts at : {request_date_s}")

    path = repertory + "ABOX/"
    initial_datafile_name = path + "D0.json"
    initial_membersfile_name = path + "members_initial.json"
    new_datafile_name = path + "D1.json"
    new_membersfile_name = path + "members.json"
    res_file_name = path + f"leaderboard-{request_date_f}.txt"

    # test if competition is starting (existence of D0.json file)
    try:
        with open(initial_datafile_name, "r", encoding='utf-8') as f0:
            print(f"Initial file {initial_datafile_name} exists !")
            competition_analysis(
                initial_datafile_name, new_datafile_name,
                initial_membersfile_name, new_membersfile_name,
                res_file_name, request_date_s, APIKEY, ws_D1, ws_score, nodeName)

    except FileNotFoundError:
        print(f"Starting new competition: creating {initial_datafile_name} file" )
        competition_start(initial_datafile_name, initial_membersfile_name,
                          request_date_s, APIKEY, ws_D0, nodeName)

initialisation()
