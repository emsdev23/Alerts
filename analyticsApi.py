from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from fastapi.responses import JSONResponse

app = FastAPI()

origins = [
    "*",
    # Add more origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_emsdb():
    db = mysql.connector.connect(
        host="121.242.232.211",
        user="emsroot",
        password="22@teneT",
        database='EMS',
        port=3306
    )
    return db

def get_awsdb():
    db = mysql.connector.connect(
        host="43.205.196.66",
        user="emsroot",
        password="22@teneT",
        database='EMS',
        port=3307
    )
    return db

def get_meterdb():
    db=mysql.connector.connect(
        host="43.205.196.66",
        user="emsroot",
        password="22@teneT",
        database='meterdata',
        port=3307
    )
    return db


@app.get('/Analytics/rooftopSolar')
def peak_demand_date(db: mysql.connector.connect = Depends(get_awsdb)):
    roofTop_solar = []
    try:
        processed_db = get_awsdb()
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"MySQL connection error: {str(e)}"})
    
    bms_cur = processed_db.cursor()

    bms_cur.execute("SELECT polledTime,energy,irradiation,expph1Energy,expph1Energy,ph1Actual,ph2Actual FROM EMS.roofTopHour where date(polledTime) = curdate();")

    res = bms_cur.fetchall()

    for i in res:
        polledTime = str(i[0])[11:16]
        roofTop_solar.append({'polledTime':polledTime,'Energy':i[1],'irradiation':i[2],'expph1Energy':i[3],
                              'expph2Energy':i[4],'ph1Actual':i[5],'ph2Actual':i[6]})
        
    return roofTop_solar


@app.post('/Analytics/rooftopSolar/filtered')
def peak_demand_date(data: dict, db: mysql.connector.connect = Depends(get_awsdb)):
    roofTop_solar = []
    try:
        value = data.get('date')

        if value and isinstance(value, str):
            with db.cursor() as bms_cur:

                bms_cur.execute("SELECT polledTime,energy,irradiation,expph1Energy,expph1Energy,ph1Actual,ph2Actual FROM EMS.roofTopHour where date(polledTime) = curdate();")

                res = bms_cur.fetchall()

                for i in res:
                    polledTime = str(i[0])[11:16]
                    roofTop_solar.append({'polledTime':polledTime,'Energy':i[1],'irradiation':i[2],'expph1Energy':i[3],
                                        'expph2Energy':i[4],'ph1Actual':i[5],'ph2Actual':i[6]})
                    
    except mysql.connector.Error as e:
        return JSONResponse(content={"error": "MySQL connection error"}, status_code=500)
    
    return roofTop_solar

@app.get('/Upsanalytics/energy_VS_packsoc')
def peak_demand_date(db: mysql.connector.connect = Depends(get_emsdb)):
    ups_list = []
    try:
        processed_db = get_emsdb()
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"MySQL connection error: {str(e)}"})
    
    bms_cur = processed_db.cursor()

    bms_cur.execute("""SELECT MIN(pack_usable_soc) AS pack_usable_soc,
                            MAX(received_time) AS received_time,
                            MAX(upsbatterystatus) AS upsbatterystatus,
                            MAX(upschargingenergy) AS upschargingenergy,
                            MAX(upsdischargingenergy) AS upsdischargingenergy,
                            HOUR(received_time) AS hr,
                            MINUTE(received_time) AS mint
                        FROM 
                            EMS.EMSUPSBattery
                        WHERE 
                            DATE(received_time) = CURDATE()
                        GROUP BY 
                            hr, mint;""")
    
    res = bms_cur.fetchall()

    for i in res:
        polledTime = str(i[1])[11:16]
        if i[2] == 'IDLE':
            batteryEnergy = 0.01
        elif i[2] == 'CHG':
            batteryEnergy = i[3]/100
        elif i[2] == 'DCHG':
            batteryEnergy = i[4]/100
        ups_list.append({'packsoc':i[0],'batteryEnergy':batteryEnergy,'timestamp':polledTime,'batteryStatus':i[2]})

    bms_cur.close()
    processed_db.close()

    return ups_list   


@app.post('/filtered/Upsanalytics/energy_VS_packsoc')
def peak_demand_date(data: dict, db: mysql.connector.connect = Depends(get_emsdb)):
    ups_list = []

    try:
        value = data.get('date')

        if value and isinstance(value, str):
            with db.cursor() as bmscur:
                bmscur.execute(f"SELECT MIN(pack_usable_soc) AS pack_usable_soc,MAX(received_time) AS received_time,MAX(upsbatterystatus) AS upsbatterystatus,MAX(upschargingenergy) AS upschargingenergy,MAX(upsdischargingenergy) AS upsdischargingenergy,HOUR(received_time) AS hr,MINUTE(received_time) AS mint FROM EMS.EMSUPSBattery WHERE DATE(received_time) = '{value}' GROUP BY hr, mint;")
                
                res = bmscur.fetchall()

                for i in res:
                    polledTime = str(i[1])[11:16]
                    if i[2] == 'IDLE':
                        batteryEnergy = 0.01
                    elif i[2] == 'CHG':
                        batteryEnergy = i[3]/100
                    elif i[2] == 'DCHG':
                        batteryEnergy = i[4]/100
                    
                    ups_list.append({'packsoc':i[0],'batteryEnergy':batteryEnergy,'timestamp':polledTime,'batteryStatus':i[2]})
    except mysql.connector.Error as e:
        return JSONResponse(content={"error": ["MySQL connection error",e]}, status_code=500)

    return ups_list


