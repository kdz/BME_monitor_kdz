# ############ This module runs a web-server for a baby monitor
# Can deploy via ngrok for Demo, or full deploy to Heroku & friends

import bottle
from collections import namedtuple
from twilio.rest import TwilioRestClient
import requests

# ############ Model: Representation of State #############

# A world represents the current state and relevant history of the baby monitor.
# A set of (pure) update functions take a world & some inputs & compute a new world.
class World(namedtuple("World",
                       ["body_hist",            # [[time, temp]
                        "env_hist",             # [[time, temp]]
                        "last_sms_out",         # 'heat?' or 'fan?' or None
                        "heater_is_on",         # bool
                        "fan_is_on"             # bool
                       ])):
    def last_bt(self):
        return self.body_hist[0][1] if self.body_hist else -99
    def last_et(self):
        return self.env_hist[0][1] if self.body_hist else -99
    def short_repr(self):
        return "World::%3.2f, %3.2f, %s, %s, %s" % (
            self.last_bt(), self.last_et(), self.last_sms_out, self.heater_is_on, self.fan_is_on)

# The only (mutable) global variable in the program
curr_world = None

# An action is a representation of a side-effect not yet executed.
class Action(namedtuple("Action",
                        ["out_func",  # Function
                         "args"])):   # [param]
    pass

# ############ Model: Updates & Helpers (Pure Functions) #############

# An update function takes a world and some request inputs
#   and returns a new resulting world and some actions that should be executed

def update_temp_hist(w, bt, et, time):  # -> World, List of Action
    """Takes a world, and new body and env temperatures and time.
    Returns
      - a new world,
      - 0, 1, or 2 Actions: one to send sms, another to de-activate device fan or heater."""
    low, hi = temp_range(et)
    normal_temp = (low + hi) / 2
    sms_to_send = "heat?" if bt < low else "fan?" if bt > hi else None
    sms_changed = sms_to_send != w.last_sms_out if sms_to_send else False
    sms_act = Action(send_sms, [bt, et, sms_to_send]) if sms_changed else None
    if w.heater_is_on and bt > normal_temp:
        dev_action, heater_is_on, fan_is_on = Action(heat, ['off']), False, w.fan_is_on
    elif w.fan_is_on and bt < normal_temp:
        dev_action, heater_is_on, fan_is_on = Action(fan, ['off']), False, w.heater_is_on
    else:
        dev_action, heater_is_on, fan_is_on = None, w.heater_is_on, w.fan_is_on
    nw = w._replace(
        body_hist=([[time, bt]] + w.body_hist)[0:11],
        env_hist=([[time, et]] + w.env_hist)[0:11],
        last_sms_out=sms_to_send,
        heater_is_on=heater_is_on, fan_is_on=fan_is_on)
    return nw, [sms_act, dev_action]

def update_sms_in(w, y_n):  # -> World, List of Action
    """Takes a world and a Y or N sms-reply.
    Returns a new world, and 0 or 1 action (to activate the device fan or heater)"""
    if y_n == 'Y':
        low, hi = temp_range(w.last_et())
        bt_lo, bt_hi = w.last_bt() < low, w.last_bt() > hi
        if w.last_sms_out == 'heat?' and not w.heater_is_on and bt_lo:
            nw = w._replace(heater_is_on=True)
            acts = [Action(heat, ["on"])]
        elif w.last_sms_out == 'fan?' and not w.fan_is_on and bt_hi:
            nw = w._replace(fan_is_on=True)
            acts = [Action(fan, ["on"])]
        else:
            nw = w
            acts = [None]
        return nw, acts
    return w, [None]

NORMAL_TEMP = 98.4

def temp_range(env_t):  # -> (min, max)
    return NORMAL_TEMP - 0.4, NORMAL_TEMP + 0.4

# ############ Input Requests #############

# All input requests come via HTTP (GET or POST)
# An Input Request function:
#   - prints a trace for logging (while pure functions do not do this)
#   - checks inputs,
#   - calls an Update (pure) function with curr_world & inputs to get new_world & actions
#   - steps the curr_world to the new_world
#   - executes those actions

