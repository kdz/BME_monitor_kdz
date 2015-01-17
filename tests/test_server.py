# ### tests written for pytest
# to run tests in Terminal with verbose output -vv (using python2):
#    cd <project_directory>
#    python -m pytest tests -vv

from baby_server import *

def test_update_with_normal_temps_causes_no_sms_or_fan_or_heat():
    w1 = World([], [], None, False, False)
    w2, acts = update_temp_hist(w1, 98.4, 30, 0)
    assert w2 == World([[0, 98.4]], [[0, 30]], None, False, False)
    assert acts == [None, None]

    w1 = World([], [], "fan?", False, False)
    w2, acts = update_temp_hist(w1, 100, 30, 0)
    assert w2 == World([[0, 100]], [[0, 30]], "fan?", False, False)
    assert acts == [None, None]

def test_update_with_abnormal_temps_sends_sms():
    w1 = World([], [], None, False, False)
    w2, acts = update_temp_hist(w1, 80, 30, 0)
    assert w2 == World([[0, 80]], [[0, 30]], "heat?", False, False)
    assert acts == [Action(send_sms, [80, 30, 'heat?']), None]

    w2, acts = update_temp_hist(w1, 100, 30, 0)
    assert w2 == World([[0, 100]], [[0, 30]], "fan?", False, False)
    assert acts == [Action(send_sms, [100, 30, 'fan?']), None]

    w1 = World([], [], "heat?", False, False)
    w2, acts = update_temp_hist(w1, 100, 30, 0)
    assert w2 == World([[0, 100]], [[0, 30]], "fan?", False, False)
    assert acts == [Action(send_sms, [100, 30, 'fan?']), None]

def test_update_with_normal_temps_after_fan_or_heat_turns_off_heater_or_fan():
    w1 = World([], [], None, True, False)
    w2, acts = update_temp_hist(w1, 98.5, 30, 0)
    assert w2 == World([[0, 98.5]], [[0, 30]], None, False, False)
    assert acts == [None, Action(heat, ['off'])]

    w1 = World([], [], None, False, True)
    w2, acts = update_temp_hist(w1, 98.3, 30, 0)
    assert w2 == World([[0, 98.3]], [[0, 30]], None, False, False)
    assert acts == [None, Action(fan, ['off'])]

def test_update_with_abnormal_temps_while_awaiting_previous_sms_confirmation_does_not_resend_sms():
    w1 = World([], [], 'heat?', False, False)
    w2, acts = update_temp_hist(w1, 90, 30, 0)
    assert w2 == World([[0, 90]], [[0, 30]], 'heat?', False, False)
    assert acts == [None, None]


def test_update_with_normal_temps_while_awaiting_previous_sms_confirmation_does_not_resend_sms():
    w1 = World([], [], 'heat?', False, False)
    w2, acts = update_temp_hist(w1, 98.4, 30, 0)
    assert w2 == World([[0, 98.4]], [[0, 30]], None, False, False)
    assert acts == [None, None]

def test_sms_confirmation_activates_device():
    w1 = World([[0, 40]], [[0, 30]], 'heat?', False, False)
    assert update_sms_in(w1, 'Y') == (World([[0, 40]], [[0, 30]], 'heat?', True, False),
                                      [Action(heat, ["on"])])

    w1 = World([[0, 150]], [[0, 30]], 'fan?', False, False)
    assert update_sms_in(w1, 'Y') == (World([[0, 150]], [[0, 30]], 'fan?', False, True),
                                      [Action(fan, ["on"])])

def test_sms_confirmation_ignored_if_device_already_activated():
    w1 = World([[0, 40]], [[0, 30]], 'heat?', True, False)
    assert update_sms_in(w1, 'Y') == (World([[0, 40]], [[0, 30]], 'heat?', True, False),
                                      [None])

def test_sms_refusal_means_no_device_activated():
    w1 = World([[0, 40]], [[0, 30]], 'heat?', True, False)
    assert update_sms_in(w1, 'N') == (World([[0, 40]], [[0, 30]], 'heat?', True, False),
                                      [None])

def test_sms_ignored_if_body_temp_already_ok():
    w1 = World([[0, 98.4]], [[0, 30]], 'heat?', False, False)
    assert update_sms_in(w1, 'N') == (World([[0, 98.4]], [[0, 30]], 'heat?', False, False),
                                      [None])

