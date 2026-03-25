import time

cache_store = {}
CACHE_TTL = 300  # 5 minutes

def get_cache(key):
    data = cache_store.get(key)

    if not data:
        return None

    if time.time() - data["time"] > CACHE_TTL:
        del cache_store[key]
        return None

    return data["value"]

def set_cache(key, value):
    cache_store[key] = {
        "value": value,
        "time": time.time()
    }