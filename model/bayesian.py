class WeightUpdater:
    def __init__(self):
        self.weights = {
            "offense": 0.55,
            "defense": 0.35,
            "pace": 0.10
        }

    def update(self, error):
        lr = 0.05

        if error > 0:
            self.weights["offense"] += lr
        else:
            self.weights["defense"] += lr

        total = sum(self.weights.values())
        for k in self.weights:
            self.weights[k] /= total

        return self.weights
