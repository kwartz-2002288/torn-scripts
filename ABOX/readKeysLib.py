import os,json

# create an APIkey dictionnary {user:APIkey, ... }
# from a textfile data
# name1 APIkey1
# name2 APIkey2 etc...

nodeName = os.uname().nodename
if nodeName == 'raspberrypi' or nodeName == 'acer':
    repertory = '/home/jpr/Documents/torn/files/' # Rapsberry or acer path
elif nodeName == 'iMac-JP.local' or 'MacBook-JP.local':
    repertory = '/Users/jpr/Dropbox/torn/files/' # Mac path
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

# def getLentStocks():
#     " get the lent stocks information "
#     with open(repertory+'lentStocks.txt','r') as f:
#         dict = json.load(f)
#     return dict
