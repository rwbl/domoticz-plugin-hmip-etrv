# Domoticz Home Automation - homematicIP Radiator Thermostat eTRV
# For the homematicIP Radiator Thermostats HmIP-eTRV-B, HmIP-eTRV-2:
#   * set the setpoint
#   * get the actual temperature
#   * get the low batery state
# Author: Robert W.B. Linn
# Version: See plugin xml definition
#
# NOTE: after every change run
# sudo service domoticz.sh restart
# Domoticz Python Plugin Development Documentation:
# https://www.domoticz.com/wiki/Developing_a_Python_plugin

"""
<plugin key="HMIP-eTRV" name="homematicIP Radiator Thermostat (HmIP-eTRV)" author="rwbL" version="1.0 (Build 20191214)">
    <description>
        <h2>homematicIP Radiator Thermostat (HMIP-eTRV) v1.0</h2>
        <ul style="list-style-type:square">
            <li>Set the setpoint (degrees C).</li>
            <li>Get the actual temperature (degrees C).</li>
            <li>Get the low battery state (true or false). Theshold set in the HomeMatic WebUI</li>
            <li>Supported are the devices HmIP-eTRV-B, HmIP-eTRV-2</li>
        </ul>
        <h2>Domoticz Devices (Type,SubType)</h2>
        <ul style="list-style-type:square">
            <li>Setpoint (Thermostat,Setpoint)</li>
            <li>Temperature (Temp,LaCrosse TX3)</li>
            <li>Battery (General,Alert)</li>
        </ul>
        <h2>Hardware Configuration</h2>
        <ul style="list-style-type:square">
            <li>Address (CCU IP address, default: NNN.NNN.N.NNN)</li>
            <li>IDs (obtained via XML-API script http://ccu-ip-address/config/xmlapi/statelist.cgi):</li>
            <ul style="list-style-type:square">
                <li>Device ID HmIP-eTRV-B or HmIP-eTRV-2 (default: 1541)</li>
                <li>Datapoint IDs(#3): SET_POINT_TEMPERATURE, ACTUAL_TEMPERATURE, LOW_BAT as comma separated list in this order (defaults: 1584,1567,1549)</li>
            </ul>
            <li>Note: After configuration update, the setpoint is 0. Click the setpoint to set the value.</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="CCU IP" width="200px" required="true" default="NNN.NNN.N.NNN"/>
        <param field="Mode1" label="Device ID" width="75px" required="true" default="1541"/>
        <param field="Mode2" label="Datapoint IDs" width="150px" required="true" default="1584,1567,1549"/>
        <param field="Mode5" label="Check Interval (sec)" width="75px" required="true" default="60"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug" default="true"/>
                <option label="False" value="Normal"/>
            </options>
        </param>
    </params>
</plugin>
"""

# Set the plugin version
PLUGINVERSION = "v1.0"
PLUGINSHORTDESCRIPTON = "HmIP-eTRV"

## Imports
import Domoticz
import urllib
import urllib.request
from datetime import datetime
import json
from lxml import etree

## Domoticz device units used for creating & updating devices
UNITSETPOINTTEMPERATURE = 1 # TypeName: N/A; Type ID:242 (Name:Thermostat); SubType ID:1 (Name:Setpoint); Create device use Type=242, Subtype=1
UNITACTUALTEMPERATURE = 2   # TypeName: Temperature
UNITLOWBAT = 3              # TypeName: Alert

# Index of the datapoints from the datapoints list
# The datapoints are defined as a comma separated string in parameter Mode2
# Syntax:DATAPOINTINDEX<Type> - without blanks or underscores
DATAPOINTINDEXSETPOINTTEMPERATURE = 0
DATAPOINTINDEXACTUALTEMPERATURE = 1
DATAPOINTINDEXLOWBAT = 2

# Tasks to perform
## Change the setpoint
TASKSETPOINTTEMPERATURE = 1 
## Get values from the datapoints ACTUAL_TEMPERATURE, LOW_BAT
TASKGETDATAPOINTS = 2   

