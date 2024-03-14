import mysql.connector
from flask import Flask, jsonify
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from email.mime.multipart import MIMEMultipart
import time
from redmail import EmailSender

app = Flask('__name__')

email = EmailSender(host="smtp.gmail.com", port=587,username='emsteamrp@gmail.com',password='eebpnvgyfzzdtitb')

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

@app.route('/thermalstorage')
def thermalStorage():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        acmeterreadingsData2()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        acmeterreadingsData2()
   
    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()

    proscur.execute("SELECT polledTime FROM bmsmgmtprodv13.thermalStorageMQTTReadings order by polledTime desc limit 1;")

    res = proscur.fetchall()
    
    if len(res) > 0:
        datenow = str(res[0][0])[0:10]
        firstTime = str(res[0][0])[11:]
    
        time_secs = (curdate[0][0]-res[0][0]).total_seconds()
    
        if time_secs > 900 and time_secs < 1000:
            emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'thermal' and date(sentTime) = curdate()")

            res = emscur.fetchall()

            if len(res)!=0:
                print("mail already sent")
            else:
                print("mail loading...")
                subj = "EMS Alert - Thermal Storage data loss alert"
            
                html_content = html_head + f"""
                                    <body style="background-color:white;">
                                        <div class="container">
                                            <div class="image">
                                                <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                            </div>
                                            <div class="text">
                                                <h3>EMS Alert</h3>
                                            </div>
                                        </div>
                                        <hr>
                                        <br>
                                        <center>
                                            <table>
                                                <tr>
                                                <td><b>Alert<b></td>
                                                <td>Data loss in Thermal Storage</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Severity<b></td>
                                                    <td>Low</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Date<b></td>
                                                    <td>{datenow}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Last record<b></td>
                                                    <td>{firstTime}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>System<b></td>
                                                    <td>Thermal</td>
                                                </tr>
                                            </table>
                                            <center><a href="http://121.242.232.211:3000/RoofTopSolar" target="_blank">View Dashboard</a></center>
                                            <br>
                                            <hr>
                                            <p>EMS team</p></center>
                                    </body>"""

                sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
                val = ("thermal","10","1")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                        # Connect to the SMTP server and send the email
                with email:
                    email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
                print("Mail send sucessfully")
        
        elif time_secs > 1800 and time_secs < 1900:
            emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'thermal' and date(sentTime) = curdate() order by sentTime desc limit 1")

            res = emscur.fetchall()

            if res[0][0] == '30':
                print("mail already sent")
            else:
                emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'thermal' and date(sentTime) = curdate()")

            res = emscur.fetchall()

            if len(res)!=0:
                print("mail already sent")
            else:
                subj = 'EMS Alert - Thermal Storage data loss alert'
            
                html_content = html_head + f"""
                                    <body style="background-color:white;">
                                        <div class="container">
                                            <div class="image">
                                                <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                            </div>
                                            <div class="text">
                                                <h3>EMS Alert</h3>
                                            </div>
                                        </div>
                                        <hr>
                                        <br>
                                        <center>
                                            <table>
                                                <tr>
                                                <td><b>Alert<b></td>
                                                <td>Data loss in Thermal Storage</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Severity<b></td>
                                                    <td>Low</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Date<b></td>
                                                    <td>{datenow}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Last record<b></td>
                                                    <td>{firstTime}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>System<b></td>
                                                    <td>Thermal</td>
                                                </tr>
                                            </table>
                                            <center><a href="http://121.242.232.211:3000/RoofTopSolar" target="_blank">View Dashboard</a></center>
                                            <br>
                                            <hr>
                                            <p>EMS team</p></center>
                                    </body>"""

                sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
                val = ("thermal","30","1")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                        # Connect to the SMTP server and send the email
                
                with email:
                    email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
                print("Mail send sucessfully")
        
        elif time_secs > 3600 and time_secs < 3700:
            emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'thermal' and date(sentTime) = curdate() order by sentTime desc limit 1")

            res = emscur.fetchall()

            if res[0][0] == '60':
                print("mail already sent")
            else:
                subj = 'EMS Alert - Rooftop data loss alert'
            
                html_content = html_head + f"""
                                    <body style="background-color:white;">
                                        <div class="container">
                                            <div class="image">
                                                <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                            </div>
                                            <div class="text">
                                                <h3>EMS Alert</h3>
                                            </div>
                                        </div>
                                        <hr>
                                        <br>
                                        <center>
                                            <table>
                                                <tr>
                                                <td><b>Alert<b></td>
                                                <td>Data loss in Thermal Storage</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Severity<b></td>
                                                    <td>Low</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Date<b></td>
                                                    <td>{datenow}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Last record<b></td>
                                                    <td>{firstTime}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>System<b></td>
                                                    <td>Thermal</td>
                                                </tr>
                                            </table>
                                            <center><a href="http://121.242.232.211:3000/RoofTopSolar" target="_blank">View Dashboard</a></center>
                                            <br>
                                            <hr>
                                            <p>EMS team</p></center>
                                    </body>"""

                sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
                val = ("thermal","60","1")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                        # Connect to the SMTP server and send the email
                
                with email:
                    email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
                print("Mail send sucessfully")

        proscur.close()
        emscur.close()
        return jsonify(time_secs)
    else:
        return jsonify("time not available")


