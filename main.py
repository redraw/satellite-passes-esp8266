import os
import machine
import time
import urequests

from utils import load, save, log, unix_to_2000_epoch
from config import LED_PIN, API, NORAD_ID, LAT, LON, PASS_FILE, ONLY_VISIBLE

machine.Pin(2, machine.Pin.OUT, 0) # builtin led
led = machine.Pin(LED_PIN, machine.Pin.OUT, 0)

rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    log("Wake up.")


def query_next_pass():
    url = {"base": API, "lat": LAT, "lon": LON, "norad": NORAD_ID, "limit": 1}
    response = urequests.get("{base}/{norad}?lat={lat}&lon={lon}&limit={limit}".format(**url))
    log("[%s] HTTP %s" % (API, response.status_code))
    try:
        return response.json()[0]
    except:
        log(response.text)
        rtc.alarm(rtc.ALARM0, 60 * 60 * 1000) # 1h
        machine.deepsleep()


def schedule_next_pass():
    data = query_next_pass()
    save(PASS_FILE, data)
    log("Next pass: %s" % data["rise"]["utc_datetime"])
    return data


def display_pass(seconds):
    log("Satellite passing! %s seconds" % seconds)
    led.on()
    time.sleep(seconds)
    led.off()


# Get a scheduled pass
scheduled_pass = load(PASS_FILE) or schedule_next_pass()
countdown = unix_to_2000_epoch(scheduled_pass["rise"]["utc_timestamp"]) - time.time()

# If countdown less than 60s, display pass and reset
if countdown < 60:
    start = scheduled_pass["rise"]["utc_timestamp"]
    end = scheduled_pass["set"]["utc_timestamp"]
    if not ONLY_VISIBLE or scheduled_pass["visible"] and ONLY_VISIBLE:
        display_pass(end - start)
    os.remove(PASS_FILE)
    machine.reset()

# RTC resets at 71m. Sleep no more than 60m
keep_alive = 60 * 60
rtc_countdown = min(keep_alive, countdown)

# Give 5s to enter raw repl if needed
time.sleep(5)

log("Deep sleep for %s seconds" % rtc_countdown)
rtc.alarm(rtc.ALARM0, rtc_countdown * 1000)
machine.deepsleep()
