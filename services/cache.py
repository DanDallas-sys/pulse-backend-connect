import json
import time
import os

CACHE_FILE = "cache.json"
CACHE_TTL = 300

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)

def get_cache(key):
    cache = load_cache()
    data = cache.get(key)

    if not data:
        return None

    if time.time() - data["time"] > CACHE_TTL:
        del cache[key]
        save_cache(cache)
        return None

    return data["value"]

def set_cache(key, value):
    cache = load_cache()
    cache[key] = {
        "value": value,
        "time": time.time()
    }
    save_cache(cache)