@app.route('/griddatamvp1null30')
def gridDatanullMVP1():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridDatanullMVP1()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridDatanullMVP1()

    emscur.execute("SELECT current_timestamp();")

    curdate = emscur.fetchall()

    curdat = curdate[0][0]

    print(curdat)

    emscur.execute("select alertTime from EMS.dataLossNull where date(alertTime) = curdate() and alertName = 'mvp1null30'")

    timechk = emscur.fetchall()

    if len(timechk) !=0: 
        timer = timechk[-1][0]
        
        if (timer - curdat).total_seconds() >= 15000:
            proscur.execute("SELECT acmeterenergy,polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP1' order by polledTime desc limit 30;")
   
            res = proscur.fetchall()

            val = [i[0] for i in res if i[0] != None]

            if len(res) == 30:
                if len(val) == 0:
                    dated = str(res[-1][1])
                    datenow = dated[0:10]
                    firstTime = dated[11:]
                    
                    subj = 'EMS Alert - Schneider mvp data loss alert'

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
                                                        <td>Data loss in Schneider - MVP1</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Low</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                    sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                    val = (curdat,"mvp1null30")
                    emscur.execute(sql,val)
                    emsdb.commit()
                    print("Alert saved")
                                                # Connect to the SMTP server and send the email
                    with email:
                        email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                                # A plot in body
                                html=html_content
                                )
                    print("Mail send sucessfully")
            
    else:
        proscur.execute("SELECT acmeterenergy,polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP1' order by polledTime desc limit 30;")
   
        res = proscur.fetchall()

        val = [i[0] for i in res if i[0] != None]

        if len(res) == 30:
            if len(val) == 0:
                dated = str(res[-1][1])
                datenow = dated[0:10]
                firstTime = dated[11:]
                    
                subj = 'EMS Alert - Schneider mvp data loss alert'

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
                                                        <td>Data loss in Schneider - MVP1</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Low</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                val = (curdat,"mvp1null30")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                                # Connect to the SMTP server and send the email
                with email:
                    email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                                # A plot in body
                                html=html_content
                                )
                print("Mail send sucessfully")
    
    return jsonify(len(val))


@app.route('/griddatamvp2null30')
def gridDatanullMVP2():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridDatanullMVP2()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridDatanullMVP2()

    emscur.execute("SELECT current_timestamp();")

    curdate = emscur.fetchall()

    curdat = curdate[0][0]

    print(curdat)

    emscur.execute("select alertTime from EMS.dataLossNull where date(alertTime) = curdate() and alertName = 'mvp2null30'")

    timechk = emscur.fetchall()

    if len(timechk) !=0: 
        timer = timechk[-1][0]
        
        if (timer - curdat).total_seconds() >= 15000:
            proscur.execute("SELECT acmeterenergy,polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP2' order by polledTime desc limit 30;")
   
            res = proscur.fetchall()

            val = [i[0] for i in res if i[0] != None]

            if len(res) == 30:
                if len(val) == 0:
                    dated = str(res[-1][1])
                    datenow = dated[0:10]
                    firstTime = dated[11:]
                    
                    subj = 'EMS Alert - Schneider mvp data loss alert'

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
                                                        <td>Data loss in Schneider - MVP2</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Low</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                    sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                    val = (curdat,"mvp2null30")
                    emscur.execute(sql,val)
                    emsdb.commit()
                    print("Alert saved")
                                                # Connect to the SMTP server and send the email
                    with email:
                        email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                                # A plot in body
                                html=html_content
                                )
                    print("Mail send sucessfully")
            
    else:
        proscur.execute("SELECT acmeterenergy,polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP2' order by polledTime desc limit 30;")
   
        res = proscur.fetchall()

        val = [i[0] for i in res if i[0] != None]

        if len(res) == 30:
            if len(val) == 0:
                dated = str(res[-1][1])
                datenow = dated[0:10]
                firstTime = dated[11:]
                    
                subj = 'EMS Alert - Schneider mvp data loss alert'

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
                                                        <td>Data loss in Schneider - MVP2</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Low</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                val = (curdat,"mvp2null30")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                                # Connect to the SMTP server and send the email
                with email:
                    email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],
                                # A plot in body
                                html=html_content
                                )
                print("Mail send sucessfully")
    
    return jsonify(len(val))

@app.route('/griddatamvp3null30')
def gridDatanullMVP3():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridDatanullMVP3()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridDatanullMVP3()

    emscur.execute("SELECT current_timestamp();")

    curdate = emscur.fetchall()

    curdat = curdate[0][0]

    print(curdat)

    emscur.execute("select alertTime from EMS.dataLossNull where date(alertTime) = curdate() and alertName = 'mvp3null30'")

    timechk = emscur.fetchall()

    if len(timechk) !=0: 
        timer = timechk[-1][0]
        
        if (timer - curdat).total_seconds() >= 15000:
            proscur.execute("SELECT acmeterenergy,polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP3' order by polledTime desc limit 30;")
   
            res = proscur.fetchall()

            val = [i[0] for i in res if i[0] != None]

            if len(res) == 30:
                if len(val) == 0:
                    dated = str(res[-1][1])
                    datenow = dated[0:10]
                    firstTime = dated[11:]
                    
                    subj = 'EMS Alert - Schneider mvp data loss alert'

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
                                                        <td>Data loss in Schneider - MVP3</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Low</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                    sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                    val = (curdat,"mvp3null30")
                    emscur.execute(sql,val)
                    emsdb.commit()
                    print("Alert saved")
                                                # Connect to the SMTP server and send the email
                    with email:
                        email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                                # A plot in body
                                html=html_content
                                )
                    print("Mail send sucessfully")
            
    else:
        proscur.execute("SELECT acmeterenergy,polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP3' order by polledTime desc limit 30;")
   
        res = proscur.fetchall()

        val = [i[0] for i in res if i[0] != None]

        if len(res) == 30:
            if len(val) == 0:
                dated = str(res[-1][1])
                datenow = dated[0:10]
                firstTime = dated[11:]
                    
                subj = 'EMS Alert - Schneider mvp data loss alert'

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
                                                        <td>Data loss in Schneider - MVP3</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Low</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                val = (curdat,"mvp3null30")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                                # Connect to the SMTP server and send the email
                with email:
                    email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                                # A plot in body
                                html=html_content
                                )
                print("Mail send sucessfully")
    return jsonify(len(val))

