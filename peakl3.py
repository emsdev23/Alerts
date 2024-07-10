import mysql.connector
import time
from redmail import EmailSender

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
recipient = 'energyteam@respark.iitm.ac.in'
# 'energyteam@respark.iitm.ac.in',
   
def peaklev3():
    while True:           
        ubuntudb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
            
        emscur = ubuntudb.cursor()

        emscur.execute('select totalApparentPower2,polledTime from bmsunprocessed_prodv13.hvacSchneider7230Polling WHERE polledTime >= CURDATE() order by polledTime desc limit 4')

        res = emscur.fetchall()
        value = None
           
        val = []
        try:
            if len(res) > 0:
                for i in res:
                    if i[0] != None:
                        val.append(i[0])
            value = max(val)
            polledtime = str(res[0][1])[11:]
            date = str(res[0][1])[0:10]
        except IndexError:
            continue

        email = EmailSender(host="smtp.gmail.com", port=587,username='emsteamrp@gmail.com',password='eebpnvgyfzzdtitb')
        
        if value != None:
            print('peak l3',value)
            if value>=4400:
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
                            <td>Peak Demand Limt - Level 3 Breach</td>
                            </tr>
                            <tr>
                                <td><b>Severity<b></td>
                                <td>High</td>
                            </tr>
                            <tr>
                            <td><b>Limit<b></td>
                                <td>{value} KVA</td>
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
                        <center><a href="https://ems.tre100.in/PeakDemandAnalysis" target="_blank">View Dashboard</a></center>
                        <br>
                        <hr>
                        <p>EMS team</p></center>
                </body>"""
           
                sql = 'INSERT INTO alertLogs(alerttime,alert,limitvalue,systemName,severity,action) VALUES(%s,%s,%s,%s,%s,%s)'
                val = (res[0][1],'Peak Demand Limt - Level 3 Breach',value,'Building Load','High','Mail sent')
           
                emscur.execute(sql,val)
                print("Peakdemand alert saved")
                ubuntudb.commit()

                with email:
                    email.send(
                    subject="EMS ALERT -  Peak Demand Limit-level 3 breach",
                    sender="emsteamrp@gmail.com",
                    # arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","ems@respark.iitm.ac.in"],
                    html=html_content
                    )
                    print("Mail Sent")
        
        emscur.close()      
        time.sleep(60)

peaklev3()


