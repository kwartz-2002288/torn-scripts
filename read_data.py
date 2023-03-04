import os,json

# create an APIkey dictionnary {user:APIkey, ... }
# from a textfile data
# name1 APIkey1
# name2 APIkey2 etc...


NODE_NAME = os.uname().nodename
if NODE_NAME == 'raspberrypi' or NODE_NAME == 'acer':
    PATH_JPR_TORN_DATA = "/home/jpr/torn-data/"
elif NODE_NAME == 'iMac-JP.local' or NODE_NAME == 'MacBook-JP.local':
    PATH_JPR_TORN_DATA = "/Users/jpr/torn-data/"
else:
    raise Exception('Unknown computer')

# Create and read various constants

PATH_DATA_FOLDER = PATH_JPR_TORN_DATA + "DATA/"

with open(PATH_DATA_FOLDER + 'torn_constants.txt') as f:
    [API_KEYS, SHEET_KEYS, CONSTANTS] = json.load(f)

CONSTANTS["NODE_NAME"] = NODE_NAME
CONSTANTS["PATH_DATA_FOLDER"] = PATH_DATA_FOLDER
CONSTANTS["PATH_JPR_TORN_DATA"] = PATH_JPR_TORN_DATA


# print("read_data module : ****", NODENAME)
# print("read_data module : ****", PATH)
# print("read_data module : ****", CONSTANTS)

# def getYATAtargets():
#     " get the targets exported by YATA"
#     with open(PATH + DATAFOLDER + 'target_list.json','r') as f:
#         dict = json.load(f)
#     return dict

# def getLentStocks():
#     " get the lent stocks information "
#     with open(repertory+'lentStocks.txt','r') as f:
#         dict = json.load(f)
#     return dict
