from data.api_manager import get_odds as api_get_odds


def get_odds(force_refresh=False):
    data, usage = api_get_odds(force_refresh=force_refresh)

    # ensure safe return
    if not isinstance(data, list):
        data = []

    return data, usage