import time

cache = {}
CACHE_TTL = 300

def get_cache(key):
    cached = cache.get(key)

    if cached:
        if time.time() - cached["timestamp"] < CACHE_TTL:
            return cached["data"]

    return None


def set_cache(key, data):
    cache[key] = {
        "data": data,
        "timestamp": time.time()
    }