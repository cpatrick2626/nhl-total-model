from data.stats import get_team_stats, pace_factor

LEAGUE_AVG = 6.1
team_cache = get_team_stats()


def project_total(home, away):
    home_stats = team_cache.get(home)
    away_stats = team_cache.get(away)

    if not home_stats or not away_stats:
        return LEAGUE_AVG

    home_xg = (home_stats["goals_for"] * 0.6 + away_stats["goals_against"] * 0.4)
    away_xg = (away_stats["goals_for"] * 0.6 + home_stats["goals_against"] * 0.4)

    pace = pace_factor(home_stats, away_stats)

    return round((home_xg + away_xg) * pace, 2)
