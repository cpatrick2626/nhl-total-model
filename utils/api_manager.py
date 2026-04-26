import datetime
from utils.cache import load_cache, save_cache

def fetch_with_cache(prefix, fetch_func, max_age=300):
    today = str(datetime.date.today())
    path = f"data_cache/{prefix}_{today}.json"

    cached = load_cache(path, max_age)
    if cached:
        return cached

    data = fetch_func()
    save_cache(path, data)
    return data