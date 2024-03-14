import mysql.connector
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from PIL import Image
import time
from redmail import EmailSender
import matplotlib.pyplot as plt
#from IPython.display import display, HTML  
import time
from datetime import timedelta

def report():
    while True:
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(current_time[0:5])
        #if current_time[0:5]=="10:05":
        if 1 == 1:

    # Get today's date
            current_date = date.today()
            
            yesterday = current_date - timedelta(days = 1)
            
            formatted_date = yesterday.strftime("%d %B %Y")

            datelist = formatted_date.split(' ')
#print(datelist)
            if int(formatted_date[0]) == 0:
                dateyes = datelist[1]+','+' '+datelist[0][1:]+' '+datelist[2]
            else:
                dateyes = datelist[1]+','+' '+datelist[0]+' '+datelist[2]
            
            print(dateyes)

            # head =

            emsdb = mysql.connector.connect(
                host="43.205.196.66",
                user="emsroot",
                password="22@teneT",
                database='EMS',
                port=3307
            )

            meterdb = mysql.connector.connect(
                host="43.205.196.66",
                user="emsroot",
                password="22@teneT",
                database='meterdata',
                port=3307
            )
           
            time_list = ["00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23"]
           
            emscur = emsdb.cursor()
           
            emscur.execute("SELECT polledTime,Energy FROM BMSgridhourly where date(polledTime) = DATE_SUB(curdate(), INTERVAL 1 DAY)")

            grid = emscur.fetchall()

            grid_dict = {}

            def Summarize(polledTime,Energy):
                hour = str(polledTime)[11:13]
                # print(hour,Energy)
               
                if hour in grid_dict.keys():
                    grid_dict[hour] += Energy  
                else:
                    grid_dict[hour] = Energy
           
            for i in grid:
                Summarize(i[0],round(i[1]))
           
            for i in time_list:
                if i not in grid_dict.keys():
                    grid_dict[i] = 0

            grid_keys = list(grid_dict.keys())

            grid_time = [eval(i[1]) if i[0] == '0' else eval(i) for i in grid_keys]

            grid_time.sort()

            # print(grid_time)

            grid_keys = ['0'+str(i) if len(str(i)) == 1 else str(i) for i in grid_time]

            # print(grid_keys)
            
            grid_dict = {i: grid_dict[i] for i in grid_keys}

            # print(grid_dict)

            data = [['Hour','Grid','Rooftop','Wheeledin','Peak demand','Disel','RE','cgrid','excess RE','Min Powerfactor','Avg Powerfactor']]
       
            # for i in hour_dict.keys():
            #     data.append([i,round(hour_dict[i],0)])
           
            for i in grid_dict.keys():
                energy_value = round(grid_dict[i], 0) if i in grid_dict else 0
                data.append([i, energy_value])

            emscur.execute("""SELECT energy,polledTime FROM EMS.roofTopHour where date(polledTime) = DATE_SUB(curdate(), INTERVAL 1 DAY);""")

            result = emscur.fetchall()

            roofhr = {}

            def HourSummmarize(Energy,Time):
                hour=str(Time)[11:13]
                if hour not in roofhr.keys():
                    roofhr[hour] = Energy  

            for i in result:
                HourSummmarize(i[0],i[1])
           
            for i in time_list:
                if i not in roofhr.keys():
                    roofhr[i] = 0
            for i in data[1:7]:
                i.append(0)
            for i in data[7:20]:
                if i[0] in roofhr.keys():
                    energy_value = round(roofhr[i[0]]) if i[0] in roofhr.keys() else "-"
                    i.append(energy_value)
            for i in data[20:]:
                i.append(0)
            
                

            emscur = emsdb.cursor()

            emscur.execute("SELECT polledTime,Energy FROM WheeledHourly where date(polledTime) = DATE_SUB(curdate(), INTERVAL 1 DAY)")

            wheeled_res = emscur.fetchall()

            hourly_wheeled= {}
            def Hourlywheeled(polledTime,Energy):
                hour = str(polledTime)[11:13]
                # print(hour,Energy)
               
                if hour in hourly_wheeled.keys():
                    hourly_wheeled[hour] += Energy  
                else:
                    hourly_wheeled[hour] = Energy
           
            for i in wheeled_res:
                Hourlywheeled(i[0],i[1])
           
            for i in data[1:]:
                if i[0] in hourly_wheeled.keys():
                    # energy_value = round(hourly_wheeled[i[0]],0) if i in hourly_wheeled else 0
                    i.append(round(hourly_wheeled[i[0]],0))
                    # i.append(round(hourly_wheeled[i[0]]-(hourly_wheeled[i[0]]*0.0306),0))
                else:
                    i.append(0.0)
           
           
            emscur.execute("SELECT peakdemand,polledTime FROM EMS.peakdemandHourly where date(polledTime) = date_sub(curdate(),interval 1 day);")

            peakres = emscur.fetchall()

            peak_dict = {}
            def peakHourly(peak,polledTime):
               hour = str(polledTime)[11:13]
               if hour not in peak_dict.keys():
                   peak_dict[hour] = peak

            for i in peakres:
               peakHourly(i[0],i[1])
               
            for i in time_list:
                if i not in peak_dict.keys():
                    peak_dict[i] = 0

