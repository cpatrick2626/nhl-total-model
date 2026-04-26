def extract_best_market(game):
    """
    Extracts the best OVER total market from a game.
    Returns:
        {
            "odds": int,
            "line": float,
            "book": str
        }
    or None if no valid market found
    """

    # Safety check
    if not isinstance(game, dict):
        return None

    bookmakers = game.get("bookmakers", [])
    if not bookmakers:
        return None

    best = None

    for book in bookmakers:
        markets = book.get("markets", [])

        for m in markets:
            if m.get("key") != "totals":
                continue

            outcomes = m.get("outcomes", [])

            for o in outcomes:
                # We only care about OVER
                if o.get("name") != "Over":
                    continue

                price = o.get("price")
                point = o.get("point")

                # Skip invalid entries
                if price is None or point is None:
                    continue

                # First valid market
                if best is None:
                    best = {
                        "odds": price,
                        "line": point,
                        "book": book.get("title", "Unknown")
                    }
                    continue

                # Compare odds (higher is better for bettor)
                if price > best["odds"]:
                    best = {
                        "odds": price,
                        "line": point,
                        "book": book.get("title", "Unknown")
                    }

    return best