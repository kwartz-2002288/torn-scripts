import requests, gspread, string
from datetime import datetime, timezone
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

# Set_up
APIKey_dict, sheetKey_dict, nodeName = readKeysLib.getDicts()
repertory=sheetKey_dict['rep']
# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile = repertory + sheetKey_dict['jsonKey']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)
sheetKey = sheetKey_dict['TornStats']
# call API
def updateCrimes(name):
    APIKEY = APIKey_dict[name]
    sk = requests.get(f"https://api.torn.com/user/?selections=skills&key={APIKEY}").json()
    cr = requests.get(f"https://api.torn.com/user/?selections=crimes&key={APIKEY}").json()["criminalrecord"]

    now_date = datetime.now(timezone.utc)
    current_date = now_date.strftime("%d/%m/%Y %H:%M:%S")

    # parsing skill data
    bootlegging = float(sk["bootlegging"])
    burglary = float(sk["burglary"])
    card_skimming = float(sk["card_skimming"])
    graffiti = float(sk["graffiti"])
    hustling = float(sk["hustling"])
    pickpocketing = float(sk["pickpocketing"])
    search_for_cash = float(sk["search_for_cash"])
    shoplifting = float(sk["shoplifting"])
    disposal = float(sk["disposal"])
    reviving = float(sk["reviving"])
    hunting = float(sk["hunting"])
    racing = float(sk["racing"])

    # parsing crimes data
    vandalism = cr["vandalism"]
    theft = cr["theft"]
    counterfeiting = cr["counterfeiting"]
    fraud = cr["fraud"]
    illicitservices = cr["illicitservices"]
    cybercrime = cr["cybercrime"]
    extortion = cr["extortion"]
    illegalproduction = cr["illegalproduction"]
    crime_total = cr["total"]

    # creating row
    crimes2_data = [ #current_date,
    # a strange bug adding a ' before date in spreadsheet need to write the date in another instruction
        bootlegging, burglary, card_skimming, graffiti,
        hustling, pickpocketing, search_for_cash, shoplifting,
        disposal, reviving, hunting, racing,
        vandalism, theft, counterfeiting, fraud,
        illicitservices, cybercrime, extortion, illegalproduction,
        crime_total
    ]
    crimes2_header = [ "date",
        "bootlegging", "burglary", "card_skimming", "graffiti",
        "hustling", "pickpocketing", "search_for_cash", "shoplifting",
        "disposal", "reviving", "hunting", "racing",
        "vandalism", "theft", "counterfeiting", "fraud",
        "illicitservices", "cybercrime", "extortion", "illegalproduction",
        "crime_total"
    ]

    #writing in spreadsheets if total crimes has changed
    ws = gc.open_by_key(sheetKey).worksheet('Crimes2'+name)
    old_total = int(ws.cell(2,1).value)
    if old_total < crime_total:
        ws.update_cell(1, 1, "Updated by " + nodeName)
        # Can be executed only when a new column is created
        #zone_to_be_filled = "A2:Z2"
        #ws.update(zone_to_be_filled, [crimes2_header])
        current_row = ws.cell(1,3).value # last row that has already been written
        current_row = 1 + int(''.join(current_row.split())) #clean string and convert to int
        zone_to_be_filled = "B" + str(current_row) + ":Z" + str(current_row)
        ws.update_cell(current_row, 1, current_date)
        ws.update(zone_to_be_filled, [crimes2_data])

for name in ('Kwartz','Kivou'):
    updateCrimes(name)
