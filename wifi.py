import network
import time

from config import WIFI_SSID, WIFI_PASS

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        timeout = 5

        while not wlan.isconnected() and timeout > 0:
            timeout -= 1
            time.sleep(1)

    print('Network config:', wlan.ifconfig())
    return wlan
