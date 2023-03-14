from datetime import datetime, timezone
import os, json, pprint
import requests, gspread, string
from oauth2client.service_account import ServiceAccountCredentials
import read_data

def time_refs(): # not used
    start_date = datetime.now(timezone.utc)
    print(f"script starts at : {start_date.strftime('%Y/%m/%d %H:%M:%S')} UTC")
    r=requests.get(f"https://api.torn.com/user/?selections=timestamp&key={API_KEY}").json()
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

def get_members():
    r = requests.get(f"https://api.torn.com/faction/?selections=basic&key={API_KEY}").json()
    return r["members"]

def dump_members(members, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(members, f)

def load_members(file_name): # not used
    with open(file_name, 'r', encoding='utf-8') as f:
        return json.load(f)

def zone_fill(row_min, col_min, data, ws):
# Fills a rectangular zone in gspread sheet ws starting
# from row_min, col_min (integer indexes starting from 1) with data (list of lists)
    n_row, n_col = len(data), len(data[0])
    zone_to_be_filled = ( col_name(col_min) + str(row_min) + ":" +
                        col_name(col_min + n_col -1) + str(row_min + n_row - 1))
    ws.update(zone_to_be_filled, data)
    return

def dump_selected_data(members, file_name):
    # possible data to look at
    # L = ["name", "level", "position", "days_in_faction", "fraud_crimes",
    #      "xantaken", "peoplebusted", "overdosed", "revives", "rankedwarhits", "territoryclears"]
    data_requested = {}
    i = 0
    for id in members.keys():
        r = requests.get(f"https://api.torn.com/user/{id}?selections=crimes,personalstats&key={API_KEY}").json()
        data_requested[id] = r
        i += 1
        if PRINT_LEVEL > 1:
            print(i, members[id]["name"])
    data_dict = {}
    for id, v in members.items():
        i += 1
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
        data_dict[id]["attacksassisted"] = drp["attacksassisted"]
        data_dict[id]["defendswon"] = drp["defendswon"]

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f)
    return data_dict

def write_gspread_data(data_dict, ws):
    # BOXCAR dictionnary reconfiguration in list of lists for gspread sheet update
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
    ws.update_cell(1, 1, "Updated by " + NODE_NAME)
    ws.update_cell(2, 1, REQUEST_DATE_S)
    zone_fill(3, 1, data, ws)

def write_gspread_score(scores, column_key):
    WS_SCORE.update_cell(1, 2, "Status updated by " + NODE_NAME + " on")
    WS_SCORE.update_cell(2, 2, REQUEST_DATE_S)
    zone_fill(5, 2+4*column_key, scores, WS_SCORE)

def get_score(file0, file1, members_f0, members_f1, res_file, key_name_list, n_rank):
# Compare two data file at two different time
# Create a text file and arrays to be written as block in spreadsheets
    with open(file0,'r') as f0, open(file1,'r') as f1, open(members_f0,'r') as fm0, open(members_f1,'r') as fm1:
        D0, D1, members0, members1 = (json.load(f0), json.load(f1),
                                      json.load(fm0), json.load(fm1))
        column_key = 0
        for key_name in key_name_list:
            if RES_FILE:
                res_file.write(f"\n*** contest : {key_name}\n")
                res_file.write(f"rank;name;delta_{key_name}\n")
            if PRINT_LEVEL > 0:
                print(f"\n*** contest : {key_name}")
            if PRINT_LEVEL > 1:
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
                if RES_FILE:
                    res_file.write(f"{rank};{members1[id]['name']};{result_dict[id]}\n")
                if PRINT_LEVEL > 1:
                    print(f"{rank:>2};{members1[id]['name']:^20};{result_dict[id]:>4}")
                scores.append([rank,members1[id]['name'],result_dict[id]])
            if RES_FILE:
                res_file.write(f"\n{key_name} faction total = {total}\n")
            if PRINT_LEVEL > 0:
                print(f"\n{key_name} faction total = {total}")
            ex_aequo(scores)
            scores.insert(0,[" ","faction total", total])
            write_gspread_score(scores, column_key)
            column_key += 1
        if RES_FILE:
            for id in members1:
                if id not in members0:
                    res_file.write(f"\nWARNING {members1[id]['name']} was not in faction when the competition started")
            for id in members0:
                if id not in members1:
                    res_file.write(f"\nWARNING {members0[id]['name']} is no more in faction")

