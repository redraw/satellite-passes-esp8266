import gc
gc.collect()

import time
import ntptime
import wifi
from utils import log

print("-"*80)
wifi.connect()
log("Before NTP update")
ntptime.settime()
log("After NTP update")
print("Chip clock:", time.localtime())
print("-"*80)
