from datetime import datetime, timezone
import os, json, pprint
import requests, gspread, string
from oauth2client.service_account import ServiceAccountCredentials
import readKeysLib

def ex_aequo(scores, symbol = 'ex-aequo'):
    N = 0 # previous score
    R = 0 # previous rank
    for L in scores:
        if L[2] == N:
            L[0] = symbol
        else:
            N = L[2]
            R = L[0]
    return scores

def col_name(col_idx):
# Transforms a column index (integer >0) to a spreadsheet string description A-Z-AA-AZ...AAA etc
    name = ""
    while col_idx > 0:
        mod = (col_idx - 1) % 26
        name = chr(65 + mod) + name
        col_idx = (col_idx - mod) // 26
    return name

scores = [["rank","name","delta_fraud_crimes"],
[1,"variaxshev",37],
[2,"kwartz",37],
[3,"Alnuza",34],
[4,"p_D",32],
[5,"Coconsy",31],
[6,"Funweezy",31],
[7,"Firelord_Zuko",29],
[8,"PluckyHero",28],
[9,"smaaen",26],
[10,"ashby",25],
[11,"RogueShark21",23],
[12,"Manuito",22],
[13,"ToobZWolf",20],
[14,"nomii",19],
[15,"Penny1",18],
[16,"Klemenso",17],
[17,"MisterLego",17],
[18,"Constantin6",17],
[19,"Richk24",16],
[20,"Phil013",15]]

print(ex_aequo(scores,"#"))

L = [0, 1, 27, 28, 1230]
for i in L:
    print(i, col_name(i))