@app.get('/Upsanalytics/current_VS_voltage')
def peak_demand_date(db: mysql.connector.connect = Depends(get_emsdb)):
    ups_list = []
    try:
        processed_db = get_emsdb()
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"MySQL connection error: {str(e)}"})
    
    bms_cur = processed_db.cursor()

    bms_cur.execute("""SELECT max(received_time),max(batteryvoltage),max(batterycurrent),
                                hour(received_time) as hr,minute(received_time) as mint 
                                FROM EMS.EMSUPSbattery
                                where date(received_time) = curdate() 
                                group by hr,mint;""")
    
    res = bms_cur.fetchall()

    for i in res:
        polledTime = str(i[0])[11:16]
        ups_list.append({'polledTime':polledTime,'BatteryVoltage':i[1],'BatteryCurrent':i[2]})

    bms_cur.close()
    processed_db.close()

    return ups_list


@app.post('/filtered/Upsanalytics/current_VS_voltage')
def peak_demand_date(data: dict, db: mysql.connector.connect = Depends(get_emsdb)):
    ups_list = []

    try:
        value = data.get('date')

        if value and isinstance(value, str):
            with db.cursor() as bmscur:
                bmscur.execute(f"SELECT max(received_time),max(batteryvoltage),max(batterycurrent),hour(received_time) as hr,minute(received_time) as mint FROM EMS.EMSUPSbattery where date(received_time) = '{value}' group by hr,mint;")

                res = bmscur.fetchall()

                for i in res:
                    polledTime = str(i[0])[11:16]
                    ups_list.append({'polledTime':polledTime,'BatteryVoltage':i[1],'BatteryCurrent':i[2]})

    except mysql.connector.Error as e:
        return JSONResponse(content={"error": ["MySQL connection error",e]}, status_code=500)

    return ups_list


@app.get('/minWise')
def peak_demand_date(db: mysql.connector.connect = Depends(get_awsdb)):
    min_list = []
    try:
        processed_db = get_awsdb()
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"MySQL connection error: {str(e)}"})
    
    bms_cur = processed_db.cursor()

    bms_cur.execute("SELECT polledTime,wheeled,grid FROM EMS.minWiseData where date(polledTime) = curdate();")

    res = bms_cur.fetchall()

    for i in res:
        polledTime = str(i[0])[11:16]
        min_list.append({'polledTime':polledTime,'wheeledEnergy':i[1],'gridEnergy':i[2]})

    return min_list


@app.post('/filtered/minWise')
def peak_demand_date(data: dict, db: mysql.connector.connect = Depends(get_awsdb)):
    min_list = []

    try:
        value = data.get('date')

        if value and isinstance(value, str):
            with db.cursor() as bmscur:
                bmscur.execute(f"SELECT polledTime,wheeled,grid FROM EMS.minWiseData where date(polledTime) = '{value}'")

                res = bmscur.fetchall()

                for i in res:
                    polledTime = str(i[0])[11:16]
                    min_list.append({'polledTime':polledTime,'wheeledEnergy':i[1],'gridEnergy':i[2]})

    except mysql.connector.Error as e:
        return JSONResponse(content={"error": ["MySQL connection error",e]}, status_code=500)

    return min_list

@app.get('/peakMontly')
def peak_demand_date(db: mysql.connector.connect = Depends(get_awsdb)):
    peak_lis = []
    try:
        processed_db = get_awsdb()
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"MySQL connection error: {str(e)}"})
    
    bms_cur = processed_db.cursor()

    bms_cur.execute("SELECT polledDate,peakDemand FROM EMS.peakMonthly where year(polledDate) = year(curdate());")

    res = bms_cur.fetchall()

    for i in res:
        peak_lis.append({'polledDate':i[0],'peakDemand':i[1]})
    
    return peak_lis


@app.post('/filtered/peakMontly')
def peak_demand_date(data: dict, db: mysql.connector.connect = Depends(get_awsdb)):
    peak_lis = []

    try:
        value = data.get('date')

        if value and isinstance(value, str):
            with db.cursor() as bmscur:
                bmscur.execute(f"SELECT polledDate,peakDemand FROM EMS.peakMonthly where year(polledDate) = '{value}';")

                res = bmscur.fetchall()

                for i in res:
                    peak_lis.append({'polledDate':i[0],'peakDemand':i[1]})

    except mysql.connector.Error as e:
        return JSONResponse(content={"error": ["MySQL connection error",e]}, status_code=500)

    return peak_lis


