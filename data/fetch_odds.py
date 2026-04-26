# data/fetch_odds.py

from data.api_manager import get_odds as api_get_odds


def get_odds(force_refresh=False):
    """
    Fetch NHL odds data using the centralized API manager.

    Returns:
        tuple:
            data (list): raw games data from API
            usage (dict): API usage info (used, remaining)
    """

    data, usage = api_get_odds(force_refresh=force_refresh)

    # Basic safety check
    if not isinstance(data, list):
        return [], usage

    return data, usage