import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mysql.connector
import time
from datetime import datetime

html_head = """<head>
            <style>
                .container {
                display: flex;
                align-items: center;
                justify-content: center
              }
           
              img {
                max-width: 75%;
                max-height:50%;
            }
           
              .text {
                font-size: 25px;
                padding-left: 20px;
              }
              a:link, a:visited {
                background-color: #8bc9ab;
                color: black;
                padding: 12px 25px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
              }
              td {
                font-size: 19px
              }
              a:hover, a:active {
                background-color: #4c727d;
              }
              hr {
                border-color: green;
              }
                </style>  
        </head>"""
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'emsteamrp@gmail.com'
smtp_password = 'eebpnvgyfzzdtitb'

sender = 'emsteamrp@gmail.com'
recipient = ['arun.kumar@tenet.res.in']
           
def peaklev1():
    lis = []
    while True:
        ubuntudb = mysql.connector.connect(
                host="121.242.232.211",
                user="emsroot",
                password="22@teneT",
                database='EMS',
                port=3306
                )
   
        try:
            emscur = ubuntudb.cursor()
        except Exception as ex:
            print(ex)
            time.sleep(10)
            continue

        emscur.execute('select totalApparentPower2 from bmsunprocessed_prodv13.hvacSchneider7230Polling WHERE polledTime >= CURDATE() order by polledTime desc limit 1')
   
        res = emscur.fetchall()
        #print(res)

        date = datetime.now()
        
        try:
            peak = max(res)[0]
        except:
            peak = 0
        
        date = str(date)[0:10]
        polledtime = str(date)[11:16]

        try:
            if peak != None and peak != None:
                val = peak
            else:
                val = 0
        except IndexError:
            continue
        lis.append((val,polledtime))
        vallis = []
        print('peak l1',val)
        if len(lis) == 60:
            for i in lis:
                if i !=None:
                    vallis.append(i[0])
            print(lis)
            lis =[]
            if max(vallis) >= 3900 and max(vallis) < 4200:
                message = MIMEMultipart('alternative')
                message['Subject'] = 'EMS ALERT -  Peak Demand Limit-level 1 breach'
                message['From'] = sender
                message['To'] = 'energyteam@respark.iitm.ac.in'

                html_content = html_head + f"""
                <body style="background-color:white;">
                    <div class="container">
                        <div class="image">
                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                        </div>
                        <div class="text">
                            <h3>  EMS Alert</h3>
                        </div>
                    </div>
                    <hr>
                    <br>
                    <center>
                        <table>
                            <tr>
                            <td><b>Alert<b></td>
                            <td>Peak Demand Limt - Level 1 Breach</td>
                            </tr>
                            <tr>
                                <td><b>Severity<b></td>
                                <td>Medium</td>
                            </tr>
                            <tr>
                            <td><b>Limit<b></td>
                                <td> {max(vallis)} KVA</td>
                            </tr>
                            <tr>
                                <td><b>Date<b></td>
                                <td>{date}</td>
                            </tr>
                            <tr>
                                <td><b>Time<b></td>
                                <td>{polledtime}</td>
                            </tr>
                            <tr>
                                <td><b>System<b></td>
                                <td>Building Load</td>
                            </tr>
                        </table>
                        <center><a href="http://43.205.196.66:3000/peakgraph" target="_blank">View Dashboard</a></center>
                        <br>
                        <hr>
                        <p>EMS team</p></center>
                </body>"""

                html_part = MIMEText(html_content, 'html')

                message.attach(html_part)

                sql = 'INSERT INTO alertLogs(alerttime,alert,limitvalue,systemName,severity,action) VALUES(%s,%s,%s,%s,%s,%s)'
                val = (res[0][1],'Peak Demand Limt - Level 1 Breach',max(vallis),'Building Load','Medium','Mail sent')
                emscur.execute(sql,val)
                print("Peakdemand alert saved")
                ubuntudb.commit()
           
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.sendmail(sender, recipient, message.as_string())
                    print('L1 - Email sent successfully!')
        emscur.close()  
        time.sleep(50)
while True:
    peaklev1()
    time.sleep(10)
