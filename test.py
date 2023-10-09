import os,json

D = {"K1" : "you", "K2" : "me"}
L = ["a", "b", "c", "d"]
print(D)
print(L)
structure = [L,D]
path = "/Users/jpr/torn-data/DATA/"
# with open(path+'structure.txt','w') as f:
#     json.dump(structure, f)
print(structure)
with open(path+'structure.txt','r') as f:
	S = json.load(f)
print(S)
print(S[1]["K1"])

print("test pour github")
print("encore un petit dernier test pour github")
