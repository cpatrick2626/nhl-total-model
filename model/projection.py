from data.stats import get_team_stats, pace_factor

LEAGUE_AVG = 6.1

team_cache = get_team_stats()

def project_total(home, away, weights=None):
    home_stats = team_cache.get(home, {})
    away_stats = team_cache.get(away, {})

    if not home_stats or not away_stats:
        return LEAGUE_AVG

    w_off = weights["offense"] if weights else 0.55
    w_def = weights["defense"] if weights else 0.35

    home_off = home_stats["goals_for"]
    away_off = away_stats["goals_for"]

    home_def = home_stats["goals_against"]
    away_def = away_stats["goals_against"]

    pace = pace_factor(home_stats, away_stats)

    home_xg = (home_off * w_off + away_def * w_def) * pace
    away_xg = (away_off * w_off + home_def * w_def) * pace

    return round(home_xg + away_xg, 2)