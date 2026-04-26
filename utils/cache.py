import json, os, time

def load_cache(path, max_age=300):
    if not os.path.exists(path):
        return None
    
    if time.time() - os.path.getmtime(path) > max_age:
        return None
    
    with open(path, "r") as f:
        return json.load(f)

def save_cache(path, data):
    with open(path, "w") as f:
        json.dump(data, f)