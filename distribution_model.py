import random

class DistributionModel:
    def __init__(self, distribution="constant", value=1.0, params=None):
        self.distribution = distribution
        self.value = value
        self.params = params

    def sample(self):
        if self.distribution == "constant":
            return self.value

        elif self.distribution == "normal":
            mu = self.params.get("mu", 1.0)
            sigma = self.params.get("sigma", 0.1)
            return max(0, random.gauss(mu, sigma))

        elif self.distribution == "uniform":
            low = self.params.get("low", 0.5)
            high = self.params.get("high", 1.5)
            return random.uniform(low, high)

        elif self.distribution == "exponential":
            lam = self.params.get("lambda", 1.0)
            return random.expovariate(lam)

        else:
            raise ValueError(f"Unknown distribution: {self.distribution}")