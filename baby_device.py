# ############# This module runs on a Raspberry-Pi connected to Arduino via Serial
# Posts sensor updates to BABY_SERVER
# Listens for device activation commands (heater & fan) via http

from BreakfastSerial import Arduino, Sensor, setInterval, Led
from bottle import route, run
import requests

board = Arduino()
body_sensor = Sensor(board, "A0")
env_sensor = Sensor(board, "A1")
heatLed = Led(board, 2)
fanLed = Led(board, 13)

def temp_calibrator(v1, t1, v2, t2):  # -> Function[float -> float]
    """Given 2 calibration points, returns a customized V_to_Temp function"""
    def raw_v_to_temp(rawV):
        return (t2 - t1)/(v2 - v1) * (rawV - v1) + t1
    return raw_v_to_temp

raw_v_to_temp = temp_calibrator(0.3628, 83.0, 0.309, 70.0)

TIME_GAP_SECS = 5   # sampling interval for device
CURR_TIME_SECS = 0  # simple seconds time counter, don't need datetime

def update_temps():
    """Will be called periodically to gather & post device sensor values"""
    global CURR_TIME_SECS
    bv = body_sensor.value
    ev = env_sensor.value
    CURR_TIME_SECS += TIME_GAP_SECS
    if bv is None or ev is None:
        return
    else:
        bt = raw_v_to_temp(bv)
        et = raw_v_to_temp(ev)
        # print "Body: %3.2f, Env: %3.2f" % (bt, et)
        requests.post('http://localhost:8080/update_temps/%s/%s/%s' % (bt, et, CURR_TIME_SECS))

setInterval(update_temps, TIME_GAP_SECS*1000)

@route("/fan_on", ["POST", "GET"])
def fan_on():
    print "DEVICE ROUTE: FAN_ON"
    fanLed.on()
    return "Fan on"

@route("/fan_off", ["POST", "GET"])
def fan_off():
    print "DEVICE ROUTE: FAN_OFF"
    fanLed.off()
    return "Fan off"

@route("/heat_on", ["POST", "GET"])
def heat_on():
    print "DEVICE ROUTE: HEAT_ON"
    heatLed.on()
    return "Heat on"

@route("/heat_off", ["POST", "GET"])
def heat_off():
    print "DEVICE ROUTE: HEAT_OFF"
    heatLed.off()
    return "Heat off"

if __name__ == '__main__':
    # only run this if the file is directly executed, not as an import
    fan_off()
    heat_off()

    run(host='localhost', port=8090)