@app.route('/griddatamvp4null30')
def gridDatanullMVP4():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridDatanullMVP4()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridDatanullMVP4()

    emscur.execute("SELECT current_timestamp();")

    curdate = emscur.fetchall()

    curdat = curdate[0][0]

    print(curdat)

    emscur.execute("select alertTime from EMS.dataLossNull where date(alertTime) = curdate() and alertName = 'mvp4null30'")

    timechk = emscur.fetchall()

    if len(timechk) !=0: 
        timer = timechk[-1][0]
        
        if (timer - curdat).total_seconds() >= 15000:
            proscur.execute("SELECT acmeterenergy,polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP4' order by polledTime desc limit 30;")
   
            res = proscur.fetchall()

            val = [i[0] for i in res if i[0] != None]

            if len(res) == 30:
                if len(val) == 0:
                    dated = str(res[-1][1])
                    datenow = dated[0:10]
                    firstTime = dated[11:]
                    
                    subj = 'EMS Alert - Schneider mvp data loss alert'

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
                                                        <td>Data loss in Schneider - MVP4</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Low</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                    sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                    val = (curdat,"mvp4null30")
                    emscur.execute(sql,val)
                    emsdb.commit()
                    print("Alert saved")
                                                # Connect to the SMTP server and send the email
                    with email:
                        email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                                # A plot in body
                                html=html_content
                                )
                    print("Mail send sucessfully")
            
    else:
        proscur.execute("SELECT acmeterenergy,polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP4' order by polledTime desc limit 30;")
   
        res = proscur.fetchall()

        val = [i[0] for i in res if i[0] != None]

        if len(res) == 30:
            if len(val) == 0:
                dated = str(res[-1][1])
                datenow = dated[0:10]
                firstTime = dated[11:]
                    
                subj = 'EMS Alert - Schneider mvp data loss alert'

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
                                                        <td>Data loss in Schneider - MVP4</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Low</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                val = (curdat,"mvp4null30")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                                # Connect to the SMTP server and send the email
                with email:
                    email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                                # A plot in body
                                html=html_content
                                )
                print("Mail send sucessfully")
    
    return jsonify(len(val))

@app.route('/schneidernull30')
def schneiderDatanull1():
    try:
        bmsdb = mysql.connector.connect(
            host="121.242.232.151",
            user="bmsrouser6",
            password="bmsrouser6@151U",
            database='bmsmgmtprodv13',
            port=3306
            )
 
        bmscur = bmsdb.cursor()


    except Exception as ex:
        print(ex)
        time.sleep(5)
        dataLoss()
    
    emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
    
    emscur = emsdb.cursor()
    
    emscur.execute("SELECT current_timestamp();")

    curdate = emscur.fetchall()

    curdat = curdate[0][0]

    print(curdat)

    emscur.execute("select alertTime from EMS.dataLossNull where date(alertTime) = curdate() and alertName = 'schneider30'")

    timechk = emscur.fetchall()

    if len(timechk) !=0: 
        timer = timechk[-1][0]
        
        if (timer - curdat).total_seconds() >= 15000:
            bmscur.execute("SELECT totalApparentPower2,polledTime FROM bmsmgmt_olap_prod_v13.hvacSchneider7230Polling order by polledTime desc limit 120;")

            res = bmscur.fetchall()

            val = [i[0] for i in res if i[0] != None]

            if len(res) == 120:
                if len(val) == 0:

                    dated = str(res[-1][1])
                    datenow = dated[0:10]
                    firstTime = dated[11:]

                    smtp_host = 'smtp.gmail.com'
                    smtp_port = 587
                    sender_email = 'emsteamrp@gmail.com'
                    sender_password = 'eebpnvgyfzzdtitb'
                    receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
                    subj = 'EMS Alert - Schneider Peak demand data loss alert'
                    
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
                                                        <td>Data loss in Schneider - Peakdemand</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Low</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                    sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                    val = (curdat,"schneider30")
                    emscur.execute(sql,val)
                    emsdb.commit()
                    print("Alert saved")
                                                # Connect to the SMTP server and send the email
                    with email:
                        email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                                # A plot in body
                                html=html_content
                                )
                    print("Mail send sucessfully")

    else:
        bmscur.execute("SELECT totalApparentPower2,polledTime FROM bmsmgmt_olap_prod_v13.hvacSchneider7230Polling order by polledTime desc limit 240;")

        res = bmscur.fetchall()

        val = [i[0] for i in res if i[0] != None]

        if len(res) == 120:
            if len(val) == 0:

                dated = str(res[-1][1])
                datenow = dated[0:10]
                firstTime = dated[11:]

                subj = 'EMS Alert - Schneider Peak demand data loss alert'
                    
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
                                                        <td>Data loss in Schneider - Peakdemand</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Low</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                val = (curdat,"schneider30")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                                # Connect to the SMTP server and send the email
                with email:
                    email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                                # A plot in body
                                html=html_content
                                )
                print("Mail send sucessfully")


    return jsonify(len(val))



