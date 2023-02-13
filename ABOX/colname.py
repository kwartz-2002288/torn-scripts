def index_to_col_name(col_idx):
    name = ""
    while col_idx > 0:
        mod = (col_idx - 1) % 26
        name = chr(65 + mod) + name
        col_idx = (col_idx - mod) // 26
    return name

def col_name_to_index(col_name):
    idx = 0
    for i, char in enumerate(col_name[::-1]):
        idx += (ord(char) - 64) * (26 ** i)
    return idx

L = [1, 5, 11, 25, 26 , 27, 100, 215, 676, 677, 702, 703, 1024, 111111, 229549]
L1 = [index_to_col_name(i) for i in L]
print(L1)

L2 = [col_name_to_index(st) for st in L1]
print(L2)
