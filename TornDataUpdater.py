from __future__ import print_function
import requests
import gspread
import string
import math, datetime
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

# APIKeys and sheetKeys are saved in files in an external repertory see the module readKeysLib
APIKey_dict,sheetKey_dict = readKeysLib.getDicts()
repertory=sheetKey_dict['rep']

# Get authorization for gspread
scope = ['https://spreadsheets.google.com/feeds']
json_keyfile=repertory+sheetKey_dict['jsonKey2']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)
sheetKey = sheetKey_dict['TornData']

def updatePersonalData(name, gc, sheetKey, APIKey_dict):
        APIKEY = APIKey_dict[name]
        r    = requests.get( 'https://api.torn.com/user/?selections=basic,profile,jobpoints,bars,networth,crimes,education,profile,cooldowns,travel,personalstats,workstats,battlestats,inventory&key={api}'.format( api=APIKEY ) ).json()
        rbis = requests.get( 'https://api.torn.com/user/?selections=money,icons&key={api}'.format( api=APIKEY ) ).json() # incompatibility with networth
        torn = requests.get( 'https://api.torn.com/torn/?selections=education&key={api}'.format( api=APIKEY ) ).json() # incompatibility with networth

# Open the google sheet (don't forget to share it with the gspread mail adress)
###   projettorn@appspot.gserviceaccount.com   ###
        ws = gc.open_by_key(sheetKey).worksheet( 'RawData{}'.format(name) )

        cell_list = ws.range( 'A2:B499' )
        for i in range( len( cell_list ) ):
            cell_list[i].value = ''
        ws.update_cells( cell_list )

        range_it = 2
        sub_r = r['networth']
        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        sub_r = r['criminalrecord']
        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        sub_r = r['jobpoints']['jobs']
        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = 'jobpoints'+key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        try:
            sub_r = r['jobpoints']['companies']
            n_row = len(sub_r)
            cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
            cell_list = ws.range( cell_range )
            for i,key in enumerate(sub_r):
                cell_list[2*i+0].value = 'jobpoints'+sub_r[ key ]["name"].replace(' ', '').lower()
                cell_list[2*i+1].value = sub_r[ key ]["jobpoints"]
            ws.update_cells( cell_list )
            range_it += n_row+1
        except:
            pass

        sub_r = r['cooldowns']
        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        sub_r = r['travel']
        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        sub_r = rbis['icons']
        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        subkey='happy'
        sub_r = r[subkey]
        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = subkey+key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        subkey='life'
        sub_r = r[subkey]
        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = subkey+key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        subkey='energy'
        sub_r = r[subkey]
        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = subkey+key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        subkey='nerve'
        sub_r = r[subkey]
        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = subkey+key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        sub_r = r['personalstats']
        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        job = ''
        for icon in r['basicicons']:
            if r['basicicons'][icon].split(' ')[0] == "Job":
                job = r['basicicons'][icon].split(' ')[2]
            if r['basicicons'][icon].split(' ')[0] == "Company":
                job = r['basicicons'][icon].split('(')[-1].replace(")","")

        drug_addiction = ''
        for icon in rbis['icons']:
            str_split=rbis['icons'][icon].split()
            if "Drug" in str_split and "Addiction" in str_split:
                drug_addiction=str_split[-1].replace("(","").replace(")","")

        sub_r = {'defense':r['defense'],
                 'speed':r['speed'],
                 'dexterity':r['dexterity'],
                 'strength':r['strength'],
                 'education_current':torn['education'][str(r['education_current'])]['name'],
                 'education_timeleft':r['education_timeleft'],
                 'manual_labor':r['manual_labor'],
                 'intelligence':r['intelligence'],
                 'endurance':r['endurance'],
#                print(r['last_action']['relative'])  modif by kwartz (API evolution!)
                 'last_action':r['last_action']['relative'],
                 'awards':r['awards'],
                 'bank_time_left':rbis['city_bank']['time_left'],
                 'rank':r['rank'],
                 'level':r['level'],
                 'job_position':job,
                 'drug_addiction':drug_addiction
                 }

        n_row = len(sub_r)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(sub_r):
            cell_list[2*i+0].value = key
            cell_list[2*i+1].value = sub_r[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

        valuables={  "LionPlushie":"","AfricanViolet":"",
                    "CamelPlushie":"","TribulusOmanense":"",
                    "JaguarPlushie":"","Dahlia":"",
                    "Crocus":"","WolverinePlushie":"",
                    "StingrayPlushie":"","BananaOrchid":"",
                    "Heather":"","NessiePlushie":"",
                    "RedFoxPlushie":"","Orchid":"",
                    "Edelweiss":"","ChamoisPlushie":"",
                    "CeiboFlower":"","MonkeyPlushie":"",
                    "PandaPlushie":"","Peony":"",
                    "CherryBlossom":"",
                    "Xanax":"", "EroticDVD": "", "Ecstasy": ""
        }
        inventory = r['inventory']
        for valuable in valuables:
            for item_in_inventory in inventory:
                if item_in_inventory['name'].replace(' ', '') == valuable:
                    valuables[valuable] = item_in_inventory['quantity']
                    break

        n_row = len(valuables)
        cell_range = 'A{}:B{}'.format( range_it, range_it+n_row-1 )
        cell_list = ws.range( cell_range )
        for i,key in enumerate(valuables):
            cell_list[2*i+0].value = key
            cell_list[2*i+1].value = valuables[ key ]
        ws.update_cells( cell_list )
        range_it += n_row+1

def updateItemPrices(name, gc, sheetKey, APIKey_dict):
        APIKEY = APIKey_dict[name]
        item_c = requests.get( 'http://travelrun.torncentral.com/records.json' ).json()
        countries = { "1" : ("Mexico", 18),
                      "2" : ("Cayman Islands", 25),
                      "3" : ("Canada", 29),
                      "4" : ("Hawaii", 94),
                      "5" : ("United Kingdom", 111),
                      "6" : ("Argentina", 117),
                      "7" : ("Switzerland", 123),
                      "8" : ("Japan", 158),
                      "9" : ("China", 169),
                      "10": ("UAE", 190),
                      "11": ("South Africa", 208) }

        item_t = requests.get( 'https://api.torn.com/torn/?selections=items&key={api}'.format( api=APIKEY ) ).json()['items']
        r = [['country', 'travel_time', 'name', 'type', 'buy_price', 'sell_price', 'market_value', 'cost', 'left']]
        for kc in countries:
            country    = countries[ kc ][0]
            traveltime = countries[ kc ][1]
            try:
                for ki in item_c[ kc ]:
                    a = item_t[ ki ][ "name" ]
                    b = int(kc)
                    if( ( b == 1  and ( a == "Jaguar Plushie" or a == "Dahlia" ) ) or
                        ( b == 2  and ( a == "Stingray Plushie" or a == "Banana Orchid" ) ) or
                        ( b == 3  and ( a == "Wolverine Plushie" or a == "Crocus" ) ) or
                        ( b == 4  and ( a == "Orchid" ) ) or
                        ( b == 5  and ( a == "Nessie Plushie" or a == "Red Fox Plushie" or a == "Heather" ) ) or
                        ( b == 6  and ( a == "Monkey Plushie" or a == "Ceibo Flower" ) ) or
                        ( b == 7  and ( a == "Chamois Plushie" or a == "Edelweiss" ) ) or
                        ( b == 8  and ( a == "Cherry Blossom" ) ) or
                        ( b == 9  and ( a == "Peony" or a == "Panda Plushie" ) ) or
                        ( b == 10 and ( a == "Tribulus Omanense" or a == "Camel Plushie" ) ) or
                        ( b == 11 and ( a == "Lion Plushie" or a == "African Violet" or a == "Xanax" ) ) ):
                #if not ( ( item_t[ ki ][ "name" ] == "Jaguar Plushie" and country == "United Kingdom"  ) or
                #         ( item_t[ ki ][ "name" ] == "Dahlia"         and country == "Switzerland"  ) ):
                            r.append( [country,traveltime,
                                    item_t[ ki ][ "name" ],
                                    item_t[ ki ][ "type" ],
                                    item_t[ ki ][ "buy_price" ],
                                    item_t[ ki ][ "sell_price" ],
                                    item_t[ ki ][ "market_value" ],
                                    item_c[ kc ][ ki ]["cost"],
                                    item_c[ kc ][ ki ]["left"]] )
            except:
                print("No objects in: {}".format(country))
                pass

        ws = gc.open_by_key(sheetKey).worksheet( 'RawDataItems' )

        n_row = len(r)
        n_col = len(r[0])
        cell_range = 'A1:{}{}'.format( string.ascii_uppercase[ n_col-1 ], n_row )
        cell_list = ws.range( cell_range )
        for i in range( n_row ):
            for j in range( n_col ):
                cell_list[n_col*i+j].value = r[ i ][ j ]

        ws.update_cells( cell_list )

def updateDate(wsName,gc,sheetKey,row,column):
    # write the update date
    ws = gc.open_by_key(sheetKey).worksheet(wsName)
    current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    ws.update_cell( row,column,"Last update : " + current_date)

for name in ('Kivou','Kwartz','Quatuor','Argozdoc'):
    updatePersonalData( name , gc, sheetKey, APIKey_dict )

updateItemPrices( 'Quatuor', gc, sheetKey, APIKey_dict )

updateDate('UserStats',gc,sheetKey,1,4)
updateDate('Sets', gc, sheetKey,1,1)
