# ToDo domoticz-plugin-hmip-etrv
Status 20200128

### FIX: onMessage TypeError
Understand this error message and seek a fix.
```
2020-01-21 19:57:22.685 Error: (Thermostat WZ-1) 'onMessage' failed 'TypeError':'byte indices must be integers or slices, not str'. 
2020-01-21 19:57:22.685 Error: (Thermostat WZ-1) ----> Line 367 in '/home/pi/domoticz/plugins/hmip-etrv/plugin.py', function onMessage 
2020-01-21 19:57:22.685 Error: (Thermostat WZ-1) ----> Line 228 in '/home/pi/domoticz/plugins/hmip-etrv/plugin.py', function onMessage
```
Line 228 in onMessage is:
```
def onMessage(self, Connection, Data):
	# Parse the JSON Data Object with keys Status (Number) and Data (ByteArray)
    ## 200 is OK
    responseStatus = int(Data["Status"])
```

_Status_
Not started.

### NEW: Sync state when changed in HomeMatic WebUI
A solution is implemented where Domoticz is triggering requesting the state from the CCU.
This is done during the check interval to update setpoint and temperature data.
Seeking for a solution where the CCU triggers the update of the Domoticz device(s).

_Status_
It is advised by RaspberryMatic to use the addon CUxD.
Tested an example to update a domoticz text device via CUxD device (remote control)
_Example_
```
string sDate = system.Date("%d.%m.%Y"); ! sDate = "09.08.2019"; 
string sTime = system.Date("%H:%M:%S"); ! sTime = "07:32:00"; 
string nIdx = 36;
string sMsg = sDate # " " # sTime # " - Threshold reached! Take action...";
string cAmp = "&";
string sDomUrl = "'http://ccu-ip-address:8080/json.htm";
string sUrl = sDomUrl#"?type=command"#cAmp#"param=udevice"#cAmp#"idx="#nIdx#cAmp#"nvalue=0"#cAmp#"svalue="#sMsg#"'";

! OPTION: Run the command without a return result
! res = dom.GetObject("CUxD.CUX2801001:1.CMD_EXEC").State("wget -q -O - "#sUrl);

! OPTION: Run the command with a return result
! Define the command to execute
dom.GetObject("CUxD.CUX2801001:1.CMD_SETS").State ("wget -q -O - "#sUrl);

! Set the return flag to 1 to be able to read the json result
dom.GetObject("CUxD.CUX2801001:1.CMD_QUERY_RET").State (1);

! Start the command, wait till completed and get the result JSON string, i.e.
! {"status" : "OK","title" : "Update Device"}
! NOTE: The script running on the CCU waits until the completion - ensure not to execute commands which take long time.
string sRes = dom.GetObject("CUxD.CUX2801001:1.CMD_RETS").State();
! WriteLine("VT="#sRes.VarType()#"/"#sRes); ! VT=4, {"status" : "OK","title" : "Update Device"}

! handle result
var dl = dom.GetObject ("DomoticzLog");
! Update the var with result text
if (sRes.Find("OK") > 0) {
  dl.Variable("Last update OK")
}
else {
  dl.Variable("Last update ERROR")
};
! WriteLine("VT="#dl.VarType());  ! VT=9
! WriteLine(dl.Variable());       ! shows the last update string
```

_Status_
Not started.

#### NEW: Change Active Profile
Change the active profile as defined by this datapoint:
```
<datapoint ise_id="1566" name="HmIP-RF.000A18A9A64DAC:1.ACTIVE_PROFILE" operations="7" timestamp="1562422330" valueunit="" valuetype="16" value="1" type="ACTIVE_PROFILE"/>
```
Solution option:
Domoticz Device: Selector Switch
Taken from the datasheet: Up to three adjustable week profiles.
The room temperature can be adjusted according to individually tailored heating phases (up to 6 per day with configurable temperature)
The temperature can automatically be reduced during 

_Status_
Not started.

#### NEW: Valve Level
Show the valve level
```
<datapoint ise_id="1576" name="HmIP-RF.000A18A9A64DAC:1.LEVEL" operations="7" timestamp="1562415475" valueunit="" valuetype="4" value="0.000000" type="LEVEL"/>
```
Domoticz Device: Slider or Text or TBD

_Status_
Not started.
