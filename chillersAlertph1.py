import psycopg2
import time
from datetime import datetime
import pytz

while True:
    conn2 = psycopg2.connect(
        host="10.9.200.203",
        database="cpm_phase_2",
        user="rpuser",
        password="parkPassword")

    cpmcur2 = conn2.cursor()

    cpmcur2.execute("select to_timestamp(timestamp) AS polledTime,device from energymeter where to_timestamp(timestamp)::date = CURRENT_DATE order by timestamp desc, device asc limit 29;")

    res2 = cpmcur2.fetchall()

    stsDict = {
                'chiller1': 0,
                'chiller2': 0,
                'chiller3': 0,
                'chiller4': 0,
                'primarypump1': 0,
                'primarypump2': 0,
                'primarypump3': 0,
                'primarypump4': 0,
                'primarypump5': 0,
                'condensorpump1': 0,
                'condensorpump2': 0,
                'condensorpump3': 0,
                'condensorpump4': 0,
                'condensorpump5': 0,
                'coolingtower1': 0,
                'coolingtower2': 0,
                'coolingtower3': 0,
                'coolingtower4': 0,
                'coolingtower5': 0,
                'coolingtower6': 0,
                'coolingtower7': 0,
                'coolingtower8': 0,
                'coolingtower9': 0,
                'coolingtower10': 0,
                'secondarypump1': 0,
                'secondarypump2': 0,
                'secondarypump3': 0,
                'secondarypump4': 0,
                'secondarypump5': 0
            }
    dataloss = set()

    for i in res2:
        aware_datetime = datetime.now(pytz.timezone('Asia/Kolkata'))

        naive_datetime = datetime.now()

        naive_datetime_with_tz = pytz.timezone('Asia/Kolkata').localize(naive_datetime)

        polledTime = str(i[0])[14:16]
        # print(i[0],i[1])

        time_difference = (naive_datetime_with_tz - i[0]).total_seconds()

        if i[1] == 0 and time_difference >= 3600:
            stsDict['chiller1'] = 1
        else:
            stsDict['chiller1'] = 1
        
        if i[1] == 1 and time_difference >= 3600:
            stsDict['chiller2'] = 1
        else:
            stsDict['chiller2'] = 0
    
        if i[1] == 2 and time_difference >= 3600:
            stsDict['chiller3'] = 1
        else:
            stsDict['chiller3'] = 0
        
        if i[1] == 3 and time_difference >= 3600:
            stsDict['chiller4'] = 1
        else:
            stsDict['chiller4'] = 0
        
        if i[1] == 4 and time_difference >= 3600:
            stsDict['primarypump1'] = 1
        else:
            stsDict['primarypump1'] = 0
        
        if i[1] == 5 and time_difference >= 3600:
            stsDict['primarypump2'] = 1
        else:
            stsDict['primarypump2'] = 0
        
        if i[1] == 6 and time_difference >= 3600:
            stsDict['primarypump3'] = 1
        else:
            stsDict['primarypump3'] = 0
        
        if i[1] == 7 and time_difference >= 3600:
            stsDict['primarypump4'] = 1
        else:
            stsDict['primarypump4'] = 0
        
        if i[1] == 8 and time_difference >= 3600:
            stsDict['primarypump5'] = 1
        else:
            stsDict['primarypump5'] = 0
        
        if i[1] == 9 and time_difference >= 3600:
            stsDict['condensorpump1'] = 1
        else:
            stsDict['condensorpump1']  = 0
        
        if i[1] == 10 and time_difference >= 3600:
            stsDict['condensorpump2']  = 1
        else:
            stsDict['condensorpump2'] = 0
        
        if i[1] == 11 and time_difference >= 3600:
            stsDict['condensorpump3'] = 1
        else:
            stsDict['condensorpump3'] = 0
        
        if i[1] == 12 and time_difference >= 3600:
            stsDict['condensorpump4'] = 1
        else:
            stsDict['condensorpump4'] = 0
        
        if i[1] == 13 and time_difference >= 3600:
            stsDict['condensorpump5'] = 1
        else:
            stsDict['condensorpump5'] = 0
        
        if i[1] == 14 and time_difference >= 3600:
            stsDict['coolingtower1'] = 1
        else:
            stsDict['coolingtower1'] = 0

        if i[1] == 15 and time_difference >= 3600:
            stsDict['coolingtower2'] = 1
        else:
            stsDict['coolingtower2'] = 0
        
        if i[1] == 16 and time_difference >= 3600:
            stsDict['coolingtower3'] = 1
        else:
            stsDict['coolingtower3'] = 0
        
        if i[1] == 17 and time_difference >= 3600:
            stsDict['coolingtower4'] = 1
        else:
            stsDict['coolingtower4'] = 0
        
        if i[1] == 18 and time_difference >= 3600:
            stsDict['coolingtower5'] = 1
        else:
            stsDict['coolingtower5'] = 0
        
        if i[1] == 19 and time_difference >= 3600:
            stsDict['coolingtower6'] = 1
        else:
            stsDict['coolingtower6'] = 0

        if i[1] == 20 and time_difference >= 3600:
            stsDict['coolingtower7'] = 1
        else:
            stsDict['coolingtower7'] = 0
        
        if i[1] == 21 and time_difference >= 3600:
            stsDict['coolingtower8'] = 1
        else:
            stsDict['coolingtower8'] = 0
        
        if i[1] == 22 and time_difference >= 3600:
            stsDict['coolingtower9'] = 1
        else:
            stsDict['coolingtower9'] = 0
        
        if i[1] == 23 and time_difference >= 3600:
            stsDict['coolingtower10'] = 1
        else:
            stsDict['coolingtower10'] = 0
        
        if i[1] == 24 and time_difference >= 3600:
            stsDict['secondarypump1'] = 1
        else:
            stsDict['secondarypump1'] = 0
        
        if i[1] == 25 and time_difference >= 3600:
            stsDict['secondarypump2'] = 1
        else:
            stsDict['secondarypump2'] = 0
        
        if i[1] == 26 and time_difference >= 3600:
            stsDict['secondarypump3'] = 1
        else:
            stsDict['secondarypump3'] = 0
        
        if i[1] == 27 and time_difference >= 3600:
            stsDict['secondarypump4'] = 1
        else:
            stsDict['secondarypump4'] = 0
        
        if i[1] == 28 and time_difference >= 3600:
            stsDict['secondarypump5'] = 1
        else:
            stsDict['secondarypump5'] = 0

        for i in stsDict.keys():
            if stsDict[i] == 1:
                dataloss.add(i)     
        
    print("Data loss in",dataloss)  
    time.sleep(60)

