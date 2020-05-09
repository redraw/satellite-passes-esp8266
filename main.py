import os
import machine
import time
import urequests

from utils import load, save, log, unix_to_2000_epoch
from config import LED_PIN, API, NORAD_ID, LAT, LON, PASS_FILE, ONLY_VISIBLE

rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

machine.Pin(2, machine.Pin.OUT, 0) # builtin
led = machine.Pin(LED_PIN, machine.Pin.OUT, 0)

def query_next_pass():
    response = urequests.get("%s/%s?lat=%s&lon=%s&limit=1" % (API, NORAD_ID, LAT, LON))
    log("HTTP [%s] satellites.fly.dev" % response.status_code)
    if response.status_code >= 400:
        log(response.text)
        rtc.alarm(rtc.ALARM0, 60 * 60 * 1000) # 1 hour
        machine.deepsleep()
    return response.json()[0]

def schedule_next_pass():
    data = query_next_pass()
    when = unix_to_2000_epoch(data["start"]["timestamp"])
    save(PASS_FILE, data)
    timeout = when - time.time()
    log("Enter deep sleep. Next pass: %s" % data["start"]["datetime"])
    log("Timeout: %s seconds" % timeout)
    rtc.alarm(rtc.ALARM0, timeout * 1000)
    machine.deepsleep()

def display_pass(seconds):
    log("ISS pass! Displaying for %s seconds" % seconds)
    led.on()
    time.sleep(seconds)
    led.off()

# Load scheduled pass
scheduled_pass = load(PASS_FILE)

# If woke up, and there's a pass, display pass
if scheduled_pass and machine.reset_cause() == machine.DEEPSLEEP_RESET:
    log("Wake up.")
    start = scheduled_pass["start"]["timestamp"]
    end = scheduled_pass["end"]["timestamp"]
    duration_from_now = unix_to_2000_epoch(end) - time.time()
    if duration_from_now > 0:
        if not ONLY_VISIBLE or schedule_next_pass["visible"] and ONLY_VISIBLE:
            display_pass(duration_from_now)
    else:
        log("Missed pass, off %s" % duration_from_now)
    os.remove(PASS_FILE)

# Finally schedule next pass
schedule_next_pass()