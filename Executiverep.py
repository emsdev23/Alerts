import mysql.connector
from redmail import EmailSender
from datetime import date,timedelta,datetime
import time

head="""
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report</title>
        <style>
            body {
                margin: 0;
                font-family: Sans-Serif;
            }
            .energycontainer{
                margin-left: 1%;
                width: 95%;
                border-radius: 5px;
                background-color: #F7F7F7;
                border: 5px solid white;
            }
            .buildcontainer{
                margin-left: 1%;
                width: 95%;
                border-radius: 5px;
                background-color: #F7F7F7;
                border: 5px solid white;
            }
            .container {
                width: 96.5%;
                height: 14%;
                background-color: white;
                border: 1px solid white;
                padding: 1%;
                box-sizing: border-box;
                position: relative;
                border-radius: 5px;
                margin-left: 1%;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .container1 {
                margin-top:0%;
                width: 95%;
                height: 14%;
                background-color: #F7F7F7;
                padding: 1%;
                box-sizing: border-box;
                position: relative;
                border-radius: 5px;
                justify-content: space-between;
                align-items: center;
            }
            .evcontainer {
                width: 100%;
                height: 14%;
                background-color: white;
                border: 1px solid white;
                box-sizing: border-box;
                border-radius: 5px;
                margin-left: 1%;
                position: relative;
                display: flex;
                align-items: center;
            }
            .content {
                background-color: #3d403d;
                color: white;
                padding: 0.35%;
                border-radius: 5px;
                width: 25%;
                text-align: center;
            }
            .content1 {
                margin-left: 1%;
                background-color: #947F9B;
                color: white;
                height : 5%;
                border-radius: 5px;
                width: 22%;
                text-align: center;
            }
            h3 {
                margin: 0;
                font-size: 25px;
            }
            .bar-container {
                width: 95%;
                height: 25px;
                margin-left: 1%;
                background-color: #F7F7F7;
                overflow: hidden;
                position: relative;
                display: flex;
                align-items: flex-start;
                justify-content: center;
            }
            .bar {
                height: 100%;
                transition: width 0.5s ease-in-out;
                float: left;
            }

            .bar.clients {
                background-color: #FF9F0E;
            }

            .bar.chillers {
                background-color: #FFB443;
            }

            .bar.utilities {
                background-color: #FFCF87;
            }
            .bar.others{
                background-color: #FFE7C4;
            }
            .bar.grid{
                background-color: #2E61E6;
            }
            .bar.wheel{
                background-color: #6589E6;
            }
            .bar.roof{
                background-color: #6589E6;
            }
            .bar.diesel{
                background-color: #b0a9a5;
            }
        </style>
    </head>
"""

