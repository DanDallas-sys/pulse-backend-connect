import json
import time
import os

CACHE_FILE = "cache.json"
CACHE_TTL = 300

def load_cache():
    print("📂 LOADING CACHE FILE...")

    if not os.path.exists(CACHE_FILE):
        print("❌ CACHE FILE DOES NOT EXIST")
        return {}

    with open(CACHE_FILE, "r") as f:
        data = json.load(f)
        print("✅ CACHE FILE CONTENT:", data)
        return data


def save_cache(data):
    print("💾 SAVING CACHE:", data)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)


def get_cache(key):
    cache = load_cache()

    print("🔍 LOOKING FOR KEY:", key)

    data = cache.get(key)

    if not data:
        print("❌ KEY NOT FOUND")
        return None

    if time.time() - data["time"] > CACHE_TTL:
        print("⏳ CACHE EXPIRED")
        del cache[key]
        save_cache(cache)
        return None

    print("✅ CACHE HIT")
    return data["value"]


def set_cache(key, value):
    cache = load_cache()

    cache[key] = {
        "value": value,
        "time": time.time()
    }

    save_cache(cache)