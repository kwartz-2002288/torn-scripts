def getKeys(file_name):
    keys = dict()
    with open(file_name, 'r') as f:
        for l in f.readlines():
            splt = l.strip("\n").replace(" ", "").split(":")
            if len(splt) == 2:
                keys[splt[0]] = splt[1]

    return keys


def apiCall(section, selections, key):
    import requests
    url = "https://api.torn.com/{}/?selections={}&key={}".format(section, selections, key)
    print("API call: {}".format(url))
    return requests.get(url).json()


def cleanhtml(raw_html):
    import re

    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


# bind integers with letters for gspread range
I2A = ["", "A", "B", "C", "D", "E", "F"]


def getSpreadsheet(gsJson, gsID):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    gsURL = 'https://spreadsheets.google.com/feeds'
    gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name("{}.json".format(gsJson), gsURL))
    return gc.open_by_key(gsID)
