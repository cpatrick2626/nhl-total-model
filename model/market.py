def extract_best_market(game):
    if "bookmakers" not in game:
        return None

    best = None

    for book in game.get("bookmakers", []):
        for m in book.get("markets", []):
            if m.get("key") == "totals":
                for o in m.get("outcomes", []):
                    if o.get("name") == "Over":
                        if not best or o["price"] > best["price"]:
                            best = {
                                "odds": o["price"],
                                "line": o["point"],
                                "book": book["title"]
                            }

    return best