import requests
import time

c5url = "http://localhost:8005/Chiller5Energy"
c6url = "http://localhost:8005/Chiller6Energy"
c7url = "http://localhost:8005/Chiller7Energy"
c8url = "http://localhost:8005/Chiller8Energy"
pp1url = "http://localhost:8005/Primarypump1"
pp2url = "http://localhost:8005/Primarypump2"
pp3url = "http://localhost:8005/Primarypump3"
pp4url = "http://localhost:8005/Primarypump4"
pp5url = "http://localhost:8005/Primarypump5"
cp2url = "http://localhost:8005/Condenserpump2"
cp3url = "http://localhost:8005/Condenserpump3"
cp4url = "http://localhost:8005/Condenserpump4"
cturl = "http://localhost:8005/Coolingtower"
spurl = "http://localhost:8005/Secondarypump"
cbt5url = "http://localhost:8005/Chiller5btu"
cbt6url = "http://localhost:8005/Chiller6btu"
cbt7url = "http://localhost:8005/Chiller7btu"
cbt8url = "http://localhost:8005/Chiller8btu"
hdurl = "http://localhost:8005/header"

def chiller5Energy():
    print("Chiller5")
    c1res = requests.get(c5url)
    print(c1res.json())
    time.sleep(5)

def chiller6Energy():
    print("Chiller6")
    c1res = requests.get(c6url)
    print(c1res.json())
    time.sleep(5)

def chiller7Energy():
    print("Chiller7")
    c1res = requests.get(c7url)
    print(c1res.json())
    time.sleep(5)

def chiller8Energy():
    print("Chiller8")
    c1res = requests.get(c8url)
    print(c1res.json())
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

def Condenserpump2():
    print("Condenserpump2")
    pp5res = requests.get(cp2url)
    print(pp5res.json())
    time.sleep(5)

def Condenserpump3():
    print("Condenserpump3")
    pp5res = requests.get(cp3url)
    print(pp5res.json())
    time.sleep(5)

def Condenserpump4():
    print("Condenserpump4")
    pp5res = requests.get(cp4url)
    print(pp5res.json())
    time.sleep(5)

def Coolingtower():
    print("Coolingtower")
    pp5res = requests.get(cturl)
    print(pp5res.json())
    time.sleep(5)

def Secondarypump():
    print("Secondarypump")
    pp5res = requests.get(spurl)
    print(pp5res.json())
    time.sleep(5)

def Chiller5btu():
    print("Chiller5btu")
    cbt1res = requests.get(cbt5url)
    print(cbt1res.json())
    time.sleep(5)

def Chiller6btu():
    print("Chiller6btu")
    cbt1res = requests.get(cbt6url)
    print(cbt1res.json())
    time.sleep(5)

def Chiller7btu():
    print("Chiller7btu")
    cbt1res = requests.get(cbt7url)
    print(cbt1res.json())
    time.sleep(5)

def Chiller8btu():
    print("Chiller8btu")
    cbt1res = requests.get(cbt8url)
    print(cbt1res.json())
    time.sleep(5)

def header():
    print("header")
    hdres = requests.get(hdurl)
    print(hdres.json())
    time.sleep(5)

function_names = ['chiller5Energy','chiller6Energy','chiller7Energy','chiller8Energy','Primarypump1','Primarypump2','Primarypump3','Primarypump4','Primarypump5','Condenserpump2','Condenserpump3','Condenserpump4','Coolingtower','Secondarypump','Chiller5btu','Chiller6btu','Chiller7btu','Chiller8btu','header']

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