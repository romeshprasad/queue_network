import math
import numpy as np


class MMQueue:
    def __init__(self, arrival_rate, service_rate):
        self.lambda_ = arrival_rate
        self.mu = service_rate
        self.rho = self.lambda_ / self.mu

    def calculate_measures(self):
        pass

    def print_results(self):
        print(f"L: {self.L:.4f}")
        print(f"Lq: {self.Lq:.4f}")
        print(f"Ls: {self.Ls:.4f}")
        print(f"W: {self.W:.4f}")
        print(f"Wq: {self.Wq:.4f}")
        print(f"Ws: {self.Ws:.4f}")

class MM1Queue(MMQueue):
    def calculate_measures(self):
        self.L = self.rho / (1 - self.rho)
        self.Lq = self.rho**2 / (1 - self.rho)
        self.Ls = self.rho
        self.W = 1 / (self.mu - self.lambda_)
        self.Wq = self.rho / (self.mu - self.lambda_)
        self.Ws = 1 / self.mu

class MM1kQueue(MMQueue):
    def __init__(self, arrival_rate, service_rate, k):
        super().__init__(arrival_rate, service_rate)
        self.k = k

    def calculate_measures(self):
        if self.rho == 1:
            p0 = 1 / (self.k + 1)
        else:
            p0 = (1 - self.rho) / (1 - self.rho**(self.k + 1))
        
        self.L = self.rho * (1 - (self.k + 1) * self.rho**self.k + self.k * self.rho**(self.k + 1)) / ((1 - self.rho) * (1 - self.rho**(self.k + 1)))
        self.Lq = self.L - self.rho * (1 - p0)
        self.Ls = self.L - self.Lq
        self.lambda_eff = self.lambda_ * (1 - self.rho**self.k * p0)
        self.W = self.L / self.lambda_eff
        self.Wq = self.Lq / self.lambda_eff
        self.Ws = 1 / self.mu

class MMcQueue(MMQueue):
    def __init__(self, arrival_rate, service_rate, c):
        super().__init__(arrival_rate, service_rate)
        self.c = c
        self.rho = self.lambda_ / (self.c * self.mu)

    def calculate_measures(self):
        r = self.lambda_ / self.mu
        p0 = 1 / (sum(r**n / math.factorial(n) for n in range(self.c)) + 
                   (r**self.c / math.factorial(self.c)) * (1 / (1 - self.rho)))
        
        self.Lq = (r**self.c * self.rho * p0) / (math.factorial(self.c) * (1 - self.rho)**2)
        self.L = self.Lq + r
        self.Ls = r
        self.W = self.L / self.lambda_
        self.Wq = self.Lq / self.lambda_
        self.Ws = 1 / self.mu

class MMckQueue(MMQueue):
    def __init__(self, arrival_rate, service_rate, c, k):
        super().__init__(arrival_rate, service_rate)
        self.c = c
        self.k = k
        self.rho = self.lambda_ / (self.c * self.mu)

    def calculate_measures(self):
        if self.c == 1:
            # If c = 1, use M/M/1/k calculations
            mm1k = MM1kQueue(self.lambda_, self.mu, self.k)
            mm1k.calculate_measures()
            self.L = mm1k.L
            self.Lq = mm1k.Lq
            self.Ls = mm1k.Ls
            self.W = mm1k.W
            self.Wq = mm1k.Wq
            self.Ws = mm1k.Ws
            self.lambda_eff = mm1k.lambda_eff
        else:
            p0 = self._calculate_p0()
            pn = self._calculate_pn(p0)
            
            self.L = sum(n * pn[n] for n in range(self.k + 1))
            self.Lq = sum((n - self.c) * pn[n] for n in range(self.c + 1, self.k + 1))
            self.Ls = self.L - self.Lq
            self.lambda_eff = self.lambda_ * (1 - pn[self.k])
            self.W = self.L / self.lambda_eff
            self.Wq = self.Lq / self.lambda_eff
            self.Ws = 1 / self.mu

    def _calculate_p0(self):
        sum1 = sum((self.lambda_ / self.mu) ** n / math.factorial(n) for n in range(self.c))
        sum2 = ((self.lambda_ / self.mu) ** self.c / math.factorial(self.c)) * sum((self.lambda_ / (self.c * self.mu)) ** n for n in range(self.k - self.c + 1))
        return 1 / (sum1 + sum2)

    def _calculate_pn(self, p0):
        pn = {}
        for n in range(self.k + 1):
            if n <= self.c:
                pn[n] = (self.lambda_ / self.mu) ** n * p0 / math.factorial(n)
            else:
                pn[n] = (self.lambda_ / self.mu) ** n * p0 / (self.c ** (n - self.c) * math.factorial(self.c))
        return pn