@app.route('/schneidernull60')
def schneiderDatanull():
    try:
        bmsdb = mysql.connector.connect(
            host="121.242.232.151",
            user="bmsrouser6",
            password="bmsrouser6@151U",
            database='bmsmgmtprodv13',
            port=3306
            )
 
        bmscur = bmsdb.cursor()


    except Exception as ex:
        print(ex)
        time.sleep(5)
        dataLoss()
    emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )

    emscur = emsdb.cursor()
        
    emscur.execute("SELECT current_timestamp();")

    curdate = emscur.fetchall()

    curdat = curdate[0][0]

    print(curdat)

    emscur.execute("select alertTime from EMS.dataLossNull where date(alertTime) = curdate() and alertName = 'schneider60'")

    timechk = emscur.fetchall()

    if len(timechk) !=0: 
        timer = timechk[-1][0]
        
        if (timer - curdat).total_seconds() >= 15000:
            bmscur.execute("SELECT totalApparentPower2,polledTime FROM bmsmgmt_olap_prod_v13.hvacSchneider7230Polling order by polledTime desc limit 240;")

            res = bmscur.fetchall()

            val = [i[0] for i in res if i[0] != None]

            if len(res) == 240:
                if len(val) == 0:

                    dated = str(res[-1][1])
                    datenow = dated[0:10]
                    firstTime = dated[11:]

                    smtp_host = 'smtp.gmail.com'
                    smtp_port = 587
                    sender_email = 'emsteamrp@gmail.com'
                    sender_password = 'eebpnvgyfzzdtitb'
                    receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
                    subj = 'EMS Alert - Schneider Peak demand data loss alert'
                    
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
                                                        <td>Data loss in Schneider - Peakdemand</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Medium</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                    sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                    val = (curdat,"schneider60")
                    emscur.execute(sql,val)
                    emsdb.commit()
                    print("Alert saved")
                                                # Connect to the SMTP server and send the email
                    with email:
                        email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                                # A plot in body
                                html=html_content
                                )
                    print("Mail send sucessfully")

    else:
        bmscur.execute("SELECT totalApparentPower2,polledTime FROM bmsmgmt_olap_prod_v13.hvacSchneider7230Polling order by polledTime desc limit 240;")

        res = bmscur.fetchall()

        val = [i[0] for i in res if i[0] != None]

        if len(res) == 30:
            if len(val) == 0:

                dated = str(res[-1][1])
                datenow = dated[0:10]
                firstTime = dated[11:]

                subj = 'EMS Alert - Schneider Peak demand data loss alert'
                    
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
                                                        <td>Data loss in Schneider - Peakdemand</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Severity<b></td>
                                                            <td>Low</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Date<b></td>
                                                            <td>{datenow}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>Last record<b></td>
                                                            <td>{firstTime}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><b>System<b></td>
                                                            <td>Building Consumption</td>
                                                        </tr>
                                                    </table>
                                                    <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                                    <br>
                                                    <hr>
                                                    <p>EMS team</p></center>
                                            </body>"""

                sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
                val = (curdat,"schneider30")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                                # Connect to the SMTP server and send the email
                with email:
                    email.send(
                                subject=subj,
                                sender="emsteamrp@gmail.com",
                                #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                                receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                                # A plot in body
                                html=html_content
                                )
                print("Mail send sucessfully")


    return jsonify(len(val))



@app.route('/datalosswheelednull30',methods=['GET'])
def dataLossWheelednull():
    try:
        bmsdb = mysql.connector.connect(
            host="121.242.232.151",
            user="bmsrouser6",
            password="bmsrouser6@151U",
            database='bmsmgmtprodv13',
            port=3306
            )
 
        bmscur = bmsdb.cursor()


    except Exception as ex:
        print(ex)
        time.sleep(5)
        dataLoss()
    emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
 
    emscur = emsdb.cursor()

    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()

    curdat = str(curdate[0][0])

    print(curdat)
    
    bmscur.execute("select ctsedogenergy,createdTime from bmsmgmtprodv13.ctsedogreadings where date(createdTime) = curdate() order by createdTime desc limit 30")
   
    res = bmscur.fetchall()

    val = [i[0] for i in res if i[0] != None]

    try:
        dated = str(res[0][1])  
    except Exception as ex:
        print(ex)
        dated = None

    if dated != None:
        datenow = dated[0:10]
        firstTime = dated[11:]
    
    emscur.execute("select alertTime from EMS.dataLossNull where alertName = 'wheeled30' and date(alertTime) = curdate();")

    alertTime = emscur.fetchall()

    if len(alertTime) != 0:
        alertTime

    if len(res) == 30:
        if len(val) == 0:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Wheeled in solar data loss alert'
            
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
                                                <td>Data loss in Wheeled-in solar</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Severity<b></td>
                                                    <td>Low</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Date<b></td>
                                                    <td>{datenow}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Last record<b></td>
                                                    <td>{firstTime}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>System<b></td>
                                                    <td>Wheeled-in solar</td>
                                                </tr>
                                            </table>
                                            <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                            <br>
                                            <hr>
                                            <p>EMS team</p></center>
                                    </body>"""

            sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
            val = ("wheeled30",curdat)
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                        # Connect to the SMTP server and send the email
            with email:
                email.send(
                        subject=subj,
                        sender="emsteamrp@gmail.com",
                        #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                        receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                        # A plot in body
                        html=html_content
                        )
            print("Mail send sucessfully")
    return jsonify(len(val))