def competition_analysis():
    # get competition start time using initial data file
    stat = os.stat(INITIAL_DATA_FILE_NAME)
    c_timestamp = stat.st_ctime
    c_time = datetime.fromtimestamp(c_timestamp, timezone.utc)
    start_date = c_time.strftime('%Y/%m/%d %H:%M:%S') + ' UTC'
    WS_SCORE.update_cell(1, 6, "Competition started on")
    WS_SCORE.update_cell(2, 6, start_date)
    # create new results file
    if RES_FILE:
        res_file = open(RES_FILE_NAME, 'w')
        res_file.write(f"All contests started at {start_date}\n")
        res_file.write(f"Leaderboard analysis at {REQUEST_DATE_S}\n")
    else:
        res_file = None
    # collect members
    members = get_members()
    n_rank = len(members)
    dump_members(members, NEW_MEMBERS_FILE_NAME)

    if PRINT_LEVEL > 1:
        print(f"file {INITIAL_DATA_FILE_NAME} os.stat: {stat}")
    if PRINT_LEVEL > 0:
        print(f"All contests started at {c_time}")
        print(f"leaderboard analysis at {REQUEST_DATE_S}")
        print(f"\nFaction has currently {n_rank} members\n")

# For debugging purpose (not to have to read API data again and again
#    with open(new_datafile_name, 'r', encoding='utf-8') as f:
#        data_dict = json.load(f)

# collect and save new data
    data_dict = dump_selected_data(members, NEW_DATA_FILE_NAME)

    # write data on spreadsheet
    write_gspread_data(data_dict, WS_D1)
    # BOXCAR contests
    get_score(INITIAL_DATA_FILE_NAME, NEW_DATA_FILE_NAME,
              INITIAL_MEMBERS_FILE_NAME, NEW_MEMBERS_FILE_NAME, res_file,
              ["peoplebusted", "overdosed", "xantaken", "cantaken", "fraud_crimes", "revives", "attacksassisted"], n_rank)
    if RES_FILE:
        res_file.close()

def competition_start():
    if PRINT_LEVEL > 0:
        print(f"All contests started at {REQUEST_DATE_S}")
    # collect members
    members = get_members()
    n_rank = len(members)
    if PRINT_LEVEL > 0:
        print(f"\nFaction has currently {n_rank} members\n")
    dump_members(members, INITIAL_MEMBERS_FILE_NAME)
    # collect and save initial data
    data_dict = dump_selected_data(members, INITIAL_DATA_FILE_NAME)
    # write data on spreadsheet
    write_gspread_data(data_dict, WS_D0)

def initialisation():
    if PRINT_LEVEL > 0:
        print(f"Script starts at : {REQUEST_DATE_S}")
    # test if competition is starting (existence of D0.json file)
    try:
        with open(INITIAL_DATA_FILE_NAME, "r", encoding='utf-8') as f0:
            if PRINT_LEVEL > 0:
                print(f"Initial file {INITIAL_DATA_FILE_NAME} exists !")
            competition_analysis()

    except FileNotFoundError:
        if PRINT_LEVEL > 0:
            print(f"Starting new competition: creating {INITIAL_DATA_FILE_NAME} file" )
        competition_start()

API_KEY = read_data.API_KEYS["Kwartz"]
SHEET_KEYS = read_data.SHEET_KEYS
CONSTANTS = read_data.CONSTANTS
PATH_JPR_TORN_DATA = CONSTANTS["PATH_JPR_TORN_DATA"]
PATH_BOXCAR_FOLDER = PATH_JPR_TORN_DATA + CONSTANTS["BOXCAR_FOLDER"]
PATH_DATA_FOLDER = CONSTANTS["PATH_DATA_FOLDER"]
NODE_NAME = CONSTANTS["NODE_NAME"]
JSON_KEYFILE = PATH_DATA_FOLDER + SHEET_KEYS["jsonKey"]
PRINT_LEVEL = CONSTANTS["PRINT_LEVEL"]
RES_FILE = CONSTANTS["RES_FILE"]

GC = gspread.authorize(
        ServiceAccountCredentials.from_json_keyfile_name
        (JSON_KEYFILE, CONSTANTS["SCOPE"]))
WS_SCORE = GC.open_by_key(SHEET_KEYS["BOXCAR"]).worksheet('score')
WS_D0 = GC.open_by_key(SHEET_KEYS["BOXCAR"]).worksheet('D0')
WS_D1 = GC.open_by_key(SHEET_KEYS["BOXCAR"]).worksheet('D1')

REQUEST_DATE = datetime.now(timezone.utc)
REQUEST_DATE_F = REQUEST_DATE.strftime('%Y-%m-%d-%H-%M')
REQUEST_DATE_S = REQUEST_DATE.strftime('%Y/%m/%d %H:%M:%S') + ' UTC'

INITIAL_DATA_FILE_NAME = PATH_BOXCAR_FOLDER + "D0.json"
NEW_DATA_FILE_NAME = PATH_BOXCAR_FOLDER + "D1.json"
INITIAL_MEMBERS_FILE_NAME = PATH_BOXCAR_FOLDER + "members_initial.json"
NEW_MEMBERS_FILE_NAME = PATH_BOXCAR_FOLDER + "members.json"
RES_FILE_NAME = PATH_BOXCAR_FOLDER + f"leaderboard-{REQUEST_DATE_F}.txt"

# print(NEW_DATA_FILE_NAME, RES_FILE_NAME, JSON_KEYFILE)

initialisation()