class series():
    def __init__(self, arrival_rate, service_rate, num_servers):
        self.lambda_ = arrival_rate
        self.mu = service_rate 
        self.c = num_servers
        self.rho = [self.lambda_/ (self.mu[i]*self.c[i]) for i in range(len(self.mu))]
        self.data = {stages:[] for stages in range(len(self.c))}  # FIXED: was range(1, len(self.c))

    def calculate_measures(self):
        for stage in range(len(self.c)):
            if self.c[stage] == 1:
                self.L = self.rho[stage] / (1 - self.rho[stage])
                self.Lq = self.rho[stage]**2 / (1 - self.rho[stage])
                self.Ls = self.rho[stage]
                self.W = 1 / (self.mu[stage] - self.lambda_)
                self.Wq = self.rho[stage] / (self.mu[stage] - self.lambda_)
                self.Ws = 1 / self.mu[stage]
            else:
                r = self.lambda_ / self.mu[stage]
                p0 = 1 / (sum(r**n / math.factorial(n) for n in range(self.c[stage])) + 
                        (r**self.c[stage] / math.factorial(self.c[stage])) * (1 / (1 - self.rho[stage])))
                
                self.Lq = (r**self.c[stage] * self.rho[stage] * p0) / (math.factorial(self.c[stage]) * (1 - self.rho[stage])**2)
                self.L = self.Lq + r
                self.Ls = r
                self.W = self.L / self.lambda_
                self.Wq = self.Lq / self.lambda_
                self.Ws = 1 / self.mu[stage]

            self.data[stage] = [self.L, self.Lq, self.Ls, self.W, self.Wq, self.Ws]  # FIXED: was stage + 1
        
        return self.data
    
    def print_results(self):
        print(f"Utilization factor (rho): {self.rho}")
        print(f"L: {self.L:.4f}")
        print(f"Lq: {self.Lq:.4f}")
        print(f"Ls: {self.Ls:.4f}")
        print(f"W: {self.W:.4f}")
        print(f"Wq: {self.Wq:.4f}")
        print(f"Ws: {self.Ws:.4f}")

