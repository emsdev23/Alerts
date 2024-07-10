import mysql.connector
import time
from datetime import date,timedelta
import pandas as pd
import matplotlib.pyplot as plt
from redmail import EmailSender

while True:
    image_link = "https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844759/iitmrp_logo?e=2147483647&v=beta&t=9HZWEv1IVlDMW-9PQc8dDacfDsnKpdBrA0J7NZokEgc"

    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(current_time[0:5])
    #if current_time[0:5]=="10:05":
    if 1 == 1:

        current_date = date.today()
        yesterday = current_date - timedelta(days = 1)
        formatted_date = yesterday.strftime("%d %B %Y")
        datelist = formatted_date.split(' ')
        
        if int(formatted_date[0]) == 0:
            dateyes = datelist[1]+','+' '+datelist[0][1:]+' '+datelist[2]
        else:
            dateyes = datelist[1]+','+' '+datelist[0]+' '+datelist[2]
        print(dateyes)
        
        awsdb = mysql.connector.connect(
                    host="3.111.70.53",
                    user="emsroot",
                    password="22@teneT",
                    database='EMS',
                    port=3307
                )
        awscur = awsdb.cursor()

        awscur.execute("""SELECT polledTime,bmsgrid,rooftopEnergy,wheeledinEnergy,wheeledinEnergy2,peakDemand,diesel,windEnergy
                            FROM EMS.buildingConsumption where date(polledTime) = date_sub(curdate(), interval 1 day);""")
        
        res = awscur.fetchall()

        time_list = ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23"]

        dictVal = {}
        data = [['Hour','Grid','Rooftop','Wheeledin','Wheeledin2','Peak demand','Disel','Wind','RE','excess RE','Avg Powerfactor','Min Powerfactor']]

        for i in res:
            polledTime = int(str(i[0])[11:13])
            if i[1] == None:
                grid = None
                i[1] = 0
            else:
                grid = i[1]

            if i[2] == None:
                rf = 0
                roof = None
            else:
                roof = round(i[2])
                rf = i[2]

            if i[3] == None:
                wheel = None
                wh = 0
            else:
                wheel = i[3]
                wh = i[3]

            if i[4] == None:
                wheel2 = None
                wh2 = 0
            else:
                wheel2 = i[4]
                wh2 = i[4]

            if i[7] == 0:
                wd = 0
            else:
                wd = i[7]

            if grid != None:
                grid = i[1] - (wh+wh2+wd)
                if grid <= 0:
                    grid = 0

            if polledTime < 6 or polledTime > 18:
                if roof != None:
                    roof = 0
                else:
                    roof = None

                if wheel != None:
                    wheel = 0
                else:
                    wheel = None

                if wheel2 != None:
                    wheel2 = 0
                else:
                    wheel2 = None
            
            re = round(((rf+wh+wh2+wd)/(i[1]+i[3]+rf))*100)
            ex = 0
            if re > 100:
                ex = re - 100
                re = 100

            polledTime = str(polledTime)
            dictVal[polledTime] = [polledTime,round(grid),round(roof),round(wheel),round(wheel2),round(i[5]),round(i[6]),round(i[7]),re,ex]
            
        
        dictLi = list(dictVal.keys())

        for time_point in time_list:
            if time_point not in dictVal:
                dictVal[time_point] = [None, None, None, None, None, None, None, None, None]

        awscur.execute("SELECT polledTime,avgpowerfactor,minpowerfactor FROM EMS.schneider7230processed where date(polledTime) = date_sub(curdate(), interval 1 day);")

        res1 = awscur.fetchall()

        for i in res1:
            polledTime = str(int(str(i[0])[11:13]))

            if polledTime in dictVal.keys():
                dictVal[polledTime].append(i[1])
                dictVal[polledTime].append(i[2])
        
        valLi = list(dictVal.values())

        for i in valLi:
            data.append(i)
        
        df = pd.DataFrame(data[1:], columns =data[0], dtype = float)

        print(df)

        gridTotal = df['Grid'].sum()
        wheeledTotal = df['Wheeledin'].sum()
        wheeled2Total = df['Wheeledin2'].sum()
        rooftopTotal = df['Rooftop'].sum()
        windTotal = df['Wind'].sum()
        dieselTotal = df['Disel'].sum()
        peakMax = df['Peak demand'].max()

        print("Grid total",gridTotal)
        print("Wheeled total",wheeledTotal)
        print("Wheeled2 total",wheeled2Total)
        print("Rooftop total",rooftopTotal)
        print("Disel total",dieselTotal)
        print("Wind total",windTotal)

        totalRE = round(((wheeledTotal+wheeledTotal+windTotal+rooftopTotal)/(gridTotal+dieselTotal+wheeledTotal+wheeledTotal+windTotal+rooftopTotal))*100)
        excessRE = 0
        if totalRE > 100:
            totalRE =  100
            excessRE = totalRE - 100
        print("Total RE",totalRE)
        print("Excess RE",excessRE)

        df['Hour'] = df['Hour'].astype(int)
        df['Grid'] = df['Grid'].astype(float)
        df['Rooftop'] = df['Rooftop'].astype(float)
        df['Wheeledin'] = df['Wheeledin'].astype(float)
        df['Wheeledin2'] = df['Wheeledin2'].astype(float)
        df['Wind'] = df['Wind'].astype(float)
        df['Peak demand'] = df['Peak demand'].astype(float)

        fig, ax = plt.subplots(figsize=(12, 6.5))
        df.plot(x='Hour', y='Grid', kind='line', color='#f54242', ax=ax)
        df.plot(x='Hour', y='Rooftop', kind='line', color='#f59342', ax=ax)
        df.plot(x='Hour', y='Wheeledin', kind='line', color='#1de09c', ax=ax)
        df.plot(x='Hour', y='Wheeledin2', kind='line', color='#f2f542', ax=ax)
        df.plot(x='Hour', y='Wind', kind='line', color='#1d3ee0', ax=ax)
        df.plot(x='Hour', y='Peak demand', kind='line', color='#af1de0', ax=ax)
        
        ax.set_xlabel('Hour')
        ax.set_ylabel('Energy (kWh)')

        email = EmailSender(host="smtp.gmail.com", port=587,username='emsteamrp@gmail.com',password='eebpnvgyfzzdtitb')

        table = """"""

        for i in data[1:]:
            table += f"""
                        <tr>
                        <td>{i[0]}</td>
                        <td>{i[5]}</td>
                        <td>{i[1]}</td>
                        <td>{i[6]}</td>
                        <td>{i[3]}</td>
                        <td>{i[4]}</td>
                        <td>{i[2]}</td>
                        <td>{i[7]}</td>
                        <td>{i[11]}</td>
                        <td>{i[10]}</td>
                        <td>{i[8]}</td>
                        <td>{i[9]}</td>
                        </tr>"""
        html= '''
            <head>
            <style>
                html, body {
                    height: 100%;
                    margin: 0;
                    padding: 20px;
                }

                body {
                    background-color:white;
                }
                .container {
                    display: flex;
                    align-items: center;
                    justify-content: center
                }
                .text {
                    font-size: 25px;
                    padding-left: 20px;
                }
                hr {
                    border-color: green;
                }
                td{
                    font-size: 17px;
                    text-align: center;
                }
                th{
                    font-family:'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
                    font-size: 20px;
                    color: aliceblue;
                    background-color: #2092e8;
                    text-align: center;
                }
                p{
                    font-size: 23px;
                    color: #306bc9;
                }
            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.min.js"></script>
            </head>
            ''' 
        
        body =  f'''
                    <body>
                        <div class="container">
                            <div class="image">
                                <img class="img" src={image_link} height="100px" width="100px">
                            </div>
                            <div class="text">
                                <h3>  EMS - Daily Summary Report</h3>
                            </div>
                            </div>
                            <hr>
                            <center><p>{dateyes}</p></center>
                            <center>
                            <h3>Highlights of the Day</h3>
                            <table border=1px>
                            <tr>
                            <td bgcolor="#c99db6"><bold>TNEB Grid (kWh)</bold></td>
                            <td bgcolor="#c99db6"><bold>Rooftop Solar (kWh)</bold></td>
                            <td bgcolor="#c99db6"><bold>Wheeled-in Solar (kWh)</bold></td>
                            <td bgcolor="#c99db6"><bold>Wheeled-in Solar 2 (kWh)</bold></td>
                            <td bgcolor="#c99db6"><bold>Wind (kWh)</bold></td>
                            <td bgcolor="#c99db6"><bold>DG (kWh)</bold></td>
                            <td bgcolor="#c99db6"><bold>Peak Demand Max (kVA)</bold></td>
                            <td bgcolor="#c99db6"><bold>Total RE (%)</bold></td>
                            </tr>
                            <tr>
                            <td>{round(gridTotal)}</td>
                            <td>{round(rooftopTotal)}</td>
                            <td>{round(wheeledTotal)}</td>
                            <td>{round(wheeled2Total)}</td>
                            <td>{round(windTotal)}</td>
                            <td>{round(dieselTotal)}</td>
                            <td>{peakMax}</td>
                            <td>{totalRE}</td>
                            </tr>
                            </table>
                            </center>
                            <br>
                            <center>
                            <table border=1px>
                                <tr>
                                    <th>Hour</th>
                                    <th>Peak Demand (kVA) </th>
                                    <th>TNEB Grid (kWh)</th>
                                    <th>DG (kWh)</th>
                                    <th>Wheeled in solar (kWh)</th>
                                    <th>Wheeled in solar-2 (kWh)</th>
                                    <th>Rooftop solar (kWh)</th>
                                    <th>Wind (kWh)</th>
                                    <th>Min Powerfactor</th>
                                    <th>Avg Powerfactor</th>
                                    <th>RE %</th>
                                    <th>Excess RE%</th>
                                </tr>
                                '''
        table = table + '''
                        </center>
                        </table>
                        '''
        pic =  '''<center>{{ embedded_plot }} </center>'''
        footer = '''<br>
                    <hr>
                    <p>EMS Team</p>'''
        
        template = html+body+table+pic+footer

        with email:
            email.send(
            subject="Daily summary report",
            sender="emsteamrp@gmail.com",
            #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
            receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

            # A plot in body
            html=template,
            body_images={
                "embedded_plot": fig
            })
        print("Mail send sucessfully")

        time.sleep(60)