@app.route('/datalosswheelednull60',methods=['GET'])
def dataLossWheelednull1():
    try:
        bmsdb = mysql.connector.connect(
            host="121.242.232.151",
            user="bmsrouser6",
            password="bmsrouser6@151U",
            database='bmsmgmtprodv13',
            port=3306
            )
 
        bmscur = bmsdb.cursor()


    except Exception as ex:
        print(ex)
        time.sleep(5)
        dataLoss()
    emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
 
    emscur = emsdb.cursor()

    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()

    curdat = str(curdate[0][0])

    print(curdat)

    bmscur.execute("select ctsedogenergy,createdTime from bmsmgmtprodv13.ctsedogreadings where date(createdTime) = curdate() order by createdTime desc limit 60")
   
    res = bmscur.fetchall()

    val = [i[0] for i in res if i[0] != None]

    try:
        dated = str(res[0][1])  
    except Exception as ex:
        print(ex)
        dated = None

    if dated != None:
        datenow = dated[0:10]
        firstTime = dated[11:]

    if len(res) == 60:
        if len(val) == 0:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Wheeled in solar data loss alert'
            
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
                                                <td>Data loss in Wheeled-in solar</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Severity<b></td>
                                                    <td>Low</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Date<b></td>
                                                    <td>{datenow}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Last record<b></td>
                                                    <td>{firstTime}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>System<b></td>
                                                    <td>Wheeled-in solar</td>
                                                </tr>
                                            </table>
                                            <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                            <br>
                                            <hr>
                                            <p>EMS team</p></center>
                                    </body>"""

            sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
            val = ("wheeled60",curdat)
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                        # Connect to the SMTP server and send the email
            with email:
                email.send(
                        subject=subj,
                        sender="emsteamrp@gmail.com",
                        #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                        receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                        # A plot in body
                        html=html_content
                        )
            print("Mail send sucessfully")
    
    return jsonify(len(val))


@app.route('/datalosswheelednull120',methods=['GET'])
def dataLossWheelednull2():
    try:
        bmsdb = mysql.connector.connect(
            host="121.242.232.151",
            user="bmsrouser6",
            password="bmsrouser6@151U",
            database='bmsmgmtprodv13',
            port=3306
            )
 
        bmscur = bmsdb.cursor()


    except Exception as ex:
        print(ex)
        time.sleep(5)
        dataLoss()
    emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
 
    emscur = emsdb.cursor()

    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()

    curdat = str(curdate[0][0])

    print(curdat)

    bmscur.execute("select ctsedogenergy,createdTime from bmsmgmtprodv13.ctsedogreadings where date(createdTime) = curdate() order by createdTime desc limit 120")
   
    res = bmscur.fetchall()

    val = [i[0] for i in res if i[0] != None]

    try:
        dated = str(res[0][1])  
    except Exception as ex:
        print(ex)
        dated = None

    if dated != None:
        datenow = dated[0:10]
        firstTime = dated[11:]

    if len(res) == 120:
        if len(val) == 0:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Wheeled in solar data loss alert'
            
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
                                                <td>Data loss in Wheeled-in solar</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Severity<b></td>
                                                    <td>Low</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Date<b></td>
                                                    <td>{datenow}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Last record<b></td>
                                                    <td>{firstTime}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>System<b></td>
                                                    <td>Wheeled-in solar</td>
                                                </tr>
                                            </table>
                                            <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                            <br>
                                            <hr>
                                            <p>EMS team</p></center>
                                    </body>"""

            sql = "INSERT INTO EMS.dataLossNull(alertTime,alertName) VALUES(%s,%s)"
            val = ("wheeled120",curdat)
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                        # Connect to the SMTP server and send the email
            with email:
                email.send(
                        subject=subj,
                        sender="emsteamrp@gmail.com",
                        #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                        receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                        # A plot in body
                        html=html_content
                        )
            print("Mail send sucessfully")
    
    return jsonify(len(val))