# for i in peak_dict.keys():
#    res = [i for i in peak_dict[i] if i is not None]
#    print(i,max(res))

            for i in data:
               if i[0] in peak_dict.keys():
                  #res = [i for i in peak_dict[i[0]] if i is not None]
                  i.append(round(float(peak_dict[i[0]]),2))

            # print(data[1][1])
           
            diselcur = meterdb.cursor()

            diselcur.execute("SELECT Energy,polledTime FROM EMS.DGHourly where date(polledTime) = date_sub(curdate(),interval 1 day);")

            diselres = diselcur.fetchall()

            disel_hour = {}

            def HourlyDisel(Energy,Time):
                hour = str(Time)[11:13]
                if hour in disel_hour.keys():
                    if Energy !=None:
                        disel_hour[hour] += Energy
                else:
                    if Energy !=None:
                        disel_hour[hour] = Energy
                   
            for i in diselres:
                # print(i[0],i[1])
                HourlyDisel(i[0],i[1])

            for i in data:
                try:
                    val = type(int((i[0])))
                except ValueError:
                    continue
           
                if i[0] in disel_hour.keys():
                    if disel_hour[i[0]] >= 0:
                       i.append(int(disel_hour[i[0]]))
                    else:
                       i.append(0)
                elif val == int:
                    i.append(0)

           
            # for i in data:
            #     print(i)
       
            for i in range(1,len(data)):
                # print(data[i])
                data[i].append(round((data[i][2]+data[i][3])/(data[i][1]+data[i][2]+data[i][5]),2))
               
            for i in range(1,len(data)):
                if data[i][1] > data[i][3]:
                    data[i].append(data[i][1]-data[i][3])  
                else:
                    data[i].append(0)    
           
            for i in range(1,len(data)):
                if data[i][6] > 1:
                    data[i].append(round(data[i][6] -1,2))
                    data[i][6] = 1
                else:
                    data[i].append(0)
                    
           
            powerfact = emsdb.cursor()

            powerfact.execute("select polledTime,avgpowerfactor,minpowerfactor from schneider7230processed where date(polledTime) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)")

            powerfactor = powerfact.fetchall()

            mfacthr = {}
            afacthr = {}

            def minFactor(hour,power):
                if power !=None:
                    mfacthr[hour] = power

            def avgFactor(hour,power):
                if power !=None:
                    afacthr[hour] = power

            for i in powerfactor:
                minFactor(str(i[0])[11:13],i[2])
                avgFactor(str(i[0])[11:13],i[1])
            
            for i in time_list:
                if i not in mfacthr.keys():
                    mfacthr[i] = None
                
            for i in time_list:
                if i not in afacthr.keys():
                    afacthr[i] = None
                 
            for i in data:
                if i[0] in  mfacthr.keys():
                    i.append(mfacthr[i[0]])

                if i[0] in  afacthr.keys():
                    i.append(afacthr[i[0]])   
           
            for i in data:
                print(i)
       
            df = pd.DataFrame(data[1:], columns =data[0], dtype = float)

            total_grid = abs(sum(grid_dict.values()) - sum(hourly_wheeled.values()))
           
            print(df)
            total_re = round((round(sum(roofhr.values()))+round(sum(hourly_wheeled.values())))/(round(sum(grid_dict.values()))+round(sum(roofhr.values()))+round(sum(disel_hour.values())))*100,1)
            print("TNEB Grid",total_grid)
            print("Roof Top Solar",sum(roofhr.values()))
            print("Wheeled-in Solar",sum(hourly_wheeled.values()))
            print("DG",sum(disel_hour.values()))
            print("Peak Deamnd(max)",max(peak_dict.values()))
            print("Total RE",total_re)
       
            df['Hour'] = df['Hour'].astype(int)
            df['cgrid'] = df['cgrid'].astype(float)
            df['Rooftop'] = df['Rooftop'].astype(float)
            df['Wheeledin'] = df['Wheeledin'].astype(float)
            df['Peak demand'] = df['Peak demand'].astype(float)
           
            fig, ax = plt.subplots(figsize=(12, 6.5))
            df.plot(x='Hour', y='cgrid', kind='line', color='#1d3ee0', ax=ax)
            df.plot(x='Hour', y='Rooftop', kind='line', color='#ab3a3a', ax=ax)
            df.plot(x='Hour', y='Wheeledin', kind='line', color='#1de09c', ax=ax)
            df.plot(x='Hour', y='Peak demand', kind='line', color='#af1de0', ax=ax)
           
            ax.set_xlabel('Hour')
            ax.set_ylabel('Energy (kWh)')
           
       
            # XPypXz2xN6VMP57ijHLt
       
       
            # datum = [grid,roof,wheel,peak]
            current_time
           
            # print(url)
       
            email = EmailSender(host="smtp.gmail.com", port=587,username='emsteamrp@gmail.com',password='eebpnvgyfzzdtitb')

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
                            <img class="img" src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
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
                        <td bgcolor="#c99db6"><bold>DG (kWh)</bold></td>
                        <td bgcolor="#c99db6"><bold>Peak Demand Max (kVA)</bold></td>
                        <td bgcolor="#c99db6"><bold>Total RE (%)</bold></td>
                        </tr>
                        <tr>
                        <td>{round(sum(grid_dict.values()))}</td>
                        <td>{round(sum(roofhr.values()))}</td>
                        <td>{round(sum(hourly_wheeled.values()))}</td>
                        <td>{round(sum(disel_hour.values()))}</td>
                        <td>{max(peak_dict.values())}</td>
                        <td>{total_re}</td>
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
                                <th>Wheeled in solar(kWh)</th>
                                <th>Rooftop solar(kWh)</th>
                                <th>Min Powerfactor</th>
                                <th>Avg Powerfactor</th>
                                <th>RE %</th>
                                <th>Excess RE%</th>
                            </tr>
                            <tr>
                                <td>0</td>
                                <td>{int(data[1][4])}</td>
                                <td>{int(data[1][7])}</td>
                                <td>{int(data[1][5])}</td>
                                <td>{int(data[1][3])}</td>
                                <td>{int(data[1][2])}</td>
                                <td>{data[1][9]}</td>
                                <td>{data[1][10]}</td>
                                <td>{round(data[1][6]*100)}</td>
                                <td>{round(data[1][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>1</td>
                                <td>{int(data[2][4])}</td>
                                <td>{int(data[2][7])}</td>
                                <td>{int(data[2][5])}</td>
                                <td>{int(data[2][3])}</td>
                                <td>{int(data[2][2])}</td>
                                <td>{data[2][9]}</td>
                                <td>{data[2][10]}</td>
                                <td>{round(data[2][6]*100)}</td>
                                <td>{round(data[2][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>2</td>
                                <td>{int(data[3][4])}</td>
                                <td>{int(data[3][7])}</td>
                                <td>{int(data[3][5])}</td>
                                <td>{int(data[3][3])}</td>
                                <td>{int(data[3][2])}</td>
                                <td>{data[3][9]}</td>
                                <td>{data[3][10]}</td>
                                <td>{round(data[3][6]*100)}</td>
                                <td>{round(data[3][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>3</td>
                                <td>{int(data[4][4])}</td>
                                <td>{int(data[4][7])}</td>
                                <td>{int(data[4][5])}</td>
                                <td>{int(data[4][3])}</td>
                                <td>{int(data[4][2])}</td>
                                <td>{data[4][9]}</td>
                                <td>{data[4][10]}</td>
                                <td>{round(data[4][6]*100)}</td>
                                <td>{round(data[4][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>4</td>
                                <td>{int(data[5][4])}</td>
                                <td>{int(data[5][7])}</td>
                                <td>{int(data[5][5])}</td>
                                <td>{int(data[5][3])}</td>
                                <td>{int(data[5][2])}</td>
                                <td>{data[5][9]}</td>
                                <td>{data[5][10]}</td>
                                <td>{round(data[5][6]*100)}</td>
                                <td>{round(data[5][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>5</td>
                                <td>{int(data[6][4])}</td>
                                <td>{int(data[6][7])}</td>
                                <td>{int(data[6][5])}</td>
                                <td>{int(data[6][3])}</td>
                                <td>{int(data[6][2])}</td>
                                <td>{data[6][9]}</td>
                                <td>{data[6][10]}</td>
                                <td>{round(data[6][6]*100)}</td>
                                <td>{round(data[6][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>6</td>
                                <td>{int(data[7][4])}</td>
                                <td>{int(data[7][7])}</td>
                                <td>{int(data[7][5])}</td>
                                <td>{int(data[7][3])}</td>
                                <td>{int(data[7][2])}</td>
                                <td>{data[7][9]}</td>
                                <td>{data[7][10]}</td>
                                <td>{round(data[7][6]*100)}</td>
                                <td>{round(data[7][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>7</td>
                                <td>{int(data[8][4])}</td>
                                <td>{int(data[8][7])}</td>
                                <td>{int(data[8][5])}</td>
                                <td>{int(data[8][3])}</td>
                                <td>{int(data[8][2])}</td>
                                <td>{data[8][9]}</td>
                                <td>{data[8][10]}</td>
                                <td>{round(data[8][6]*100)}</td>
                                <td>{round(data[8][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>8</td>
                                <td>{int(data[9][4])}</td>
                                <td>{int(data[9][7])}</td>
                                <td>{int(data[9][5])}</td>
                                <td>{int(data[9][3])}</td>
                                <td>{int(data[9][2])}</td>
                                <td>{data[9][9]}</td>
                                <td>{data[9][10]}</td>
                                <td>{round(data[9][6]*100)}</td>
                                <td>{round(data[9][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>9</td>
                                <td>{int(data[10][4])}</td>
                                <td>{int(data[10][7])}</td>
                                <td>{int(data[10][5])}</td>
                                <td>{int(data[10][3])}</td>
                                <td>{int(data[10][2])}</td>
                                <td>{data[10][9]}</td>
                                <td>{data[10][10]}</td>
                                <td>{round(data[10][6]*100)}</td>
                                <td>{round(data[10][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>10</td>
                                <td>{int(data[11][4])}</td>
                                <td>{int(data[11][7])}</td>
                                <td>{int(data[11][5])}</td>
                                <td>{int(data[11][3])}</td>
                                <td>{int(data[11][2])}</td>
                                <td>{data[11][9]}</td>
                                <td>{data[11][10]}</td>
                                <td>{round(data[11][6]*100)}</td>
                                <td>{round(data[11][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>11</td>
                                <td>{int(data[12][4])}</td>
                                <td>{int(data[12][7])}</td>
                                <td>{int(data[12][5])}</td>
                                <td>{int(data[12][3])}</td>
                                <td>{int(data[12][2])}</td>
                                <td>{data[12][9]}</td>
                                <td>{data[12][10]}</td>
                                <td>{round(data[12][6]*100)}</td>
                                <td>{round(data[12][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>12</td>
                                <td>{int(data[13][4])}</td>
                                <td>{int(data[13][7])}</td>
                                <td>{int(data[13][5])}</td>
                                <td>{int(data[13][3])}</td>
                                <td>{int(data[13][2])}</td>
                                <td>{data[13][9]}</td>
                                <td>{data[13][10]}</td>
                                <td>{round(data[13][6]*100)}</td>
                                <td>{round(data[13][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>13</td>
                                <td>{int(data[14][4])}</td>
                                <td>{int(data[14][7])}</td>
                                <td>{int(data[14][5])}</td>
                                <td>{int(data[14][3])}</td>
                                <td>{int(data[14][2])}</td>
                                <td>{data[14][9]}</td>
                                <td>{data[14][10]}</td>
                                <td>{round(data[14][6]*100)}</td>
                                <td>{round(data[14][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>14</td>
                                <td>{int(data[15][4])}</td>
                                <td>{int(data[15][7])}</td>
                                <td>{int(data[15][5])}</td>
                                <td>{int(data[15][3])}</td>
                                <td>{int(data[15][2])}</td>
                                <td>{data[15][9]}</td>
                                <td>{data[15][10]}</td>
                                <td>{round(data[15][6]*100)}</td>
                                <td>{round(data[15][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>15</td>
                                <td>{int(data[16][4])}</td>
                                <td>{int(data[16][7])}</td>
                                <td>{int(data[16][5])}</td>
                                <td>{int(data[16][3])}</td>
                                <td>{int(data[16][2])}</td>
                                <td>{data[16][9]}</td>
                                <td>{data[16][10]}</td>
                                <td>{round(data[16][6]*100)}</td>
                                <td>{round(data[16][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>16</td>
                                <td>{int(data[17][4])}</td>
                                <td>{int(data[17][7])}</td>
                                <td>{int(data[17][5])}</td>
                                <td>{int(data[17][3])}</td>
                                <td>{int(data[17][2])}</td>
                                <td>{data[17][9]}</td>
                                <td>{data[17][10]}</td>
                                <td>{round(data[17][6]*100)}</td>
                                <td>{round(data[17][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>17</td>
                                <td>{int(data[18][4])}</td>
                                <td>{int(data[18][7])}</td>
                                <td>{int(data[18][5])}</td>
                                <td>{int(data[18][3])}</td>
                                <td>{int(data[18][2])}</td>
                                <td>{data[18][9]}</td>
                                <td>{data[18][10]}</td>
                                <td>{round(data[18][6]*100)}</td>
                                <td>{round(data[18][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>18</td>
                                <td>{int(data[19][4])}</td>
                                <td>{int(data[19][7])}</td>
                                <td>{int(data[19][5])}</td>
                                <td>{int(data[19][3])}</td>
                                <td>{int(data[19][2])}</td>
                                <td>{data[19][9]}</td>
                                <td>{data[19][10]}</td>
                                <td>{round(data[19][6]*100)}</td>
                                <td>{round(data[19][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>19</td>
                                <td>{int(data[20][4])}</td>
                                <td>{int(data[20][7])}</td>
                                <td>{int(data[20][5])}</td>
                                <td>{int(data[20][3])}</td>
                                <td>{int(data[20][2])}</td>
                                <td>{data[20][9]}</td>
                                <td>{data[20][10]}</td>
                                <td>{round(data[20][6]*100)}</td>
                                <td>{round(data[20][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>20</td>
                                <td>{int(data[21][4])}</td>
                                <td>{int(data[21][7])}</td>
                                <td>{int(data[21][5])}</td>
                                <td>{int(data[21][3])}</td>
                                <td>{int(data[21][2])}</td>
                                <td>{data[21][9]}</td>
                                <td>{data[21][10]}</td>
                                <td>{round(data[21][6]*100)}</td>
                                <td>{round(data[21][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>21</td>
                                <td>{int(data[22][4])}</td>
                                <td>{int(data[22][7])}</td>
                                <td>{int(data[22][5])}</td>
                                <td>{int(data[22][3])}</td>
                                <td>{int(data[22][2])}</td>
                                <td>{data[22][9]}</td>
                                <td>{data[22][10]}</td>
                                <td>{round(data[22][6]*100)}</td>
                                <td>{round(data[22][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>22</td>
                                <td>{int(data[23][4])}</td>
                                <td>{int(data[23][7])}</td>
                                <td>{int(data[23][5])}</td>
                                <td>{int(data[23][3])}</td>
                                <td>{int(data[23][2])}</td>
                                <td>{data[23][9]}</td>
                                <td>{data[23][10]}</td>
                                <td>{round(data[23][6]*100)}</td>
                                <td>{round(data[23][8]*100)}</td>
                            </tr>
                            <tr>
                                <td>23</td>
                                <td>{int(data[24][4])}</td>
                                <td>{int(data[24][7])}</td>
                                <td>{int(data[24][5])}</td>
                                <td>{int(data[24][3])}</td>
                                <td>{int(data[24][2])}</td>
                                <td>{data[24][9]}</td>
                                <td>{data[24][10]}</td>
                                <td>{round(data[24][6]*100)}</td>
                                <td>{round(data[24][8]*100)}</td>
                            </tr>
                        </table>'''
            pic =  '''<center>{{ embedded_plot }} </center>'''
            footer = '''<br>
                        <hr>
                        <p>EMS Team></p>'''
           
            template = html+body+pic+footer
           
            with email:
                email.send(
                subject="Daily summary report",
                sender="emsteamrp@gmail.com",
                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                receivers=["arun.kumar@tenet.res.in"],

                # A plot in body
                html=template,
                body_images={
                    "embedded_plot": fig
                })
            print("Mail send sucessfully")
        time.sleep(60)
       
report()