while True:

    curdate = datetime.now()
    mint = str(curdate)[11:16]
    print(mint)

    if 1==1:

    # if mint == "10:00":

        try:
            emsdb = mysql.connector.connect(
                host="121.242.232.211",
                user="emsroot",
                password="22@teneT",
                database='EMS',
                port=3306
            )

            emscur = emsdb.cursor()

            awsdb = mysql.connector.connect(
                    host="43.205.196.66",
                    user="emsroot",
                    password="22@teneT",
                    database='EMS',
                    port=3307
                )

            awscur = awsdb.cursor()
        
        except Exception as ex:
            print(ex)
            continue

        current_date = date.today()
                    
        yesterday = current_date - timedelta(days = 1)
                    
        formatted_date = yesterday.strftime("%d %B %Y")

        datelist = formatted_date.split(' ')
        # print(datelist)
        if int(formatted_date[0]) == 0:
            yesdate = datelist[0][1:] + " " + datelist[1] + " " + datelist[2]
        #     dateyes = datelist[1]+','+' '+datelist[0][1:]+' '+datelist[2]
        else:
            yesdate = datelist[0] + " " + datelist[1] + " " + datelist[2]



        awscur.execute("SELECT totalApparentPower2,polledTime FROM bmsunprocessed_prodv13.hvacSchneider7230Polling WHERE DATE(polledTime) = DATE_SUB(CURDATE(), INTERVAL 1 DAY) ORDER BY totalApparentPower2 DESC LIMIT 1;")

        peak_res = awscur.fetchall()

        peakDemand = round(peak_res[0][0])
        peakTime = str(peak_res[0][1])[11:16]


        awscur.execute("select Chillers,Client,Utilities,Others from EMS.electricDaywiseUsage where polledDate = date_sub(curdate(), interval 1 day);")

        conres = awscur.fetchall()

        if conres[0][0] != None:
            Chillers = round(conres[0][0])
        else:
            Chillers = 0

        if conres[0][1] != None:
            Client = round(conres[0][1])
        else:
            Client = 0

        if conres[0][2] != None:
            Utilities = round(conres[0][2])
        else:
            Utilities = 0

        if conres[0][3] != None:
            Others = round(conres[0][3])
        else:
            Others = 0


        overall = Chillers+Client+Utilities+Others

        Chillerspr = round((Chillers/overall)*100)
        Clientpr = round((Client/overall)*100)
        Utilitiespr = round((Utilities/overall)*100)
        Otherspr = round((Others/overall)*100)

        if Utilitiespr > 0 and Utilitiespr < 10:
            UtilitiesperDiv = f""" <div class="bar utilities" style="width: 10%; background-color: #FFCF87;"> &nbsp; {Utilitiespr}%</div>"""
            UtilitiesNameDiv = f"""<div class="bar white" style="width: 10%;">Utilities</div>"""
            UtilitiesvalDiv = f"""<div class="bar white" style="width: 10%;"><b>{Utilities}</b></div>"""
        elif Utilitiespr > 10:
            UtilitiesperDiv = f""" <div class="bar utilities" style="width: {Utilitiespr}%; background-color: #FFCF87;"> &nbsp; {Utilitiespr}%</div>"""
            UtilitiesNameDiv = f"""<div class="bar white" style="width: {Utilitiespr}%;">Utilities</div>"""
            UtilitiesvalDiv = f"""<div class="bar white" style="width: {Utilitiespr}%;"><b>{Utilities}</b></div>"""

        if Chillerspr > 0 and Chillerspr < 10:
            ChillerperDiv = f"""<div class="bar white" style="width: 10%; background-color: #FFB443;"> &nbsp; {Chillerspr}%</div>"""
            ChillersNameDiv = f"""<div class="bar white" style="width: 10%;">Chillers</div>"""
            ChillersvalDiv = f"""<div class="bar white" style="width: 10%;"><b>{Chillers}</b></div>"""
        elif Chillerspr > 10:
            ChillerperDiv = f"""<div class="bar white" style="width: {Chillerspr}%; background-color: #FFB443;"> &nbsp; {Chillerspr}%</div>"""
            ChillersNameDiv = f"""<div class="bar white" style="width: {Chillerspr}%;">Chillers</div>"""
            ChillersvalDiv = f"""<div class="bar white" style="width: {Chillerspr}%;"><b>{Chillers}</b></div>"""

        if Clientpr >0 and Clientpr < 10:
            ClientNameDiv = f"""<div class="bar white" style="width: 10%;">Clients</div>"""
            ClientperDiv = f"""<div class="bar clients" style="width: 10%; background-color: #FF9F0E;"> &nbsp; {Clientpr}%</div>"""
            ClientvalDiv = f"""<div class="bar white" style="width: 10%;"><b>{Client}</b></div>"""
        elif Clientpr > 10:
            ClientNameDiv = f"""<div class="bar white" style="width: {Clientpr}%;">Clients</div>"""
            ClientperDiv = f"""<div class="bar clients" style="width: {Clientpr}%; background-color: #FF9F0E;"> &nbsp; {Clientpr}%</div>"""
            ClientvalDiv = f"""<div class="bar white" style="width: {Clientpr}%;"><b>{Client}</b></div>"""

        if Otherspr >0 and Otherspr < 10:
            OthersNameDiv = f"""<div class="bar othres" style="width: 10%;">Others</div>"""
            OthersvalDiv = f"""<div class="bar othres" style="width: 10%;"><b>{Others}</b></div>"""
            OtherperDiv = f"""<div class="bar others" style="width: 10%; background-color: #FFE7C4;"> &nbsp; {Otherspr}%</div>"""
        elif Otherspr > 10:
            OthersNameDiv = f"""<div class="bar othres" style="width: {Otherspr}%;">Others</div>"""
            OthersvalDiv = f"""<div class="bar othres" style="width: {Otherspr}%;"><b>{Others}</b></div>"""
            OtherperDiv = f"""<div class="bar others" style="width: {Otherspr}%; background-color: #FFE7C4;"> &nbsp; {Otherspr}%</div>"""

        # print(Chillerspr)
        # print(Clientpr)
        # print(Utilitiespr)
        # print(Otherspr)



        awscur.execute("SELECT sum(bmsgrid),sum(rooftopEnergy),sum(wheeledinEnergy),sum(diesel) FROM EMS.buildingConsumption where date(polledTime) = date_sub(curdate(), interval 1 day);")

        total_res = awscur.fetchall()

        if total_res[0][0] != None:
            grid = round(total_res[0][0])
        else:
            grid = 0

        if total_res[0][1] != None:
            roof = round(total_res[0][1])
        else:
            roof = 0

        if total_res[0][2] != None:
            wheel = round(total_res[0][2])
        else:
            wheel = 0

        total_grid = grid - wheel

        if total_res[0][3] != None:
            diesel = round(total_res[0][3])
        else:
            diesel = 0 

        print(total_grid)
        print(roof)
        print(wheel)

        total = total_grid+roof+wheel+diesel

        gridpr = round((total_grid/total)*100,2)
        roofpr = round((roof/total)*100,2)
        wheelpr = round((wheel/total)*100,2)
        dieselpr = round((diesel/total)*100,2)

        if dieselpr > 10:
            dieselNameVal = f"""<div class="bar others" style="width: {dieselpr}%;">Diesel</div>"""
            dieselDiv =f"""<div class="bar others" style="width: {dieselpr}%; background-color: #b0a9a5; color:white;"> &nbsp;{dieselpr}%</div>"""
            dieselValDiv = f"""<div class="bar othres" style="width: {dieselpr}%;"><b>{diesel}</b></div>"""
        elif dieselpr > 0 and dieselpr < 10:
            dieselNameVal = f"""<div class="bar others" style="width: 10%;">Diesel</div>"""
            dieselDiv =f"""<div class="bar others" style="width: 10%; background-color: #b0a9a5; color:white;"> &nbsp;{dieselpr}%</div>"""
            dieselValDiv = f"""<div class="bar othres" style="width: 10%;"><b>{diesel}</b></div>"""
        else:
            dieselNameVal = f"""<div class="bar others" style="width: 10%;">Diesel</div>"""
            dieselDiv =f"""<div class="bar others" style="width: 10%; background-color: #F7F7F7;">{dieselpr}%</div>"""
            dieselValDiv = f"""<div class="bar othres" style="width: 10%;"><b>{diesel}</b></div>"""

        if roofpr > 10:
            roofNameVal = f"""<div class="bar roof" style="width: {roofpr}%;">Rooftop</div>"""
            roofDiv = f"""<div class="bar roof" style="width: {roofpr}%; background-color: #9BB5F9; color:white;"><b> &nbsp;{roofpr}%</b></div>"""
            roofValDiv =f"""<div class="bar white" style="width: {roofpr}%; "><b>{roof}</b></div>"""
        elif roofpr > 0 and roofpr < 10:
            roofNameVal = f"""<div class="bar roof" style="width: 10%;">Rooftop</div>"""
            roofDiv = f"""<div class="bar roof" style="width: 10%; background-color: #9BB5F9; color:white;"><b> &nbsp;{roofpr}%</b></div>"""
            roofValDiv =f"""<div class="bar white" style="width: 10%;"><b>{roof}</b></div>"""
        else:
            roofNameVal = f"""<div class="bar roof" style="width: 10%;">Rooftop</div>"""
            roofDiv =f"""<div class="bar white" style="width: 10%; background-color: #F7F7F7;"><b> &nbsp;{roofpr}%</b></div>"""
            roofValDiv = f"""<div class="bar white" style="width: 10%;"><b>{roof}</b></div>"""

        if wheelpr > 25:
            wheelNameVal = f"""<div class="bar wheel" style="width: {wheelpr}%;">Wheeled in Solar</div>"""
            wheelDiv = f"""<div class="bar wheel" style="width: {wheelpr}%; background-color: #6589E6;  color:white;"> &nbsp;{wheelpr}%</div>"""
            wheelValDiv = f"""<div class="bar wheel" style="width: {wheelpr}%;"><b>{wheel}</b></div>"""
        elif wheelpr > 0 and wheelpr < 20:
            wheelNameVal = f"""<div class="bar wheel" style="width: 25%;">Wheeled in Solar</div>"""
            wheelDiv = f"""<div class="bar wheel" style="width: 25%; background-color: #6589E6; color:white;"> &nbsp;{wheelpr}%</div>"""
            wheelValDiv = f"""<div class="bar white" style="width: 25%;"><b>{wheel}</b></div>"""
        else:
            wheelNameVal = f"""<div class="bar wheel" style="width: 10%;">Wheeled in Solar</div>"""
            wheelDiv = f"""<div class="bar wheel" style="width: 10%; background-color: #F7F7F7;"> &nbsp;{wheelpr}%</div>"""
            wheelValDiv = f"""<div class="bar white" style="width: 10%;"><b>{wheel}</b></div>"""

        if gridpr > 10:
            gridValName = f"""<div class="bar grid" style="width: {gridpr}%;">Grid+wind</div>"""
            gridDiv = f"""<div class="bar grid" style="width: {gridpr}%; background-color: #2E61E6; color:white;"><span> &nbsp;{gridpr}%</span></div>"""
            gridValDiv = f"""<div class="bar white" style="width: {gridpr}%;"><b>{total_grid}</b></div>"""
        elif gridpr > 0 and gridpr < 10:
            gridValName = f"""<div class="bar grid" style="width: 10%;">Grid+wind</div>"""
            gridDiv = f"""<div class="bar grid" style="width: 10%; background-color: #2E61E6; color:white;"><span> &nbsp; {gridpr}%</span></div>"""
            gridValDiv = f"""<div class="bar white" style="width: 10%;"><b>{total_grid}</b></div>"""
        else:
            gridValName = f"""<div class="bar grid" style="width: 10%;">Grid+wind</div>"""
            gridDiv = f"""<div class="bar grid" style="width: 10%; background-color: #F7F7F7;"><span> &nbsp; {gridpr}%</span></div>"""
            gridValDiv =f"""<div class="bar white" style="width: 10%;"><b>{total_grid}</b></div>"""


        awscur.execute("SELECT sum(totalsessions),round(sum(energyconsumption)) FROM EMS.evcharger where date(servertime) = date_sub(curdate(), interval 1 day);")

        evres = awscur.fetchall()

        if evres[0][0] != None:
            total_EvSessions = evres[0][0]
        else:
            total_EvSessions = 0

        if evres[0][1] != None:
            total_EvEnergy = evres[0][1]
        else:
            total_EvEnergy = 0

        awscur.execute("""SELECT sum(thermalDischarge) FROM EMS.buildingConsumption 
        where polledTime >= CURDATE() - INTERVAL 1 DAY + INTERVAL 6 HOUR 
        and polledTime <= CURDATE() - INTERVAL 1 DAY + INTERVAL 10 HOUR 
        or polledTime >= CURDATE() - INTERVAL 1 DAY + INTERVAL 18 HOUR
        and polledTime <= CURDATE() - INTERVAL 1 DAY + INTERVAL 22 HOUR;""")

        thermal_res = awscur.fetchall()

        if thermal_res[0][0] != None:
            thermalEnergy = round(thermal_res[0][0])
        else:
            thermalEnergy = 0

        # if thermal_res[0][1] != None:
        #     thermalCost = thermal_res[0][1]
        # else:
        #     thermalCost = 0

        peakDemandDiv = f"""
                        <table style="width:96%; margin-left: 1%;">
                            <tr>
                            <td bgcolor="#8D9EA7"><bold>Peak Demand</bold></td>
                            </tr>
                        </table>
                        <table style="width:96%; margin-left: 1%;">
                            <tr>
                            <td>&#128350 06:00-10:00 & 18:00-22:00</td>
                            <td><b>System Used</b> <br><br> Thermal Storage</td>
                            <td><b>Savings</b> <br><br>Discharge Energy 1000kW</td>
                            <td><b></b> <br><br></td>
                            </tr>
                        </table>
                        """

        if diesel > 0:
            powerFailureDiv = f"""
                        <table style="width:96%; margin-left: 2%;">
                            <tr>
                            <td bgcolor="#8D9EA7"; style ="color:white;">&nbsp;<b>Power Failure</b></td>
                            </tr>
                        </table>
                        <table style="width:96%; margin-left: 2%;">
                            <tr>
                            <td>&#128350 06:00-10:00 & 18:00-22:00</td>
                            <td><b>System Used</b> <br><br> Diesel</td>
                            <td><br><br>Energy {round(diesel)}kW</td>
                            </tr>
                        </table>"""

        else:
            powerFailureDiv = f"""
                        <table style="width:96%; margin-left: 2%;">
                            <tr>
                            <td bgcolor="#8D9EA7"; style ="color:white;">&nbsp;<b>Power Failure</b></td>
                            </tr>
                        </table>
                        <table style="width:96%; margin-left: 2%;">
                            <tr>
                            <td>No power failure</td>
                            </tr>
                        </table>"""
            

        emscur.execute("SELECT dischargeON,dischargeOFF,Energy FROM EMS.ltoLogDchg where recordDate = date(curdate()-5) and cause = 'peakdemand';")

        enerres = emscur.fetchall()

        peak_discharge = ""

        if len(enerres) > 0:
            for i in enerres:
                disOn = str(i[0])[11:16]
                disOff = str(i[1])[11:16]
                peak_discharge = peak_discharge+f"""
                <tr>                
                <td> <br><br>&#128350 {disOn}-{disOff}</td>
                <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>System Used</b> <br><br>&nbsp;&nbsp;&nbsp;&nbsp; LTO Battery</td>
                <td><b>Savings</b> <br><br>Discharge Energy {i[2]}kWh</td>
                </tr>"""
        
        else:
            peak_discharge = """            
            <table style="width:96%; margin-left: 2%;">
                <tr>
                <td>No peak discharge</td>
                </tr>
            </table> """


        email = EmailSender(host="smtp.gmail.com", port=587, username='emsteamrp@gmail.com', password='eebpnvgyfzzdtitb')

        body = f"""
        <body>
            <div class="container">
                <div>
                    <h3>IIT Madras Research Park</h3>
                    <p>Chennai, India {yesdate}</p>
                </div>
                <div class="content">
                    <p><b>Peak Demand</b></p>
                    <p><b> <span style="font-size:17px">{peakDemand}kVA </span></b> &nbsp; &#128350 {peakTime} </p>
                </div>
            </div>

            <div class="energycontainer">
            <div class="container1">
                <p style="font-size: 18px;"><b>Total Energy Consumed</b>  &nbsp;<span style="color:#b0a9a5">Energy in kWh</span></p>
                <p><b>{total}</b></p>
            </div>
            <div class="bar-container">
                {gridValName}
                <div class="bar white" style="width: 10%;"></div>

                {wheelNameVal}
                <div class="bar white" style="width: 10%;"></div>

                {roofNameVal}
                <div class="bar white" style="width: 10%;"></div>

                {dieselNameVal}
            </div>
            
            <div>
            </div>

            <div class="bar-container">
                {gridDiv}
                <div class="bar white" style="width: 10%;"></div>

                {wheelDiv}
                <div class="bar white" style="width: 10%;"></div>

                {roofDiv}
                <div class="bar white" style="width: 10%;"></div>

                {dieselDiv}
            </div>
            <div class="bar-container">
                {gridValDiv}
                <div class="bar white" style="width: 10%;"></div>

                {wheelValDiv}
                <div class="bar white" style="width: 10%;"></div>

                {roofValDiv}
                <div class="bar white" style="width: 10%;"></div>

                {dieselValDiv}   
            </div>
            </div>


            <div class="buildcontainer">
                <div class="container1">
                <p style="font-size: 18px;"><b>Building Consumption</b> &nbsp;<span style="color:#b0a9a5">Energy in kWh</span></p>
                </div>
                <div class="bar-container">
                    {ClientNameDiv}
                    {ChillersNameDiv}
                    {UtilitiesNameDiv}
                    {OthersNameDiv} 
                </div>
                <div class="bar-container">
                    {ClientperDiv}
                    {ChillerperDiv}
                    {UtilitiesperDiv}
                    {OtherperDiv}
                </div>
                <div class="bar-container">
                    {ClientvalDiv}
                    {ChillersvalDiv}
                    {UtilitiesvalDiv}
                    {OthersvalDiv} 
                </div>
            </div>
            
            

            <p style="margin-left: 2%;"><b>EV Charges</b></p>
            <div class="evcontainer">
                <div class="content1">
                    <p>Total Energy Consumed</p>
                    <p><b>{total_EvEnergy} kWh</b></p>
                </div>
                &nbsp; &nbsp; &nbsp; &nbsp;
                <div class="content1">
                    <p>Total Sessions(s)</p>
                    <p><b>{total_EvSessions}</b></p>
                </div>
            </div>

            <br>

            <div class="container4">
            <table style="width:96%; margin-left: 2%;">
                <tr>
                <td bgcolor="#8D9EA7"; style ="color:white;">&nbsp;<b>Peak Tarrif Hours</b></td>
                </tr>
            </table>
            <table style="width:96%; margin-left: 2%;">
                <tr>
                <td> <br><br>&#128350 06:00-10:00 & 18:00-22:00</td>
                <td><b>System Used</b> <br><br> Thermal Storage</td>
                <td><b>Savings</b> <br><br>Discharge Energy {thermalEnergy}ckWh</td>
                </tr>
            </table>
            <br>
            <br>

            

            <table style="width:96%; margin-left: 2%;">
                <tr>
                <td bgcolor="#8D9EA7"; style ="color:white;">&nbsp;<b>Peak Demand</b></td>
                </tr>
            </table>
            <table style="width:96%; margin-left: 2%;">
            {peak_discharge}
            </table>
            <br>

            

            {powerFailureDiv}
            </div>
        </body>
        """

        html = head+body

        with email:
            email.send(
                subject="Executive Summary",
                sender="emsteamrp@gmail.com",
                receivers=["arun.kumar@tenet.res.in"],
                # "faheera@respark.iitm.ac.in","anirbaan@respark.iitm.ac.in"],
                html=html
            )
        
        emscur.close()
        awscur.close()
        print("Mail sent successfully")

    time.sleep(60)
