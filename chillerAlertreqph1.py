import requests
import time

c1url = "http://localhost:8002/Chiller1Energy"
c2url = "http://localhost:8002/Chiller2Energy"
c3url = "http://localhost:8002/Chiller3Energy"
c4url = "http://localhost:8002/Chiller4Energy"
pp1url = "http://localhost:8002/Primarypump1"
pp2url = "http://localhost:8002/Primarypump2"
pp3url = "http://localhost:8002/Primarypump3"
pp4url = "http://localhost:8002/Primarypump4"
pp5url = "http://localhost:8002/Primarypump5"
cp1url = "http://localhost:8002/Condenserpump1"
cp2url = "http://localhost:8002/Condenserpump2"
cp3url = "http://localhost:8002/Condenserpump3"
cp4url = "http://localhost:8002/Condenserpump4"
cp5url = "http://localhost:8002/Condenserpump5"
ct1url = "http://localhost:8002/Coolingtower1"
ct2url = "http://localhost:8002/Coolingtower2"
ct3url = "http://localhost:8002/Coolingtower3"
ct4url = "http://localhost:8002/Coolingtower4"
ct5url = "http://localhost:8002/Coolingtower5"
ct6url = "http://localhost:8002/Coolingtower6"
ct7url = "http://localhost:8002/Coolingtower7"
ct8url = "http://localhost:8002/Coolingtower8"
ct9url = "http://localhost:8002/Coolingtower9"
ct10url = "http://localhost:8002/Coolingtower10"
sp1 = "http://localhost:8002/Secondarypump1"
sp2 = "http://localhost:8002/Secondarypump2"
sp3 = "http://localhost:8002/Secondarypump3"
sp4 = "http://localhost:8002/Secondarypump4"
sp5 = "http://localhost:8002/Secondarypump5"
cbt1url = "http://localhost:8002/Chiller1btu"
cbt2url = "http://localhost:8002/Chiller2btu"
cbt3url = "http://localhost:8002/Chiller3btu"
cbt4url = "http://localhost:8002/Chiller4btu"
hdurl = "http://localhost:8002/header"
cdurl = "http://localhost:8002/Condensor"

def chiller1Energy():
    print("Chiller1")
    c1res = requests.get(c1url)
    print(c1res.json())
    time.sleep(5)

def chiller2Energy():
    print("Chiller2")
    c2res = requests.get(c2url)
    print(c2res.json())
    time.sleep(5)

def chiller3Energy():
    print("Chiller3")
    c3res = requests.get(c3url)
    print(c3res.json())
    time.sleep(5)

def chiller4Energy():
    print("Chiller4")
    c4res = requests.get(c4url)
    print(c4res.json())
    time.sleep(5)

def Primarypump1():
    print("Primarypump1")
    pp1res = requests.get(pp1url)
    print(pp1res.json())
    time.sleep(5)

def Primarypump2():
    print("Primarypump2")
    pp2res = requests.get(pp2url)
    print(pp2res.json())
    time.sleep(5)

def Primarypump3():
    print("Primarypump3")
    pp3res = requests.get(pp3url)
    print(pp3res.json())
    time.sleep(5)

def Primarypump4():
    print("Primarypump4")
    pp4res = requests.get(pp4url)
    print(pp4res.json())
    time.sleep(5)

def Primarypump5():
    print("Primarypump5")
    pp5res = requests.get(pp5url)
    print(pp5res.json())
    time.sleep(5)

def Condenserpump1():
    print("Condenserpump1")
    cp1res = requests.get(cp1url)
    print(cp1res.json())
    time.sleep(5)

def Condenserpump2():
    print("Condenserpump2")
    cp2res = requests.get(cp2url)
    print(cp2res.json())
    time.sleep(5)

def Condenserpump3():
    print("Condenserpump3")
    cp3res = requests.get(cp3url)
    print(cp3res.json())
    time.sleep(5)

def Condenserpump4():
    print("Condenserpump4")
    cp4res = requests.get(cp4url)
    print(cp4res.json())
    time.sleep(5)

