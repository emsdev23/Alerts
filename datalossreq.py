import requests
import time

pkurl = 'http://localhost:8002/schneider'
whurl = 'http://localhost:8002/datalosswheeled'
bturl = 'http://localhost:8002/batterydata'
dlurl = 'http://localhost:8002/diseldata'
gdurl1 = 'http://localhost:8002/griddatamvp1'
gdurl2 = 'http://localhost:8002/griddatamvp2'
gdurl3 = 'http://localhost:8002/griddatamvp3'
gdurl4 = 'http://localhost:8002/griddatamvp4'
acurl1 = 'http://localhost:8002/acmeterreadings1035'
acurl2 = 'http://localhost:8002/acmeterreadings1147'
whlnull = 'http://localhost:8002/datalosswheelednull30'
whlnull1 = 'http://localhost:8002/datalosswheelednull60'
whlnull2 = 'http://localhost:8002/datalosswheelednull120'
pkurlnull = 'http://localhost:8002/schneidernull30'
pkurlnull1 = 'http://localhost:8002/schneidernull60'
gdnull1 = 'http://localhost:8002/griddatamvp1null30'
gdnull2 = 'http://localhost:8002/griddatamvp2null30'
gdnull3 = 'http://localhost:8002/griddatamvp3null30'
gdnull4 = 'http://localhost:8002/griddatamvp4null30'
thrml = 'http://localhost:8002/thermalstorage'
# gdurl = 'http://localhost:8002/griddata'
# acurl = 'http://localhost:8002/acmeterreadings'

def thermalstorage():
    print("THERMAL")
    pkres = requests.get(thrml)
    print(pkres.json())
    time.sleep(5)

def schneider():
    print("SCHNEIDER")
    pkres = requests.get(pkurl)
    print(pkres.json())
    time.sleep(5)

def gridnull1():
    print("GRID MVP1 NULL")
    gdres = requests.get(gdnull1)
    print(gdres.json())
    time.sleep(5)

def gridnull2():
    print("GRID MVP2 NULL")
    gdres = requests.get(gdnull2)
    print(gdres.json())
    time.sleep(5)

def gridnull3():
    print("GRID MVP3 NULL")
    gdres = requests.get(gdnull3)
    print(gdres.json())
    time.sleep(5)

def gridnull4():
    print("GRID MVP4 NULL")
    gdres = requests.get(gdnull4)
    print(gdres.json())
    time.sleep(5)

def schneidernull():
    print("SCHNEIDER - null")
    pkres = requests.get(pkurlnull)
    print(pkres.json())
    time.sleep(5)

def schneidernull1():
    print("SCHNEIDER - null")
    pkres = requests.get(pkurlnull1)
    print(pkres.json())
    time.sleep(5)

def wheelednull():
    print("WHEELED - null")
    whres = requests.get(whlnull)
    print(whres.json())
    time.sleep(5)

def wheelednull1():
    print("WHEELED - null")
    whres = requests.get(whlnull1)
    print(whres.json())
    time.sleep(5)

def wheelednull2():
    print("WHEELED - null")
    whres = requests.get(whlnull2)
    print(whres.json())
    time.sleep(5)

def wheeled():
    print("WHEELED")
    whres = requests.get(whurl)
    print(whres.json())
    time.sleep(5)

def battery():
    print("BATTERY")
    btres = requests.get(bturl)
    print(btres.json())
    time.sleep(5)

def disel():
    print("DISEL")
    dlres = requests.get(dlurl)
    print(dlres.json())
    time.sleep(5)
    
# def grid():
#     print("GRID")
#     gdres = requests.get(gdurl)
#     print(gdres.json())
#     time.sleep(5)

def grid1():
    print("GRID")
    gdres = requests.get(gdurl1)
    print(gdres.json())
    time.sleep(5)

def grid2():
    print("GRID")
    gdres = requests.get(gdurl2)
    print(gdres.json())
    time.sleep(5)

def grid3():
    print("GRID")
    gdres = requests.get(gdurl3)
    print(gdres.json())
    time.sleep(5)

def grid4():
    print("GRID")
    gdres = requests.get(gdurl4)
    print(gdres.json())
    time.sleep(5)

# def rooftop():
#     print("ROOFTOP")
#     acres = requests.get(acurl)
#     print(acres.json())
#     time.sleep(5)
     
def rooftop1():
    print("ROOFTOP 1035")
    acres = requests.get(acurl1)
    print(acres.json())
    time.sleep(5)

def rooftop2():
    print("ROOFTOP 1147")
    acres = requests.get(acurl2)
    print(acres.json())
    time.sleep(5)



function_names = ['wheeled']
#'thermalstorage','gridnull1','gridnull2','gridnull3','gridnull4','schneidernull','schneidernull1','wheelednull','wheelednull1','wheelednull2','rooftop1','rooftop2','grid4','grid3','grid2','grid1','disel','battery','schneider','wheeled']

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
   
