import itertools

def generate_weights():
    options = [0.4, 0.5, 0.6]

    for o, d in itertools.product(options, options):
        if o + d <= 1:
            yield {
                "offense": o,
                "defense": d,
                "pace": 1 - (o + d)
            }