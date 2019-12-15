# Domoticz Plugin homematicIP Radiator Thermostat (HmIP-eTRV-B & HmIP-eTRV-2)
v1.0 (Build 20191214)

# Objectives
Control, via Domoticz Homeautomation System, the homematicIP Radiator Thermostats HmIP-eTRV-B & HmIP-eTRV-2 connected to a RaspberryMatic CCU:
* set the temperature setpoint (SET_POINT_TEMPERATURE)
* get the room temperature (ACTUAL_TEMPERATURE)
* get the low battery status (LOW_BAT)

_Abbreviations_: GUI=Domoticz Web UI, CCU=HomeMatic Central-Control-Unit

## Solution
A Domoticz Hardware Plugin, developed with the Domoticz Python Framework, interfacing with RaspberryMatic to control the homematicIP devices.

The [RaspberryMatic](https://raspberrymatic.de/) operating system runs a "HomeMatic Central-Control-Unit (CCU)".

The CCU has the additional mandatory software XML-API CCU Addon installed.
The communication between Domoticz and the CCU is by sending a HTTP XML-API request and handle the HTTP XML response.

This plugin creates the Domoticz Devices (Type,SubType):
* Setpoint (Thermostat,Setpoint)
* Temperature (Temp,LaCrosse TX3)
* Battery (General,Alert)

### Hardware
![hmip-etrv-h](https://user-images.githubusercontent.com/47274144/70861022-066abc80-1f29-11ea-94c7-f83ca87aa403.png)
### Devices
![hmip-etrv-d](https://user-images.githubusercontent.com/47274144/70861021-04086280-1f29-11ea-83ca-37c2da9e2ce2.png)
### Communication
![hmip-etrv-c](https://user-images.githubusercontent.com/47274144/70860861-45980e00-1f27-11ea-977c-16f7c9953f4a.png)

## Hardware
* Raspberry Pi 3B+ (RaspberryMatic System)
* homematicIP Radiator Thermostats HmIP-eTRV-B and HmIP-eTRV-2

## Software
Versions for developing & using this plugin.
* Raspberry Pi Raspian  4.19.42-v7+ #1219
* RaspberryMatic 3.47.22.20191130 [info](https://raspberrymatic.de/)
* XML-API CCU Addon 1.20 [info](https://github.com/jens-maus/XML-API)
* Python 3.5.3
* Python library lxml XML toolkit 3.7.1-1 [info](https://lxml.de/)

## Prepare
The RaspberryMatic system has been setup according [these](https://github.com/jens-maus/RaspberryMatic) guidelines.

The XML-API CCU Addon is required and installed via the HomeMatic WebUI > Settings > Control panel > Additional software (see previous URL).

### Python library lxml XML toolkit
The Python library lxml XML toolkit is used to parse the XML-API response. 
Install from the CLI:
``` 
sudo apt-get install python3-lxml
```
_Note_
If the plugin is added to the Domoticz Hardware without lxml installed, then delete the hardware prior installing lxml.
After installing lxml, restart Domoticz: sudo service domoticz.sh restart

### Plugin Folder and File
Each plugin requires a dedicated subfolder in the Domoticz plugins folder, which contains the plugin file __plugin.py__.
``` 
mkdir /home/pi/domoticz/plugins/hmip-etrv
``` 
Copy the file **plugin.py** to the newly created folder.

### Restart Domoticz
After adding the plugin, Domotcicz requirs a restart to recognize the new hardware.
``` 
sudo service domoticz.sh restart
``` 
Check the Domoticz log if ok.

## Development Setup
Development PC:
* A shared drive Z: pointing to /home/pi/domoticz
* GUI > Setup > Log
* GUI > Setup > Hardware
* GUI > Setup > Devices
* WinSCP session connected to the Domoticz server (upload files)
* Putty session connected to the Domoticz server (restarting Domoticz during development)

The various GUI's are required to add the new hardware with its devices and monitor if the plugin code is running without errors.

## Development Iteration
The development process step used are:
1. Develop z:\plugins\hmip-etrv\plugin.py
2. Make changes and save plugin.py
3. Restart Domoticz from a terminal: sudo service domoticz.sh restart
4. Wait a moment and refresh the GUI > Setup > Log
5. Check the log and apply fixes as required

!IMPORTANT!
In the **GUI > Setup > Settings**, enable accepting new hardware.
This is required to add new devices created by the plugin.

Hint
For the development of a Python plugin, take (as a starter) the template from [here](https://github.com/domoticz/domoticz/blob/master/plugins/examples/BaseTemplate.py) .

## Datapoints
To communicate between the CCU and Domoticz vv, the ise_id for a device, channel and datapoint are used (the id solution).
Another option could be to use the name (i.e. name="HmIP-RF.000A18A9A64DAC:1.SET_POINT_TEMPERATURE") but this requires to obtain the full device state list for every action.
Tested the name solution, but the communication was rather slow and not the full HTTP response was loaded..
The id solution is much faster and also more flexible in defining and obtaning information for a device, channel and datapoint.

## Device Datapoint ID
Steps to obtain the device datapoint id to be able to set or get data.
The device datapoint id will be used in the plugin general parameter **Mode1**.

### Get Device Channels
Get the device channel or name from the HomeMatic WebUI > Status and control > Devices > select name. Example default name=HMIP-eTRV-2 000A18A9A64DAC or renamed=Thermostat MakeLab
Select channel 000A18A9A64DAC:1 (get this from the HomeMatic WebUI or via XML-API statelist request http://ccu-ip-address/config/xmlapi/statelist.cgi )

### Get All Devices Statelist
Submit in a webbrowser the HTTP URL XMLAPI request:
``` 
http://ccu-ip-address/config/xmlapi/statelist.cgi
``` 
The HTTP response is an XML string with the state list for all devices used (can be rather large depending number of devices connected).

### Get Device ID
From the HTTP XML-API response, search for the device name and otain the device id, i.e. 1541.

### Get Device Datapoints
**HTTP XML-API request** URL using the state script and device id (ise_id) as parameter.
``` 
http://ccu-ip-address/config/xmlapi/state.cgi?device_id=1541
``` 
**HTTP XML-API Response**
``` 
<?xml version="1.0" encoding="ISO-8859-1"?>
<state>
<device config_pending="false" unreach="false" ise_id="1541" name="Thermostat MakeLab">
<channel ise_id="1542" name="Thermostat MakeLab:0">
<datapoint ise_id="1543" name="HmIP-RF.000A18A9A64DAC:0.CONFIG_PENDING" timestamp="1576315780" valueunit="" valuetype="2" value="false" type="CONFIG_PENDING"/>
<datapoint ise_id="1547" name="HmIP-RF.000A18A9A64DAC:0.DUTY_CYCLE" timestamp="1576315780" valueunit="" valuetype="2" value="false" type="DUTY_CYCLE"/>
<datapoint ise_id="1549" name="HmIP-RF.000A18A9A64DAC:0.LOW_BAT" timestamp="1576315780" valueunit="" valuetype="2" value="false" type="LOW_BAT"/>
<datapoint ise_id="1553" name="HmIP-RF.000A18A9A64DAC:0.OPERATING_VOLTAGE" timestamp="1576315780" valueunit="" valuetype="4" value="2.800000" type="OPERATING_VOLTAGE"/>
<datapoint ise_id="1554" name="HmIP-RF.000A18A9A64DAC:0.OPERATING_VOLTAGE_STATUS" timestamp="1576315780" valueunit="" valuetype="16" value="0" type="OPERATING_VOLTAGE_STATUS"/>
<datapoint ise_id="1555" name="HmIP-RF.000A18A9A64DAC:0.RSSI_DEVICE" timestamp="1576315780" valueunit="" valuetype="8" value="187" type="RSSI_DEVICE"/>
<datapoint ise_id="1556" name="HmIP-RF.000A18A9A64DAC:0.RSSI_PEER" timestamp="1576262222" valueunit="" valuetype="8" value="187" type="RSSI_PEER"/>
<datapoint ise_id="1557" name="HmIP-RF.000A18A9A64DAC:0.UNREACH" timestamp="1576315780" valueunit="" valuetype="2" value="false" type="UNREACH"/>
<datapoint ise_id="1561" name="HmIP-RF.000A18A9A64DAC:0.UPDATE_PENDING" timestamp="1575413140" valueunit="" valuetype="2" value="false" type="UPDATE_PENDING"/>
</channel>
<channel ise_id="1565" name="HmIP-eTRV-2 000A18A9A64DAC:1">
<datapoint ise_id="1566" name="HmIP-RF.000A18A9A64DAC:1.ACTIVE_PROFILE" timestamp="1576315780" valueunit="" valuetype="16" value="1" type="ACTIVE_PROFILE"/>
<datapoint ise_id="1567" name="HmIP-RF.000A18A9A64DAC:1.ACTUAL_TEMPERATURE" timestamp="1576315780" valueunit="" valuetype="4" value="21.100000" type="ACTUAL_TEMPERATURE"/>
<datapoint ise_id="1568" name="HmIP-RF.000A18A9A64DAC:1.ACTUAL_TEMPERATURE_STATUS" timestamp="1576315780" valueunit="" valuetype="16" value="0" type="ACTUAL_TEMPERATURE_STATUS"/>
<datapoint ise_id="1569" name="HmIP-RF.000A18A9A64DAC:1.BOOST_MODE" timestamp="1576315780" valueunit="" valuetype="2" value="false" type="BOOST_MODE"/>
<datapoint ise_id="1570" name="HmIP-RF.000A18A9A64DAC:1.BOOST_TIME" timestamp="1576315780" valueunit="" valuetype="16" value="0" type="BOOST_TIME"/>
<datapoint ise_id="1571" name="HmIP-RF.000A18A9A64DAC:1.CONTROL_DIFFERENTIAL_TEMPERATURE" timestamp="0" valueunit="" valuetype="4" value="" type="CONTROL_DIFFERENTIAL_TEMPERATURE"/>
<datapoint ise_id="1572" name="HmIP-RF.000A18A9A64DAC:1.CONTROL_MODE" timestamp="0" valueunit="" valuetype="16" value="" type="CONTROL_MODE"/>
<datapoint ise_id="1573" name="HmIP-RF.000A18A9A64DAC:1.DURATION_UNIT" timestamp="0" valueunit="" valuetype="16" value="" type="DURATION_UNIT"/>
<datapoint ise_id="1574" name="HmIP-RF.000A18A9A64DAC:1.DURATION_VALUE" timestamp="0" valueunit="" valuetype="16" value="" type="DURATION_VALUE"/>
<datapoint ise_id="1575" name="HmIP-RF.000A18A9A64DAC:1.FROST_PROTECTION" timestamp="1576315780" valueunit="" valuetype="2" value="false" type="FROST_PROTECTION"/>
<datapoint ise_id="1576" name="HmIP-RF.000A18A9A64DAC:1.LEVEL" timestamp="1576315780" valueunit="" valuetype="4" value="0.150000" type="LEVEL"/>
<datapoint ise_id="1577" name="HmIP-RF.000A18A9A64DAC:1.LEVEL_STATUS" timestamp="1576315780" valueunit="" valuetype="16" value="0" type="LEVEL_STATUS"/>
<datapoint ise_id="1578" name="HmIP-RF.000A18A9A64DAC:1.PARTY_MODE" timestamp="1576315780" valueunit="" valuetype="2" value="false" type="PARTY_MODE"/>
<datapoint ise_id="1579" name="HmIP-RF.000A18A9A64DAC:1.PARTY_SET_POINT_TEMPERATURE" timestamp="0" valueunit="" valuetype="4" value="0.000000" type="PARTY_SET_POINT_TEMPERATURE"/>
<datapoint ise_id="1580" name="HmIP-RF.000A18A9A64DAC:1.PARTY_TIME_END" timestamp="0" valueunit="" valuetype="20" value="" type="PARTY_TIME_END"/>
<datapoint ise_id="1581" name="HmIP-RF.000A18A9A64DAC:1.PARTY_TIME_START" timestamp="0" valueunit="" valuetype="20" value="" type="PARTY_TIME_START"/>
<datapoint ise_id="1582" name="HmIP-RF.000A18A9A64DAC:1.QUICK_VETO_TIME" timestamp="1576315780" valueunit="" valuetype="16" value="0" type="QUICK_VETO_TIME"/>
<datapoint ise_id="1583" name="HmIP-RF.000A18A9A64DAC:1.SET_POINT_MODE" timestamp="1576315780" valueunit="" valuetype="16" value="1" type="SET_POINT_MODE"/>
<datapoint ise_id="1584" name="HmIP-RF.000A18A9A64DAC:1.SET_POINT_TEMPERATURE" timestamp="1576315780" valueunit="°C" valuetype="4" value="20.000000" type="SET_POINT_TEMPERATURE"/>
<datapoint ise_id="1585" name="HmIP-RF.000A18A9A64DAC:1.SWITCH_POINT_OCCURED" timestamp="1576315780" valueunit="" valuetype="2" value="false" type="SWITCH_POINT_OCCURED"/>
<datapoint ise_id="1586" name="HmIP-RF.000A18A9A64DAC:1.VALVE_ADAPTION" timestamp="0" valueunit="" valuetype="2" value="false" type="VALVE_ADAPTION"/>
<datapoint ise_id="1587" name="HmIP-RF.000A18A9A64DAC:1.VALVE_STATE" timestamp="1576315780" valueunit="" valuetype="16" value="4" type="VALVE_STATE"/>
<datapoint ise_id="1588" name="HmIP-RF.000A18A9A64DAC:1.WINDOW_STATE" timestamp="1576315780" valueunit="" valuetype="16" value="0" type="WINDOW_STATE"/>
</channel>
<channel ise_id="1589" name="HmIP-eTRV-2 000A18A9A64DAC:2"/>
<channel ise_id="1590" name="HmIP-eTRV-2 000A18A9A64DAC:3"/>
<channel ise_id="1591" name="HmIP-eTRV-2 000A18A9A64DAC:4"/>
<channel ise_id="1592" name="HmIP-eTRV-2 000A18A9A64DAC:5"/>
<channel ise_id="1593" name="HmIP-eTRV-2 000A18A9A64DAC:6"/>
<channel ise_id="1594" name="HmIP-eTRV-2 000A18A9A64DAC:7"/>
</device>
</state>
``` 
**Datapoints**
Get the datapoint IDs required for the plugin:
* LOW_BAT, id=1549 - used to check low battery state via alert level=1(green) or 4(red) and sent notification if alert level 4.
* ACTUAL_TEMPERATURE, id=1567 - used to get the room temperature.
* SET_POINT_TEMPERATURE, id=1584 - used to change the setpoint via Domoticz Thermostat device.
These datapoint id's will be used in the plugin general parameter **Mode2**.

### Test Changing Setpoint
Test changing the setpoint of the datapoint 1584, via webbrowser HTTP URL XML-API request using the statechange.cgi script with the datapoint id and new value.
Change setpoint to 20 C
**HTTP XML-API Request**
``` 
http://ccu-ip-address/config/xmlapi/statechange.cgi?ise_id=1584&new_value=20
``` 
**HTTP XML-API Response**
``` 
<?xml version="1.0" encoding="ISO-8859-1"?>
<result>
<changed id="1584" new_value="20"/>
</result>
``` 

To switch the thermostat OFF, set the new value to 0:
``` 
http://ccu-ip-address/config/xmlapi/statechange.cgi?ise_id=1584&new_value=0
``` 
Check the HomeMatic WebUI if the state of the channel has changed as well.

## Domoticz Devices
The **Domoticz homematicIP Radiator Thermostat** devices created are Hardware - Name (Type,SubType).
Example for new Domotcz hardware named "Thermostat MakeLab":
* Thermostat MakeLab - Setpoint (Thermostat, SetPoint)
* Thermostat MakeLab - Temperature (Temp, LaCrosse TX3)
* Thermostat MakeLab - Battery (General, Alert)


## Plugin Pseudo Code
Source code (well documented): plugin.py
__INIT__
* set self vars to handle http connection, heartbeat count, datapoints list, switch state, set task
	
__FIRST TIME__
* _onStart_ to create the Domoticz Devices
	
__NEXT TIME(S)__
* _onHeardbeat_
	* create ip connection http with the raspberrymatic
* _onConnect_
	* depending task, define the data (get,url,headers) to send to the ip connection
	* send the data and disconnect
* _onMessage_
	* parse the xml response
	* if task setpointtemperature update the setpoint and sent http xml-api request to the CCU
	* if task getdatapoints update temperature & battery device
* _onCommand_
	* set task setpointtemperature and create ip connection which is handled by onConnect

If required, add the devices manually to the Domoticz Dashboard or create a roomplan / floorplan.

## Restart Domoticz
Restart Domoticz to find the plugin:
```
sudo systemctl restart domoticz.service
```
**Note**
When making changes to the Python plugin code, ensure to restart Domoticz and refresh any of the Domoticz Web UI's.
This is the iteration process during development - build the solution step-by-step.

## Domoticz Add Hardware
**IMPORTANT**
Prior adding, set GUI > Settings the option to allow new hardware.
If this option is not enabled, no new devices are created.
Check the GUI > Setup > Log as error message Python script at the line where the new device is used
(i.e. Domoticz.Debug("Device created: "+Devices[1].Name))

In the GUI > Setup > Hardware add the new hardware **homematicIP Radiator Thermostat (HMIP-eTRV)**.
The initial check interval is set at 60 seconds. This is a good value for testing, but for final version set to higher value like every 5 minutes (300 seconds).

![hmip-etrv-h](https://user-images.githubusercontent.com/47274144/70860863-45980e00-1f27-11ea-89b7-a84367ca9746.png)

## Add Hardware - Check the Domoticz Log
After adding, ensure to check the Domoticz Log (GUI > Setup > Log)
Example:
```
2019-12-14 12:40:09.812 (MakeLab Thermostat) Debug logging mask set to: PYTHON PLUGIN QUEUE IMAGE DEVICE CONNECTION MESSAGE ALL 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Mode5':'60' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'UserDataFolder':'/home/pi/domoticz/' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'DomoticzHash':'8ec0c6f42' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Key':'HMIP-eTRV' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Author':'rwbL' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Database':'/home/pi/domoticz/domoticz.db' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Mode1':'1541' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'DomoticzVersion':'4.11564' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Name':'MakeLab Thermostat' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Language':'en' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'HomeFolder':'/home/pi/domoticz/plugins/hmip-etrv/' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Mode6':'Debug' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Version':'1.0 (Build 20191214)' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Address':'ccu-ip-address' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'HardwareID':'10' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'DomoticzBuildTime':'2019-12-13 16:35:55' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'StartupFolder':'/home/pi/domoticz/' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Mode2':'1584,1567,1549' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) 'Port':'0' 
2019-12-14 12:40:09.812 (MakeLab Thermostat) Device count: 0 
2019-12-14 12:40:09.812 (MakeLab Thermostat) Creating new devices ... 
2019-12-14 12:40:09.812 (MakeLab Thermostat) Creating device 'Setpoint'. 
2019-12-14 12:40:09.813 (MakeLab Thermostat) Device created: MakeLab Thermostat - Setpoint 
2019-12-14 12:40:09.814 (MakeLab Thermostat) Creating device 'Temperature'. 
2019-12-14 12:40:09.814 (MakeLab Thermostat) Device created: MakeLab Thermostat - Temperature 
2019-12-14 12:40:09.815 (MakeLab Thermostat) Creating device 'Battery'. 
2019-12-14 12:40:09.816 (MakeLab Thermostat) Device created: MakeLab Thermostat - Battery 
2019-12-14 12:40:09.816 (MakeLab Thermostat) Creating new devices: OK 
2019-12-14 12:40:09.816 (MakeLab Thermostat) Heartbeat set: 60 
2019-12-14 12:40:09.816 (MakeLab Thermostat) Pushing 'PollIntervalDirective' on to queue 
2019-12-14 12:40:09.816 (MakeLab Thermostat) Datapoints:1584,1567,1549 
2019-12-14 12:40:09.816 (MakeLab Thermostat) Processing 'PollIntervalDirective' message 
2019-12-14 12:40:09.816 (MakeLab Thermostat) Heartbeat interval set to: 60. 
2019-12-14 12:40:09.212 Status: (MakeLab Thermostat) Started. 
2019-12-14 12:40:09.809 Status: (MakeLab Thermostat) Entering work loop. 
2019-12-14 12:40:09.810 Status: (MakeLab Thermostat) Initialized version 1.0 (Build 20191214), author 'rwbL' 
```

## Domoticz Log Entry with Debug=False
The plugin runs every 60 seconds (Heartbeat interval) which is shown in the Domoticz log.
Note: The thermostat is turned off - displays OFF, but has auto setpoint of 4.5.
```
2019-12-14 16:58:45.131 (MakeLab Thermostat) T=19.9,S=4.5
```

## ToDo
See TODO.md
