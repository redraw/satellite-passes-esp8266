import os, time, ujson
from config import LOG_FILE

LOG_ROTATE = 256 * 1024

def try_stat(fn):
    try:
        return os.stat(fn)
    except OSError:
        pass

def save(fn, data):
    with open(fn, "w") as f:
        f.write(ujson.dumps(data))

def load(fn):
    stat = try_stat(fn)
    if stat:
        with open(fn) as f:
            return ujson.loads(f.read())

def unix_to_2000_epoch(ts):
    return ts - 946684800

def log(text):
    stat = try_stat(LOG_FILE)
    mode = 'a' if stat and stat[6] < LOG_ROTATE else 'w'
    with open(LOG_FILE, mode) as f:
        line = "%s %s\n" % (str(time.localtime()), text)
        f.write(line)