@app.get('/gridMontly')
def peak_demand_date(db: mysql.connector.connect = Depends(get_awsdb)):
    grid_lis = []
    try:
        processed_db = get_awsdb()
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"MySQL connection error: {str(e)}"})
    
    bms_cur = processed_db.cursor()

    bms_cur.execute("SELECT polledDate,Energy FROM EMS.gridMonthly where year(polledDate) = year(curdate());")

    res = bms_cur.fetchall()

    for i in res:
        grid_lis.append({'polledDate':i[0],'Energy':i[1]})
    
    return grid_lis


@app.post('/filtered/gridMontly')
def peak_demand_date(data: dict, db: mysql.connector.connect = Depends(get_awsdb)):
    grid_lis = []

    try:
        value = data.get('date')

        if value and isinstance(value, str):
            with db.cursor() as bmscur:
                bmscur.execute(f"SELECT polledDate,Energy FROM EMS.gridMonthly where year(polledDate) = '{value}';")

                res = bmscur.fetchall()

                for i in res:
                    grid_lis.append({'polledDate':i[0],'Energy':i[1]})

    except mysql.connector.Error as e:
        return JSONResponse(content={"error": ["MySQL connection error",e]}, status_code=500)

    return grid_lis


@app.get('/BuildingConsumption/BlockWise')
def peak_demand_date(db: mysql.connector.connect = Depends(get_meterdb)):
    BlockWise_Response = []
    try:
        processed_db = get_meterdb()
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"MySQL connection error: {str(e)}"})
   
    bms_cur = processed_db.cursor()

    bms_cur.execute("SELECT timestamp,ABLOCK,BBlock,CBLOCK,DBLOCK,EBLOCK,MLCP,Utility,auditorium FROM meterdata.BlockwiseDaywise where date(timestamp)=curdate();")
   
    res = bms_cur.fetchall()

    polledTime = str(res[0][0])[8:10]+"/"+str(res[0][0])[5:7]+"/"+str(res[0][0])[0:4]

    print(polledTime)

    if res[0][1] != None:
        ablock = round(res[0][1])
    else:
        ablock = 0

    if res[0][2] != None:
        bblock = round(res[0][2])
    else:
        bblock = 0

    if res[0][3] != None:
        cblock = round(res[0][3])
    else:
        cblock = 0

    if res[0][4] != None:
        dblock = round(res[0][4])
    else:
        dblock = 0

    if res[0][5] != None:
        eblock = round(res[0][5])
    else:
        eblock = 0
    
    if res[0][6] != None:
        mlcp = round(res[0][6])
    else:
        mlcp = 0
    
    if res[0][7] != None:
        utility = round(res[0][7])
    else:
        utility = 0
    
    if res[0][8] != None:
        audi = round(res[0][8])
    else:
        audi = 0


    BlockWise_Response.append({'timestamp':polledTime,'ABLOCK':ablock,'BBlock':bblock,'CBLOCK':cblock,'DBLOCK':dblock,'EBLOCK':eblock,'MLCP':mlcp,'Utility':utility,'auditorium':audi})
    bms_cur.close()
    processed_db.close()

    return BlockWise_Response


@app.post('/filtered//BuildingConsumption/BlockWise')
def peak_demand_date(data: dict, db: mysql.connector.connect = Depends(get_awsdb)):
    BlockWise_Response = []

    try:
        value = data.get('date')

        if value and isinstance(value, str):
            with db.cursor() as bmscur:
                bmscur.execute(f"SELECT timestamp,ABLOCK,BBlock,CBLOCK,DBLOCK,EBLOCK,MLCP,Utility,auditorium FROM meterdata.BlockwiseDaywise where date(timestamp)='{value}';")

                res = bmscur.fetchall()

                polledTime = str(res[0][0])[8:10]+"/"+str(res[0][0])[5:7]+"/"+str(res[0][0])[0:4]

                print(polledTime)

                if res[0][1] != None:
                    ablock = round(res[0][1])
                else:
                    ablock = 0

                if res[0][2] != None:
                    bblock = round(res[0][2])
                else:
                    bblock = 0

                if res[0][3] != None:
                    cblock = round(res[0][3])
                else:
                    cblock = 0

                if res[0][4] != None:
                    dblock = round(res[0][4])
                else:
                    dblock = 0

                if res[0][5] != None:
                    eblock = round(res[0][5])
                else:
                    eblock = 0
                
                if res[0][6] != None:
                    mlcp = round(res[0][6])
                else:
                    mlcp = 0
                
                if res[0][7] != None:
                    utility = round(res[0][7])
                else:
                    utility = 0
                
                if res[0][8] != None:
                    audi = round(res[0][8])
                else:
                    audi = 0


                BlockWise_Response.append({'timestamp':polledTime,'ABLOCK':ablock,'BBlock':bblock,'CBLOCK':cblock,'DBLOCK':dblock,'EBLOCK':eblock,'MLCP':mlcp,'Utility':utility,'auditorium':audi})
                bmscur.close()
                db.close()

    except mysql.connector.Error as e:
        return JSONResponse(content={"error": ["MySQL connection error",e]}, status_code=500)

    return BlockWise_Response

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5003)




