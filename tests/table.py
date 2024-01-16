"""
DATA1  DATA2  DATA3
-----  -----  -----
TESTA  TESTA  TESTA
TESTB  TESTB  TESTB
"""

spaces = 2

def create_table(header: list[str], datas: list[list[str]]):
    x = []

    for h in header:
        x.append("-"*len(h))

    print((" "*spaces).join(header))
    print((" "*spaces).join(x))

    sesso = len(datas) - 1

    for i in range(sesso):
        print((" "*spaces).join(datas[i]))
    

create_table(
    ["Name", "Surname"],
    [
        ["Marco", "Furry"],
        ["Luigi", "Ferro"],
        ["Lorenzo", "Ferrari"],
    ])