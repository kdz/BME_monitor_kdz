# Baby Monitor

Baby Monitor is a project done under the Columbia Engineering Showcase program. The Baby Monitor is a smart Internet-of-things device. It monitors the body and environment temperature of a baby, monitors them for abnormal conditions, and notifies a parent via SMS if needed with an option to take corrective action via an embedded fan or heater. The parent can  approve this action via SMS, or view baby stats on a web page and directly control the device from there.

I have designed and developed all of the software involved myself (except for ```smart_bounds_check```). I also helped design and develop the hardware with my teammates.

Here is an overview of the device and system. 

![image](https://cloud.githubusercontent.com/assets/4351330/10556649/c69f9a8c-744e-11e5-9417-fdad9a4ad538.png)


Here is a screenshot of the baby-stats page:

![image](https://cloud.githubusercontent.com/assets/4351330/10556604/9b70100e-744d-11e5-98c8-4b6df53ac0ea.png)


## Installation and Usage

`baby_server.py` runs the main server, and `baby_device.py` is designed to run on a Raspberry-Pi, connected via Serial to the Arduino. You can also run them as separate processes on a single machine as well following these steps:

- Install Python 2.7
- Install python libs for: twilio, requests, bottle, and BreakfastSerial
- Install ngrok
- Edit ```Parent``` variable to be cell phone of "Parent" to notify, using ```+1<area-code-phone>```
- Connect Arduino board to laptop with serial / USB cable
- In one Terminal window, type: ```ngrok -subdomain=babymon 80```
- In another Terminal window, start device with python2.7: ```python2.7 baby_device.py```
- In another Terminal window, start server wtih python2.7: ```python2.7 baby_server.py``` 
- System should be operational