app = bottle.default_app()

@app.route("/")
def welcome():
    return "<h1>Welcome to your Baby Monitor!</h1><a href='/stats'>Stats</a>"

@app.route("/update_temps/<bt:float>/<et:float>/<t:int>", ["POST", "GET"])
def update_temps(bt, et, t):
    global curr_world
    print "<== update_temps: bt:%3.2f, et:%3.2f, %s" % (bt, et, curr_world.short_repr())
    curr_world, actions = update_temp_hist(curr_world, bt, et, t)
    execute(actions)

@app.route('/s')
@app.route("/stats")
def stats():
        return bottle.template('stats',
                               world=curr_world._replace(
                                   body_hist=curr_world.body_hist[0:10],
                                   env_hist=curr_world.env_hist[0:10]))

@app.route("/sms_in", ["POST", "GET"])
def sms_in():
    global curr_world
    confirm = bottle.request.POST.get('Body') or bottle.request.GET.get('Body')
    print "<== SMS IN: %s, %s" % (confirm, curr_world.short_repr())
    if confirm in ('Y', 'y', 'N', 'n'):
        curr_world, actions = update_sms_in(curr_world, confirm.upper())
        execute(actions)
    else:
        pass

@app.route("/fan_on", ["GET", "POST"])
def fan_on():
    global curr_world
    print "<== FAN_ON: %s" % curr_world.short_repr()
    fan('on')
    curr_world = curr_world._replace(fan_is_on=True)
    return bottle.redirect("/stats")

@app.route("/fan_off", ["GET", "POST"])
def fan_off():
    global curr_world
    print "<== FAN_OFF: %s" % curr_world.short_repr()
    fan('off')
    curr_world = curr_world._replace(fan_is_on=False)
    return bottle.redirect("/stats")

@app.route("/heat_on", ["GET", "POST"])
def heat_on():
    global curr_world
    print "<== HEAT_ON: %s" % curr_world.short_repr()
    heat('on')
    curr_world = curr_world._replace(heater_is_on=True)
    return bottle.redirect("/stats")

@app.route("/heat_off", ["GET", "POST"])
def heat_off():
    global curr_world
    print "<== HEAT_OFF: %s" % curr_world.short_repr()
    heat('off')
    curr_world = curr_world._replace(heater_is_on=False)
    return bottle.redirect("/stats")

# ############ Side-Effect Functions (and Helpers) #############

# A Side-Effect Function is a required output effect from the program.
# It will print a trace for logging, and perform the side effect.

TW_account = "AC19c8832ca89e51ab84e6b1c2cc371569"
TW_password = "ff573471eec178c8ab9f07dfa72c9b73"
TW_phone = "+15129420915"
TW_client = TwilioRestClient(TW_account, TW_password)
Parent = '+15123639556'
PUBLIC_BABY_SERVER = "babymon.ngrok.com"

def execute(action_list):
    for action in action_list:
        if action:
            action.out_func(*action.args)

def send_sms(bt, et, body):
    print ("  ==> SMS out: %s" % body)
    to, from_ = Parent, TW_phone
    stats_link = PUBLIC_BABY_SERVER + "/s"
    TW_client.messages.create(
        to=to,
        from_=from_,
        body="Baby alert!\nBody:%3.2f, Env:%3.2f\n%s\nTurn on %s(Y or N)" % (bt, et, stats_link, body))

def heat(on_off):
    print "  ==> HEAT: %s" % on_off
    requests.post('http://localhost:8090/heat_%s' % on_off)

def fan(on_off):
    print "  ==> FAN: %s" % on_off
    requests.post('http://localhost:8090/fan_%s' % on_off)

# ############ Run #############

if __name__ == '__main__':
    # only run this section if the file is directly executed, not as an import

    curr_world = World([], [], None, False, False)
    bottle.run(host='localhost', port=8080)

    # in Terminal:  ngrok -subdomain babymon 8080
    # After baby_server is running, start baby_device