class Jacksonnetwork():
    def __init__(self, arrival_rate, service_rate, num_servers, prob_matrix, external_arrivals=None) -> None:
        self.lambda_ = arrival_rate
        self.mu = service_rate
        self.c = num_servers
        self.p_mat = prob_matrix
        if external_arrivals is None:
            external_arrivals = [0] * len(service_rate)
        self.external_arrivals = external_arrivals
        self.external_arrivals[0] = self.lambda_
        self.data = {stages:[] for stages in range(len(self.c))}  # FIXED: was range(1, len(self.c))

    def effective_arrival_rates(self):
        """
        Solve the traffic equations: λ = r + λP
        where λ is vector of effective arrival rates
        r is vector of external arrivals
        P is the routing probability matrix
        
        FIXED: Use linear algebra solution instead of iteration
        """
        n = len(self.mu)
        r = np.array(self.external_arrivals)
        P = np.array(self.p_mat)
        
        # Solve: λ = r + λP  =>  λ(I - P) = r  =>  λ = r(I - P)^(-1)
        I = np.eye(n)
        try:
            effective_arrival = np.linalg.solve((I - P.T), r)
        except np.linalg.LinAlgError:
            # If singular, fall back to iterative method
            effective_arrival = np.zeros(n)
            for i in range(n):
                effective_arrival[i] = self.external_arrivals[i]
            
            convergence_threshold = 1e-6
            max_iterations = 1000
            for _ in range(max_iterations):
                previous_arrival = effective_arrival.copy()
                for i in range(n):
                    effective_arrival[i] = self.external_arrivals[i] + sum(previous_arrival[j] * self.p_mat[j][i] for j in range(n))
                
                if np.all(np.abs(effective_arrival - previous_arrival) < convergence_threshold):
                    break
        
        return effective_arrival
    
    def utilization_factor(self, effective_arrival):
        rho = np.zeros(len(self.mu))
        for i in range(len(self.mu)):
            if self.c[i] == 1:
                rho[i] = effective_arrival[i]/self.mu[i]
            else:
                rho[i] = effective_arrival[i]/(self.c[i] * self.mu[i])  # FIXED: Added parentheses
        return rho
    
    def calculate_measures(self):
        self.effective_arrival = self.effective_arrival_rates()
        self.rho = self.utilization_factor(self.effective_arrival)
        for stage in range(len(self.mu)):
            if self.c[stage] == 1:
                self.L = self.rho[stage] / (1 - self.rho[stage])
                self.Lq = self.rho[stage]**2 / (1 - self.rho[stage])
                self.Ls = self.rho[stage]
                self.W = 1 / (self.mu[stage] - self.effective_arrival[stage])
                self.Wq = self.rho[stage] / (self.mu[stage] - self.effective_arrival[stage])
                self.Ws = 1 / self.mu[stage]
            else:
                r = self.effective_arrival[stage]/ self.mu[stage]
                p0 = 1 / (sum(r**n / math.factorial(n) for n in range(self.c[stage])) + 
                        (r**self.c[stage] / math.factorial(self.c[stage])) * (1 / (1 - self.rho[stage])))
                self.Lq = (r**self.c[stage] * self.rho[stage] * p0) / (math.factorial(self.c[stage]) * (1 - self.rho[stage])**2)
                self.L = self.Lq + r
                self.Ls = r
                self.W = self.L / self.effective_arrival[stage]
                self.Wq = self.Lq / self.effective_arrival[stage]
                self.Ws = 1 / self.mu[stage]
            
            self.data[stage] = [self.L, self.Lq, self.Ls, self.W, self.Wq, self.Ws]  # FIXED: was stage + 1
            
        return self.data, self.effective_arrival, self.rho
    