@app.route('/datalosswheeled',methods=['GET'])
def dataLoss():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )

        emscur = emsdb.cursor()

        bmsdb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmtprodv13',
            port=3306
            )
 
        bmscur = bmsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        dataLoss()
   
    bmscur.execute("select createdTime from bmsmgmtprodv13.ctsedogreadings where date(createdTime) = curdate() order by createdTime desc limit 1")
   
    res = bmscur.fetchall()
   
    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()
    
    if len(res) > 0:
        datenow = str(res[0][0])[0:10]
        firstTime = str(res[0][0])[11:]
        lst_time = res[0][0]
    else:
        bmscur.execute("select createdTime from bmsmgmtprodv13.ctsedogreadings order by createdTime desc limit 1")
   
        res = bmscur.fetchall()

        datenow = str(res[0][0])[0:10]
        firstTime = str(res[0][0])[11:]
        lst_time = res[0][0]
        
    bmscur.close()

    print(lst_time)
   
    time_secs = (curdate[0][0]-lst_time).total_seconds()
   
    print(time_secs)
   
    if time_secs > 900 and time_secs < 1000:

        bmscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'wheeled' and date(sentTime) = curdate()")

        res = bmscur.fetchall()

        if len(res)!=0:
            print("mail already sent")
        else:
       
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Wheeled in solar data loss alert'
        
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
                                            <td>Data loss in Wheeled-in solar</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Wheeled-in solar</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("wheeled","15","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")
    

    elif time_secs > 1800 and time_secs < 1900:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'wheeled' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '30':
            print("mail already sent")
        else:
       
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Wheeled in solar data loss alert'
        
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
                                            <td>Data loss in Wheeled-in solar</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Wheeled-in solar</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("wheeled","30","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    elif time_secs > 3600 and time_secs > 3700:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'wheeled' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if len(res) > 1:
            print("mail already sent")
        else:
       
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Wheeled in solar data loss alert'
        
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
                                            <td>Data loss in Wheeled-in solar</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Wheeled-in solar</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/Wheeledgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("wheeled","60","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    emscur.close()
    return jsonify(time_secs)

@app.route('/batterydata')
def batteryData():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
 
        emscur = emsdb.cursor()
        emsdate = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        batteryData()
   
    emscur.execute("SELECT received_time FROM EMS.EMSUPSbattery order by received_time desc limit 1;")
   
    res = emscur.fetchall()
   
    emsdate.execute("SELECT current_timestamp();")
   
    curdate = emsdate.fetchall()
   
    datenow = str(res[0][0])[0:10]
    firstTime = str(res[0][0])[11:]
    emsdate.close()
    emscur.close()
   
    time_secs = (curdate[0][0]-res[0][0]).total_seconds()
   
    print(time_secs)
   
    if time_secs > 900 and time_secs < 1000:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'battery' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if len(res)!=0:
            print("mail already sent")
        else:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in','ritvika@respark.iitm.ac.in']
            subj = 'EMS Alert - UPS Battery data loss alert'
        
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
                                            <td>Data loss in UPS Battery</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>UPS Battery</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("battery","15","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")
    
    elif time_secs > 1800 and time_secs < 1900:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'battery' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '30':
            print("mail already sent")
        else:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in','ritvika@respark.iitm.ac.in']
            subject = 'EMS Alert - UPS Battery data loss alert'
        
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
                                            <td>Data loss in UPS Battery</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>UPS Battery</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("batery","30","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")
    
    elif time_secs > 3600 and time_secs < 3700:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'battery' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '60':
            print("mail already sent")
        else:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in','ritvika@respark.iitm.ac.in']
            subj = 'EMS Alert - UPS Battery data loss alert'
        
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
                                            <td>Data loss in UPS Battery</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>UPS Battery</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("batery","60","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    return jsonify(time_secs)
   
@app.route('/diseldata')
def diselData():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        diselData()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        diselData()
   
   
    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()
   
    proscur.execute("SELECT polledTime FROM bmsmgmt_olap_prod_v13.DGPolling order by polledTime desc limit 1;")
   
    res = proscur.fetchall()
   
    datenow = str(res[0][0])[0:10]
    firstTime = str(res[0][0])[11:]
   
    time_secs = (curdate[0][0]-res[0][0]).total_seconds()
   
    if time_secs > 900 and time_secs < 1000:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'disel' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if len(res)!=0:
            print("mail already sent")
        else:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in']
            subj = 'EMS Alert - Disel data loss alert'
        
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
                                            <td>Data loss in Disel</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Disel</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""
                                
            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("disel","15","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    elif time_secs > 1800 and time_secs < 1900:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'disel' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '30':
            print("mail already sent")
        else:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in']
            subj = 'EMS Alert - Disel data loss alert'

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
                                            <td>Data loss in Disel</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Disel</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""
                                
            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("disel","30","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    elif time_secs > 3600 and time_secs < 3700:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'disel' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '60':
            print("mail already sent")
        else:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in']
            subj = 'EMS Alert - Disel data loss alert'
        
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
                                            <td>Data loss in Disel</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Disel</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("disel","60","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    proscur.close()
    emscur.close()
    return jsonify(time_secs)

@app.route('/griddatamvp1')
def gridData1():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridData1()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridData1()
   
    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()
   
    proscur.execute("SELECT polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP1' order by polledTime desc limit 1;")
   
    res = proscur.fetchall()
   
    datenow = str(res[0][0])[0:10]
    firstTime = str(res[0][0])[11:]
   
    time_secs = (curdate[0][0]-res[0][0]).total_seconds()
   
    if time_secs > 900 and time_secs < 1000:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp1' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if len(res)!=0:
            print("mail already sent")
        else:
           
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Grid data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter = MVP1</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp1","15","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")    
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    elif time_secs > 1800 and time_secs < 1900:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp1' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '30':
            print("mail already sent")
        else:
           
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Grid data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter = MVP1</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp1","30","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")    
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    if time_secs > 3600 and time_secs < 3700:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp1' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '60':
            print("mail already sent")
        else:
           
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Grid data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter = MVP1</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp1","60","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")    
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")
    
    proscur.close()
    emscur.close()
    return jsonify(time_secs)

@app.route('/griddatamvp2')
def gridData2():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridData2()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridData2()
   
    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()
   
    proscur.execute("SELECT polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP2' order by polledTime desc limit 1;")
   
    res = proscur.fetchall()
   
    datenow = str(res[0][0])[0:10]
    firstTime = str(res[0][0])[11:]
   
    time_secs = (curdate[0][0]-res[0][0]).total_seconds()
   
    if time_secs > 900 and time_secs < 1000:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp2' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if len(res)!=0:
            print("mail already sent")
        else:
           
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Grid data loss alert'

            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter - MVP2</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp3","15","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")

                                # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")
    
    elif time_secs > 1800 and time_secs < 1900:
        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp2' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '30':
            print("mail already sent")
        else:
           
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Grid data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter - MVP2</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp3","30","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")

                                # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")     

    elif time_secs > 3600 and time_secs < 3700:
        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp2' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '60':
            print("mail already sent")
        else:
           
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Grid data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter - MVP2</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp3","60","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")

                                # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    proscur.close()
    emscur.close()
    return jsonify(time_secs)

@app.route('/griddatamvp3')
def gridData3():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridData3()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridData3()
        
    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()
   
    proscur.execute("SELECT polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP3' order by polledTime desc limit 1;")
   
    res = proscur.fetchall()
   
    datenow = str(res[0][0])[0:10]
    firstTime = str(res[0][0])[11:]
   
    time_secs = (curdate[0][0]-res[0][0]).total_seconds()
   
    if time_secs > 900 and time_secs < 1000:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp3' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if len(res)!=0:
            print("mail already sent")
        else: 
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Grid data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter - MVP3</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""
            
            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp3","15","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    elif time_secs > 1800 and time_secs < 1900:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp3' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '30':
            print("mail sent")
        else: 
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Grid data loss alert'
    
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter - MVP3</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""
            
            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp3","30","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")
    
    elif time_secs > 3600 and time_secs < 3700:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp3' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '60':
            print("mail sent")
        else: 
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Grid data loss alert'
        
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter - MVP3</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""
            
            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp3","60","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    proscur.close()
    emscur.close()
    return jsonify(time_secs)

@app.route('/griddatamvp4')
def gridData4():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridData4()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        gridData4()
   
    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()
   
    proscur.execute("SELECT polledTime FROM bmsmgmt_olap_prod_v13.MVPPolling where mvpnum = 'MVP4' order by polledTime desc limit 1;")
   
    res = proscur.fetchall()
   
    datenow = str(res[0][0])[0:10]
    firstTime = str(res[0][0])[11:]
   
    time_secs = (curdate[0][0]-res[0][0]).total_seconds()
   
    if time_secs > 900 and time_secs < 1000:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp4' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if len(res)!=0:
            print("mail already sent")
        else:   
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in']
            subj = 'EMS Alert - Grid data loss alert'
    
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter - MVP4</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp4","15","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")

                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")
    

    elif time_secs > 1800 and time_secs < 1900:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp4' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '30':
            print("mail already sent")
        else:   
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in']
            subj = 'EMS Alert - Grid data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter - MVP4</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp4","30","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
            
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    elif time_secs > 3600 and time_secs < 3700:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'gridmvp4' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '60':
            print("mail already sent")
        else:   
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in']
            subj = 'EMS Alert - Grid data loss alert'
        
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Grid Meter - MVP4</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Grid</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("gridmvp4","60","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
            
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    proscur.close()
    emscur.close()
    return jsonify(time_secs)

   
@app.route('/schneider')
def schneiderData():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        schneiderData()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        schneiderData()
   
    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()
   
    proscur.execute("SELECT polledTime FROM bmsmgmt_olap_prod_v13.hvacSchneider7230Polling order by polledTime desc limit 1;")
   
    res = proscur.fetchall()
   
    datenow = str(res[0][0])[0:10]
    firstTime = str(res[0][0])[11:]
   
    time_secs = (curdate[0][0]-res[0][0]).total_seconds()
   
    if time_secs > 900 and time_secs < 1000:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'schneider' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if len(res)!=0:
            print("mail already sent")
        else:   
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in']
            subj = 'EMS Alert -  data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class=Schneider"text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Schneider</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Building Load</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("schneider","15","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    elif time_secs > 1800 and time_secs < 1900:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'schneider' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '30':
            print("mail already sent")
        else:   
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in']
            subj = 'EMS Alert -  data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class=Schneider"text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Schneider</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Building Load</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("schneider","30","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")
        


    elif time_secs > 3600 and time_secs < 3700:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'schneider' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if res[0][0] == '60':
            print("mail already sent")
        else:   
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in']
            subj = 'EMS Alert -  data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class=Schneider"text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Schneider</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Building Load</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/peakgraph" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("schneider","60","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")
        
    
    proscur.close()
    emscur.close()
    return jsonify(time_secs)  


@app.route('/acmeterreadings1035')
def acmeterreadingsData1():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        acmeterreadingsData1()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        acmeterreadingsData1()
   
    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()
   
    proscur.execute("SELECT acmeterpolledtimestamp FROM bmsmgmtprodv13.acmeterreadings where acmetersubsystemid = 1035 order by acmeterpolledtimestamp desc limit 1;")
   
    res = proscur.fetchall()
   
    datenow = str(res[0][0])[0:10]
    firstTime = str(res[0][0])[11:]
   
    time_secs = (curdate[0][0]-res[0][0]).total_seconds()
   
    if time_secs > 900 and time_secs < 1000:

        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'acmeter1035' and date(sentTime) = curdate()")

        res = emscur.fetchall()

        if len(res)!=0:
            print("mail already sent")
        else:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in'] 
            subj = 'EMS Alert - Rooftop data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Rooftop Meter - 1035</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Rooftop</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/RoofTopSolar" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""

            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("acmeter1035","15","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")
    elif time_secs > 1800 and time_secs < 1900:
        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'acmeter1035' and date(sentTime) = curdate() order by sentTime desc limit 1")

        res = emscur.fetchall()

        if res[0][0] == '30':
            print("mail already sent")
        else:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            # 'faheera@respark.iitm.ac.in',
            receiver_email = ['arun.kumar@tenet.res.in']
            subj = 'EMS Alert - Rooftop data loss alert'
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Rooftop Meter - 1035</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Rooftop</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/RoofTopSolar" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""
            
            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("acmeter1035","30","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    elif time_secs > 3600 and time_secs < 3700:
        emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'acmeter1035' and date(sentTime) = curdate() order by sentTime desc limit 1")

        res = emscur.fetchall()

        if res[0][0] == '60':
            print("mail already sent")
        else:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'emsteamrp@gmail.com'
            sender_password = 'eebpnvgyfzzdtitb'
            receiver_email = ['faheera@respark.iitm.ac.in','arun.kumar@tenet.res.in']
            subj = 'EMS Alert - Rooftop data loss alert'
    
        
            html_content = html_head + f"""
                                <body style="background-color:white;">
                                    <div class="container">
                                        <div class="image">
                                            <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                        </div>
                                        <div class="text">
                                            <h3>EMS Alert</h3>
                                        </div>
                                    </div>
                                    <hr>
                                    <br>
                                    <center>
                                        <table>
                                            <tr>
                                            <td><b>Alert<b></td>
                                            <td>Data loss in Rooftop Meter - 1035</td>
                                            </tr>
                                            <tr>
                                                <td><b>Severity<b></td>
                                                <td>Low</td>
                                            </tr>
                                            <tr>
                                                <td><b>Date<b></td>
                                                <td>{datenow}</td>
                                            </tr>
                                            <tr>
                                                <td><b>Last record<b></td>
                                                <td>{firstTime}</td>
                                            </tr>
                                            <tr>
                                                <td><b>System<b></td>
                                                <td>Rooftop</td>
                                            </tr>
                                        </table>
                                        <center><a href="http://121.242.232.211:3000/RoofTopSolar" target="_blank">View Dashboard</a></center>
                                        <br>
                                        <hr>
                                        <p>EMS team</p></center>
                                </body>"""
            
            sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
            val = ("acmeter1035","60","1")
            emscur.execute(sql,val)
            emsdb.commit()
            print("Alert saved")
                                    # Connect to the SMTP server and send the email
            with email:
                email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
            print("Mail send sucessfully")

    proscur.close()
    emscur.close()
    return jsonify(time_secs)

@app.route('/acmeterreadings1147')
def acmeterreadingsData2():
    try:
        emsdb = mysql.connector.connect(
            host="121.242.232.211",
            user="emsroot",
            password="22@teneT",
            database='EMS',
            port=3306
            )
        emscur = emsdb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        acmeterreadingsData2()
   
    try:
        processeddb = mysql.connector.connect(
            host="121.242.232.151",
            user="emsrouser",
            password="emsrouser@151",
            database='bmsmgmt_olap_prod_v13',
            port=3306
            )
   
        proscur = processeddb.cursor()
    except Exception as ex:
        print(ex)
        time.sleep(5)
        acmeterreadingsData2()
   
    emscur.execute("SELECT current_timestamp();")
   
    curdate = emscur.fetchall()
   
    proscur.execute("SELECT acmeterpolledtimestamp FROM bmsmgmtprodv13.acmeterreadings where acmetersubsystemid = 1147 order by acmeterpolledtimestamp desc limit 1;")
   
    res = proscur.fetchall()
    
    if len(res) > 0:
        datenow = str(res[0][0])[0:10]
        firstTime = str(res[0][0])[11:]
    
        time_secs = (curdate[0][0]-res[0][0]).total_seconds()
    
        if time_secs > 900 and time_secs < 1000:

            emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'acmeter1147' and date(sentTime) = curdate()")

            res = emscur.fetchall()

            if len(res)!=0:
                print("mail already sent")
            else:
                print("mail loading...")
                subj = "EMS Alert - Rooftop data loss alert"
            
                html_content = html_head + f"""
                                    <body style="background-color:white;">
                                        <div class="container">
                                            <div class="image">
                                                <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                            </div>
                                            <div class="text">
                                                <h3>EMS Alert</h3>
                                            </div>
                                        </div>
                                        <hr>
                                        <br>
                                        <center>
                                            <table>
                                                <tr>
                                                <td><b>Alert<b></td>
                                                <td>Data loss in Rooftop Meter - 1147</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Severity<b></td>
                                                    <td>Low</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Date<b></td>
                                                    <td>{datenow}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Last record<b></td>
                                                    <td>{firstTime}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>System<b></td>
                                                    <td>Rooftop</td>
                                                </tr>
                                            </table>
                                            <center><a href="http://121.242.232.211:3000/RoofTopSolar" target="_blank">View Dashboard</a></center>
                                            <br>
                                            <hr>
                                            <p>EMS team</p></center>
                                    </body>"""

                sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
                val = ("acmeter1147","10","1")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                        # Connect to the SMTP server and send the email
                with email:
                    email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in"],

                    # A plot in body
                    html=html_content
                    )
                print("Mail send sucessfully")
        
        elif time_secs > 1800 and time_secs < 1900:
            emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'acmeter1147' and date(sentTime) = curdate() order by sentTime desc limit 1")

            res = emscur.fetchall()

            if res[0][0] == '30':
                print("mail already sent")
            else:
                emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'acmeter1147' and date(sentTime) = curdate()")

            res = emscur.fetchall()

            if len(res)!=0:
                print("mail already sent")
            else:
                subj = 'EMS Alert - Rooftop data loss alert'
            
                html_content = html_head + f"""
                                    <body style="background-color:white;">
                                        <div class="container">
                                            <div class="image">
                                                <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                            </div>
                                            <div class="text">
                                                <h3>EMS Alert</h3>
                                            </div>
                                        </div>
                                        <hr>
                                        <br>
                                        <center>
                                            <table>
                                                <tr>
                                                <td><b>Alert<b></td>
                                                <td>Data loss in Rooftop Meter - 1147</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Severity<b></td>
                                                    <td>Low</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Date<b></td>
                                                    <td>{datenow}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Last record<b></td>
                                                    <td>{firstTime}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>System<b></td>
                                                    <td>Rooftop</td>
                                                </tr>
                                            </table>
                                            <center><a href="http://121.242.232.211:3000/RoofTopSolar" target="_blank">View Dashboard</a></center>
                                            <br>
                                            <hr>
                                            <p>EMS team</p></center>
                                    </body>"""

                sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
                val = ("acmeter1147","30","1")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                        # Connect to the SMTP server and send the email
                
                with email:
                    email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
                print("Mail send sucessfully")
        
        elif time_secs > 3600 and time_secs < 3700:
            emscur.execute("select lossLimit from EMS.dataLossAlert where systemName = 'acmeter1147' and date(sentTime) = curdate() order by sentTime desc limit 1")

            res = emscur.fetchall()

            if res[0][0] == '60':
                print("mail already sent")
            else:
                subj = 'EMS Alert - Rooftop data loss alert'
            
                html_content = html_head + f"""
                                    <body style="background-color:white;">
                                        <div class="container">
                                            <div class="image">
                                                <img src="https://media.licdn.com/dms/image/C560BAQFAVLoL6j71Kg/company-logo_200_200/0/1657630844148?e=1692230400&v=beta&t=yOQNePjpzF0yycZuFep1AcyaXcMmfmt9Lb-5P8xa6L4" height="100px" width="100px">
                                            </div>
                                            <div class="text">
                                                <h3>EMS Alert</h3>
                                            </div>
                                        </div>
                                        <hr>
                                        <br>
                                        <center>
                                            <table>
                                                <tr>
                                                <td><b>Alert<b></td>
                                                <td>Data loss in Rooftop Meter - 1147</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Severity<b></td>
                                                    <td>Low</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Date<b></td>
                                                    <td>{datenow}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>Last record<b></td>
                                                    <td>{firstTime}</td>
                                                </tr>
                                                <tr>
                                                    <td><b>System<b></td>
                                                    <td>Rooftop</td>
                                                </tr>
                                            </table>
                                            <center><a href="http://121.242.232.211:3000/RoofTopSolar" target="_blank">View Dashboard</a></center>
                                            <br>
                                            <hr>
                                            <p>EMS team</p></center>
                                    </body>"""

                sql = "INSERT INTO EMS.dataLossAlert(systemName,lossLimit,Alertstatus) VALUES(%s,%s,%s)"
                val = ("acmeter1147","60","1")
                emscur.execute(sql,val)
                emsdb.commit()
                print("Alert saved")
                                        # Connect to the SMTP server and send the email
                
                with email:
                    email.send(
                    subject=subj,
                    sender="emsteamrp@gmail.com",
                    #ems@respark.iitm.ac.in arun.kumar@tenet.res.in faheera@respark.iitm.ac.in
                    receivers=["arun.kumar@tenet.res.in","faheera@respark.iitm.ac.in"],

                    # A plot in body
                    html=html_content
                    )
                print("Mail send sucessfully")

        proscur.close()
        emscur.close()
        return jsonify(time_secs)
    else:
        return jsonify("time not available")



if __name__ == '__main__':
    app.run(host="localhost",port=8002)