class BasePlugin:

    def __init__(self):
        # HTTP Connection
        self.httpConn = None
        self.httpConnected = 0
        
        # List of datapoints (#3) - SET_POINT_TEMPERATURE, ACTUAL_TEMPERATURE, LOW_BAT
        self.DatapointsList = []

        # Task to complete - default is get the datapoints
        self.Task = TASKGETDATAPOINTS

        # Setpoint Thermostat
        self.SetPoint = 0       # setpoint in C 
        self.LowBat = "false"
               
        # The Domoticz heartbeat is set to every 60 seconds. Do not use a higher value as Domoticz message "Error: hardware (N) thread seems to have ended unexpectedly"
        # The Soil Moisture Monitor is read every Parameter.Mode5 seconds. This is determined by using a hearbeatcounter which is triggered by:
        # (self.HeartbeatCounter * self.HeartbeatInterval) % int(Parameter.Mode5) = 0
        self.HeartbeatInterval = 60
        self.HeartbeatCounter = 0
        return

    def onStart(self):
        Domoticz.Debug(PLUGINSHORTDESCRIPTON + " " + PLUGINVERSION)
        Domoticz.Debug("onStart called")
        Domoticz.Debug("Debug Mode:" + Parameters["Mode6"])

        if Parameters["Mode6"] == "Debug":
            self.debug = True
            Domoticz.Debugging(1)
            DumpConfigToLog()

        # if there no devices, create these
        if (len(Devices) == 0):
            Domoticz.Debug("Creating new devices ...")
            
            ## SET_POINT_TEMPERATURE - TypeName: Thermostat
            Domoticz.Device(Name="Setpoint", Unit=UNITSETPOINTTEMPERATURE, Type=242, Subtype=1, Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITSETPOINTTEMPERATURE].Name)

            ## ACTUAL_TEMPERATURE - TypeName: Temperature
            Domoticz.Device(Name="Temperature", Unit=UNITACTUALTEMPERATURE, TypeName="Temperature", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITACTUALTEMPERATURE].Name)

            ## LOW_BAT - TypeName: Alert
            Domoticz.Device(Name="Battery", Unit=UNITLOWBAT, TypeName="Alert", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITLOWBAT].Name)

            Domoticz.Debug("Creating new devices: OK")
        else:
            # NOT USED - if there are devices, go for sure and update options. Exampe selector switch
            # Options = { "LevelActions": "", "LevelNames": Parameters["Mode3"], "LevelOffHidden": "false", "SelectorStyle": "0" }
            Domoticz.Debug("Devices already created.")

        # Heartbeat
        Domoticz.Debug("Heartbeat set: "+Parameters["Mode5"])
        Domoticz.Heartbeat(self.HeartbeatInterval)
        
        # Create the datapoints list using the datapoints as defined in the parameter Mode2
        ## The string contains multiple datapoints separated by comma (,). This enables to define more devices.
        DatapointsParam = Parameters["Mode2"]
        Domoticz.Debug("Datapoints:" + DatapointsParam)
        ## Split the parameter string into a list of datapoints
        self.DatapointsList = DatapointsParam.split(',')
        # Check the list length (2 because 2 datapoints required
        if len(self.DatapointsList) < 2:
            Domoticz.Error("[ERROR] Datapoints parameter not correct! Should contain 2 datapoints.")

        return

    def onStop(self):
        Domoticz.Debug("Plugin is stopping.")

    # Send the url parameter (GET request)
    # If task = actualtemperature then to obtain device state information in xml format
    # If task = setpoint then set the setpoint usig switch using the self.switchstate
    # The http response is parsed in onMessage()
    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        if (Status == 0):
            Domoticz.Debug("CCU connected successfully.")
            self.httpConnected = 1

            # request all datapoints for the device id to get the actual data for the defined datapoints
            if self.Task == TASKGETDATAPOINTS:
                ## url example = 'http://192.168.1.225/config/xmlapi/state.cgi?device_id=' .. ID_DEVICE;
                url = '/config/xmlapi/state.cgi?device_id=' + Parameters["Mode1"]
                
            # set the new setpoitnt
            if self.Task == TASKSETPOINTTEMPERATURE:
                ## url example = 'http://192.168.1.225/config/xmlapi/statechange.cgi?ise_id=1584&new_value=
                url = '/config/xmlapi/statechange.cgi?ise_id=' + self.DatapointsList[DATAPOINTINDEXSETPOINTTEMPERATURE] + '&new_value=' + str(self.SetPoint)

            Domoticz.Debug(url)
            # define the senddata parameters (JSON)
            sendData = { 'Verb' : 'GET',
                         'URL'  : url,
                         'Headers' : { 'Content-Type': 'text/xml; charset=utf-8', \
                                       'Connection': 'keep-alive', \
                                       'Accept': 'Content-Type: text/html; charset=UTF-8', \
                                       'Host': Parameters["Address"], \
                                       'User-Agent':'Domoticz/1.0' }
                       }
            
            # Send the data and disconnect
            self.httpConn.Send(sendData)
            self.httpConn.Disconnect
            return
        else:
            self.httpConnected = 0
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Port"]+" with error: "+Description)
            return

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

        # If not conected, then leave
        if self.httpConnected == 0:
            return

        # Parse the JSON Data Object with keys Status (Number) and Data (ByteArray)
        ## 200 is OK
        responseStatus = int(Data["Status"])
        ## Domoticz.Debug("STATUS="+ str(responseStatus))
        
        ## decode the data using the encoding as given in the xml response string
        responseData = Data["Data"].decode('ISO-8859-1')
        ## Domoticz.Debug("DATA=" + responseData)

        if (responseStatus != 200):
            Domoticz.Error("[ERROR] XML-API response: " + str(responseStatus) + ";" + resonseData)
            return

        # Parse the xml string 
        # Get the xml tree - requires several conversions
        tree = etree.fromstring(bytes(responseData, encoding='utf-8'))

        # Handle the respective task to update the domoticz devices
        if self.Task == TASKGETDATAPOINTS:
            Domoticz.Debug("TASKGETDATAPOINTS")

            # Get the values for the actual_temperature
            # note that a list is returned from tree.xpath, but holds only 1 value
            actualtemperaturevalue = tree.xpath('//datapoint[@ise_id=' + self.DatapointsList[DATAPOINTINDEXACTUALTEMPERATURE] + ']/@value')   
            # Domoticz.Debug(actualtemperaturevalue[0])
            lowbat = tree.xpath('//datapoint[@ise_id=' + self.DatapointsList[DATAPOINTINDEXLOWBAT] + ']/@value')   
            # Domoticz.Debug(lowbat[0])
            setpointtemperaturevalue = tree.xpath('//datapoint[@ise_id=' + self.DatapointsList[DATAPOINTINDEXSETPOINTTEMPERATURE] + ']/@value')   
            # Domoticz.Debug(setpointtemperaturevalue[0])

            # Update the devices and log
            ## Actual temperature 
            Devices[UNITACTUALTEMPERATURE].Update( nValue=0, sValue=str(round(float(actualtemperaturevalue[0]),2)) )
            ## Battery status: false=green (1), true=red (4); store the lowbat state
            if lowbat[0] != self.LowBat:
                if lowbat[0] == "false":
                    Devices[UNITLOWBAT].Update( nValue=1, sValue="Battery status ok" )
                if lowbat[0] == "true":
                    Devices[UNITLOWBAT].Update( nValue=4, sValue="Battery status low" )
                Domoticz.Debug("T=" + Devices[UNITACTUALTEMPERATURE].sValue + "B=" + Devices[UNITLOWBAT].sValue + ",S=" +  str(round(float(setpointtemperaturevalue[0]),2)) )
            self.LowBat = lowbat[0]

            ## Update the setpoint if changed by homematic or manual
            """
            if self.SetPoint != setpointtemperaturevalue:
                self.SetPoint = round(float(setpointtemperaturevalue[0]),2)
                # Update the thermostat
                Devices[UNITSETPOINTTEMPERATURE].Update( nValue=1, sValue= str(self.SetPoint) )    
            """
            
        if self.Task == TASKSETPOINTTEMPERATURE:
            Domoticz.Debug("TASKSETPOINTTEMPERATURE")
            # Update the thermostat
            Devices[UNITSETPOINTTEMPERATURE].Update( nValue=1, sValue= str(self.SetPoint) )    
            # NOT REQUIRED = Devices[UNITSETPOINTTEMPERATURE].Refresh()    
        return

    # Set the setpoint - Create http connection, the setpoint is set in onConnect
    def onCommand(self, Unit, Command, Level, Hue):
        # onCommand called for Unit 1: Parameter 'Set Level', Level: 18.5
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        ## Set the new setpoint temperature
        self.SetPoint = Level
        Domoticz.Debug("T Setpoint=" + str(self.SetPoint))
        # Create IP connection and connect - see further onConnect where the parameters are send
        self.httpConn = Domoticz.Connection(Name="CCU-"+Parameters["Address"], Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port="80")
        self.httpConn.Connect()
        self.httpConnected = 0
        self.Task = TASKSETPOINTTEMPERATURE
        return

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        self.HeartbeatCounter = self.HeartbeatCounter + 1
        Domoticz.Debug("onHeartbeat called. Counter=" + str(self.HeartbeatCounter * self.HeartbeatInterval) + " (Heartbeat=" + Parameters["Mode5"] + ")")
        # check the heartbeatcounter against the heartbeatinterval
        if (self.HeartbeatCounter * self.HeartbeatInterval) % int(Parameters["Mode5"]) == 0:
            try:
                # Create IP connection
                self.httpConn = Domoticz.Connection(Name="CCU-"+Parameters["Address"], Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port="80")
                self.httpConn.Connect()
                self.httpConnected = 0
                self.Task = TASKGETDATAPOINTS
                return
            except:
                Domoticz.Error("[ERROR] Check settings, correct and restart Domoticz.")
                return

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

#
## Generic helper functions
#

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

"""
# <TODO>
## Sync the setpoint value in case the thermostat has been changed manual.
def syncSetpoint(self,setpoint):
        Domoticz.Debug("syncSetpoint " + str(setpoint) )

        ## Set the new setpoint temperature based on the selector switch level
        ## Convert the level 0,10,20 ... to temperature 0,19,20,12 ...
        self.SetPointLevel = Level
        ## Get the setpoint index 0,1,2 from the level to get the setpoint from the setpointlist
        setpointIndex = Level
        if setpointIndex > 0:
            setpointIndex = int(round(Level/10))
        ## Get the setpoint temperature from the setpointlist
        self.SetPoint = self.SetPointList[setpointIndex]
        Domoticz.Debug("T Setpoint=" + self.SetPoint)
        return
"""