class Jacksonnetworkfinitecapacity():
    """
    NOTE: This class provides APPROXIMATE results for finite capacity networks.
    It does not account for blocking/rejection effects on effective arrival rates.
    Use with caution for validation purposes.
    """
    def __init__(self, arrival_rate, service_rate, num_servers, prob_matrix, capacity) -> None:
        self.lambda_ = arrival_rate
        self.mu = service_rate
        self.c = num_servers
        self.p_mat = prob_matrix
        self.k = capacity
        self.data = {stages:[] for stages in range(len(self.c))}  # FIXED: was range(1, len(self.c))

    def effective_arrival_rates(self):
        """
        Simplified calculation - does NOT account for blocking/rejection.
        For accurate finite capacity validation, use simulation.
        """
        effective_arrival = np.zeros(len(self.mu))
        effective_arrival[0] = self.lambda_

        for i in range(1, len(self.mu)):
            for j in range(len(self.mu)):
                effective_arrival[i] += effective_arrival[j] * self.p_mat[j][i]        
        return effective_arrival
    
    def utilization_factor(self, effective_arrival):
        rho = np.zeros(len(self.mu))
        for i in range(len(self.mu)):
            if self.c[i] == 1:
                rho[i] = effective_arrival[i]/self.mu[i]
            else:
                rho[i] = effective_arrival[i]/ (self.c[i] * self.mu[i])
        return rho
    
    def calculate_measures(self):
        self.effective_arrival = self.effective_arrival_rates()
        self.rho = self.utilization_factor(self.effective_arrival)
        for stage in range(len(self.mu)):
            if self.c[stage] == 1:
                if self.rho[stage] == 1:
                    p0 = 1 / (self.k[stage] + 1)
                else:
                    p0 = (1 - self.rho[stage]) / (1 - self.rho[stage]**(self.k[stage] + 1))
                
                self.L = self.rho[stage] * (1 - (self.k[stage] + 1) * self.rho[stage]**self.k[stage] + self.k[stage] * self.rho[stage]**(self.k[stage] + 1)) / ((1 - self.rho[stage]) * (1 - self.rho[stage]**(self.k[stage] + 1)))
                self.Lq = self.L - self.rho[stage] * (1 - p0)
                self.Ls = self.L - self.Lq
                self.lambda_eff = self.effective_arrival[stage] * (1 - self.rho[stage]**self.k[stage] * p0)
                self.W = self.L / self.lambda_eff
                self.Wq = self.Lq / self.lambda_eff
                self.Ws = 1 / self.mu[stage]
            else:
                p0 = self._calculate_p0(stage)
                pn = self._calculate_pn(p0, stage)
                
                self.L = sum(n * pn[n] for n in range(self.k[stage] + 1))
                self.Lq = sum((n - self.c[stage]) * pn[n] for n in range(self.c[stage] + 1, self.k[stage] + 1))
                self.Ls = self.L - self.Lq
                self.lambda_eff = self.effective_arrival[stage] * (1 - pn[self.k[stage]])
                self.W = self.L / self.lambda_eff
                self.Wq = self.Lq / self.lambda_eff
                self.Ws = 1 / self.mu[stage]
            
            self.data[stage] = [self.L, self.Lq, self.Ls, self.W, self.Wq, self.Ws, p0]  # FIXED: was stage + 1
            
        return self.data, self.effective_arrival, self.rho

    def _calculate_p0(self, stage):
        sum1 = sum((self.effective_arrival[stage]/ self.mu[stage]) ** n / math.factorial(n) for n in range(self.c[stage]))
        sum2 = ((self.effective_arrival[stage]/ self.mu[stage]) ** self.c[stage] / math.factorial(self.c[stage])) * sum((self.effective_arrival[stage] / (self.c[stage] * self.mu[stage])) ** n for n in range(self.k[stage]- self.c[stage] + 1))
        return 1 / (sum1 + sum2)

    def _calculate_pn(self, p0, stage):
        pn = {}
        for n in range(self.k[stage] + 1):
            if n <= self.c[stage]:
                pn[n] = (self.effective_arrival[stage] / self.mu[stage]) ** n * p0 / math.factorial(n)
            else:
                pn[n] = (self.effective_arrival[stage] / self.mu[stage]) ** n * p0 / (self.c[stage] ** (n - self.c[stage]) * math.factorial(self.c[stage]))
        return pn

def analyze_queue(queue_type, *args):
    queue = queue_type(*args)
    queue.calculate_measures()
    print(f"\n{queue_type.__name__} Results:")
    queue.print_results()

# Example usage
if __name__ == "__main__":
    arrival_rate = 1
    service_rates = [1.5, 1.5, 2]
    num_servers = [1, 1, 1]
    prob_matrix = [[0.0, 1, 0], [0, 0.0, 1], [0.0, 0.0, 0.0]]
    capacity = [5,10,15]

    # Test basic queues
    print("="*60)
    print("BASIC QUEUE VALIDATION")
    print("="*60)
    
    analyze_queue(MM1Queue, 0.8, 1.0)
    analyze_queue(MMcQueue, 2.0, 1.0, 3)

    # Test Jackson network
    print("\n" + "="*60)
    print("JACKSON NETWORK VALIDATION")
    print("="*60)
    x = Jacksonnetwork(arrival_rate, service_rates, num_servers, prob_matrix, external_arrivals=None)
    data, eff_arrival, rho = x.calculate_measures()
    print(f"\nEffective Arrival Rates: {eff_arrival}")
    print(f"Utilization Factors: {rho}")
    print(f"\nQueue Statistics:")
    for stage, metrics in data.items():
        print(f"  Stage {stage}: L={metrics[0]:.4f}, Lq={metrics[1]:.4f}, W={metrics[3]:.4f}, Wq={metrics[4]:.4f}")
