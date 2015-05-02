# Baby Monitor

Baby Monitor is a current project being done under the Columbia Engineering Showcase program. The Baby Monitor is a smart Internet-of-things device. It monitors the body and environment temperature of a baby, monitors them for abnormal conditions, and notifies a parent via SMS if needed with an option to take corrective action via an embedded fan or heater. The parent can  approve this action via SMS, or view baby stats on a web page and directly control the device from there.

I have designed and developed all of the software involved myself (except for ```smart_bounds_check```). I also helped design and develop the hardware with my teammates.

Please see the README_babymon.pdf for an overview.

USAGE:

- Install Python 2.7
- Install python libs for: twilio, requests, bottle, and BreakfastSerial
- Install ngrok
- Edit ```Parent``` variable to be cell phone of "Parent" to notify, using ```+1<area-code-phone>```
- Connect Arduino board to laptop with serial / USB cable
- In one Terminal window, type: ```ngrok -subdomain=babymon 80```
- In another Terminal window, type: ```python<n> baby_device.py```
- In another Terminal window, type: ```python<n> baby_server.py``` 
- System should be operational