def Condenserpump5():
    print("Condenserpump5")
    cp5res = requests.get(cp5url)
    print(cp5res.json())
    time.sleep(5)

def Collingtower1():
    print("Collingtower1")
    ct1res = requests.get(ct1url)
    print(ct1res.json())
    time.sleep(5)

def Collingtower2():
    print("Collingtower2")
    ct2res = requests.get(ct2url)
    print(ct2res.json())
    time.sleep(5)


def Collingtower3():
    print("Collingtower3")
    ct3res = requests.get(ct3url)
    print(ct3res.json())
    time.sleep(5)

def Collingtower4():
    print("Collingtower4")
    ct4res = requests.get(ct4url)
    print(ct4res.json())
    time.sleep(5)

def Collingtower5():
    print("Collingtower5")
    ct5res = requests.get(ct5url)
    print(ct5res.json())
    time.sleep(5)

def Collingtower6():
    print("Collingtower6")
    ct6res = requests.get(ct6url)
    print(ct6res.json())
    time.sleep(5)

def Collingtower7():
    print("Collingtower7")
    ct7res = requests.get(ct7url)
    print(ct7res.json())
    time.sleep(5)

def Collingtower8():
    print("Collingtower8")
    ct8res = requests.get(ct8url)
    print(ct8res.json())
    time.sleep(5)

def Collingtower9():
    print("Collingtower9")
    ct9res = requests.get(ct9url)
    print(ct9res.json())
    time.sleep(5)

def Collingtower10():
    print("Collingtower10")
    ct10res = requests.get(ct10url)
    print(ct10res.json())
    time.sleep(5)

def Secondarypump1():
    print("Secondarypump1")
    sp1res = requests.get(sp1)
    print(sp1res.json())
    time.sleep(5)

def Secondarypump2():
    print("Secondarypump2")
    sp2res = requests.get(sp2)
    print(sp2res.json())
    time.sleep(5)

def Secondarypump3():
    print("Secondarypump3")
    sp3res = requests.get(sp3)
    print(sp3res.json())
    time.sleep(5)

def Secondarypump4():
    print("Secondarypump4")
    sp4res = requests.get(sp4)
    print(sp4res.json())
    time.sleep(5)

def Secondarypump5():
    print("Secondarypump5")
    sp5res = requests.get(sp5)
    print(sp5res.json())
    time.sleep(5)

def Chiller1btu():
    print("Chiller1btu")
    cbt1res = requests.get(cbt1url)
    print(cbt1res.json())
    time.sleep(5)

def Chiller2btu():
    print("Chiller2btu")
    cbt2res = requests.get(cbt2url)
    print(cbt2res.json())
    time.sleep(5)

def Chiller3btu():
    print("Chiller3btu")
    cbt3res = requests.get(cbt3url)
    print(cbt3res.json())
    time.sleep(5)

def Chiller4btu():
    print("Chiller4btu")
    cbt4res = requests.get(cbt4url)
    print(cbt4res.json())
    time.sleep(5)

def header():
    print("header")
    hdres = requests.get(hdurl)
    print(hdres.json())
    time.sleep(5)

def Condensor():
    print("Condensor")
    cdres = requests.get(cdurl)
    print(cdres.json())
    time.sleep(5)

function_names = ['chiller1Energy','chiller2Energy','chiller3Energy','chiller4Energy','Primarypump1','Primarypump2','Primarypump3','Primarypump4','Primarypump5','Condenserpump1','Condenserpump2','Condenserpump3','Condenserpump4','Condenserpump5','Collingtower1','Collingtower2','Collingtower3','Collingtower4','Collingtower5','Collingtower6','Collingtower7','Collingtower8','Collingtower9','Collingtower10','Secondarypump1','Secondarypump2','Secondarypump3','Secondarypump4','Secondarypump5','Condensor','header','Chiller1btu','Chiller2btu','Chiller3btu','Chiller4btu']

while True:
    for name in function_names:
        if name in globals() and callable(globals()[name]):
            function = globals()[name]
            try:
                result = function()
            except:
                continue
        else:
            print(f"Function {name} not found.")    
    
    time.sleep(100)