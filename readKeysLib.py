# create an APIkey dictionnary {user:APIkey, ... } 
# from a textfile data
# name1 APIkey1
# name2 APIkey2 etc...

def getKeyDict(file_name):
    " create a Key dictionnary {name:key, ... } from a textfile: name,key\n etc "
    myFile=open(file_name,'r')
    dict={}
    for line in myFile:
        L=line.rstrip('\n').split(',')
        dict[L[0]] = L[1]
    myFile.close()
    return dict

def getDicts():
    " get the two dictionnaries needed "

    #repertory = '/home/jpr/Documents/torn/files/'  # Rapsberry path
    #repertory = '/Users/jpr/Documents/Dropbox/JP-Manu/torn/files/' # MacBook path
    repertory = '/Users/jpr/Dropbox/JP-Manu/torn/files/' # iMac path

    APIKey = getKeyDict(repertory+'APIKeys.txt')
    sheetKey = getKeyDict(repertory+'sheetKeys.txt')
    sheetKey['rep']=repertory
    return APIKey, sheetKey
    
