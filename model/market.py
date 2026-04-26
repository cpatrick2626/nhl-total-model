def extract_best_market(game):
    best = None

    for book in game["bookmakers"]:
        for m in book["markets"]:
            if m["key"] == "totals":
                for o in m["outcomes"]:
                    if o["name"] == "Over":
                        if not best or o["price"] > best["price"]:
                            best = {
                                "odds": o["price"],
                                "line": o["point"],
                                "book": book["title"]
                            }

    return best