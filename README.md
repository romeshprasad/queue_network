# Open Queueing Network Simulator

A modular, discrete-event simulation framework for open queueing networks in Python.

## Features

- ✅ **Jackson Networks**: Classical infinite capacity networks
- ✅ **Finite Capacity**: Networks with rejection/loss when queues are full
- ✅ **Multi-Server Queues**: Support for M/M/c/k configurations
- ✅ **Flexible Routing**: Probabilistic routing between queues
- ✅ **FIFO Scheduling**: First-In-First-Out service discipline
- ✅ **Comprehensive Statistics**: Waiting times, queue lengths, system times
- ✅ **Visualization**: Built-in plotting functions

## Project Structure

```
queueing_network/
├── agent.py              # Agent (customer/job) class
├── server.py             # Server (service resource) class
├── queue.py              # Queue (service station) class
├── queueing_network.py   # Main simulation engine
├── visualization.py      # Plotting and statistics functions
├── main.py              # Example usage scripts
└── README.md            # This file
```

## Module Descriptions

### `agent.py`
Defines the `Agent` class representing entities moving through the network.
- Tracks arrival time, service times, queue positions
- Generates exponentially distributed inter-arrival times

### `server.py`
Defines the `Server` class representing service resources.
- Manages busy/idle status
- Tracks currently served agent

### `queue.py`
Defines the `Queue` class representing service stations.
- Manages multiple parallel servers
- Handles waiting queue with optional capacity limits
- Generates exponentially distributed service times

### `queueing_network.py`
Main simulation engine implementing discrete-event simulation.
- Event scheduling using priority queue
- Handles arrivals, departures, and routing
- Logs comprehensive statistics
- Supports both infinite and finite capacity

### `visualization.py`
Functions for analyzing and visualizing results.
- Queue length over time plots
- Waiting time distributions
- System time analysis
- Formatted statistics output

### `main.py`
Example scripts demonstrating various network configurations.
- Jackson networks
- Finite capacity networks
- Complex routing patterns
- Multi-server systems

## Installation

### Requirements
```bash
pip install numpy matplotlib
```

### Usage

1. **Clone/download all module files** to the same directory

2. **Run examples**:
```bash
python main.py
```

3. **Use in your own code**:
```python
import numpy as np
from queueing_network import QueueingNetwork
from visualization import plot_queue_lengths, print_statistics

# Define network parameters
arrival_rate = 1.0
service_rates = [1.5, 2.0, 2.5]
num_servers = [1, 1, 1]
prob_matrix = [
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 1.0],
    [0.0, 0.0, 0.0]
]
max_time = 1000.0

# Create and run simulation
network = QueueingNetwork(
    arrival_rate=arrival_rate,
    service_rates=service_rates,
    num_servers=num_servers,
    prob_matrix=prob_matrix,
    max_time=max_time
)

agents_data = network.simulate()
stats = network.get_statistics()

# Visualize results
print_statistics(stats)
plot_queue_lengths(agents_data)
```

## Network Configuration

### Parameters

- **`arrival_rate`** (float): External arrival rate λ to first queue
- **`service_rates`** (list): Service rates μ for each queue
- **`num_servers`** (list): Number of parallel servers per queue
- **`prob_matrix`** (2D array): Routing probabilities
  - `prob_matrix[i][j]` = probability of moving from queue i to queue j
  - Each row should sum to 1.0
  - Exit system when routing to absorbing state (all zeros)
- **`max_time`** (float): Maximum simulation time
- **`capacities`** (list, optional): Maximum waiting queue size per queue
  - Default: `None` (infinite capacity)
  - Finite capacity causes rejection when full

### Routing Probability Matrix

Example for 3 queues in series:
```python
prob_matrix = [
    [0.0, 1.0, 0.0],  # Queue 0 → Queue 1 (100%)
    [0.0, 0.0, 1.0],  # Queue 1 → Queue 2 (100%)
    [0.0, 0.0, 0.0]   # Queue 2 → Exit
]
```

Example with branching:
```python
prob_matrix = [
    [0.0, 0.7, 0.3],  # Queue 0 → Queue 1 (70%) or Queue 2 (30%)
    [0.0, 0.0, 0.0],  # Queue 1 → Exit
    [0.0, 0.0, 0.0]   # Queue 2 → Exit
]
```

## Output Data

### Agents Data Array
The `simulate()` method returns a numpy array with columns:
1. **agent_id**: Unique identifier
2. **arrival_time**: Time of arrival at this queue
3. **service_start_time**: Time service began
4. **departure_time**: Time service completed
5. **server_id**: ID of server that provided service
6. **queue_id**: ID of the queue
7. **queue_length_on_arrival**: Number waiting when agent arrived

### Statistics Dictionary
The `get_statistics()` method returns:
- `num_served`: Total agents served
- `avg_waiting_time`: Mean time waiting for service
- `avg_service_time`: Mean time in service
- `avg_system_time`: Mean total time in queue
- `avg_queue_length`: Mean queue length
- `max_queue_length`: Maximum queue length observed

## Theoretical Background

### Jackson Networks
When capacity is infinite, this simulator implements classical Jackson networks:
- External arrivals follow Poisson process
- Service times are exponentially distributed
- Routing is Markovian (memoryless)
- Each queue operates as M/M/c queue

**Key Property**: Product-form solution exists for steady-state probabilities.

### Finite Capacity Networks
When capacity is finite, agents are **rejected** (lost) when queues are full:
- This is a **loss system** (not blocking)
- Rejected agents leave the system entirely
- Upstream queues are NOT blocked
- Product-form solution generally does NOT apply
- Simulation is required for analysis

---

## Theoretical Validation

The `theoretical_validation.py` file provides analytical solutions for comparison with simulation results. This is crucial for verifying simulator correctness.

### Supported Queue Types

| Queue Type | Class | Description | Use for Validation? |
|------------|-------|-------------|---------------------|
| **M/M/1** | `MM1Queue` | Single server, infinite capacity | ✅ Yes - Reliable |
| **M/M/1/k** | `MM1kQueue` | Single server, finite capacity k | ✅ Yes - Reliable |
| **M/M/c** | `MMcQueue` | c servers, infinite capacity | ✅ Yes - Reliable |
| **M/M/c/k** | `MMckQueue` | c servers, finite capacity k | ✅ Yes - Reliable |
| **Series** | `series` | Series of M/M/c queues | ✅ Yes - Now fixed |
| **Jackson Network** | `Jacksonnetwork` | Open network, infinite capacity | ✅ Yes - Now fixed |
| **Finite Jackson** | `Jacksonnetworkfinitecapacity` | Open network, finite capacity | ⚠️ Approximate only |

### Validation Process

**Step 1: Run Simulation**
```python
from queueing_network import QueueingNetwork
import numpy as np

# M/M/1 example
arrival_rate = 0.8
service_rate = 1.0
network = QueueingNetwork(
    arrival_rate=arrival_rate,
    service_rates=[service_rate],
    num_servers=[1],
    prob_matrix=[[0.0]],
    max_time=10000  # Long simulation for steady-state
)
agents_data = network.simulate()
stats = network.get_statistics()
```

**Step 2: Calculate Theoretical Values**
```python
from theoretical_validation import MM1Queue

theory = MM1Queue(arrival_rate=0.8, service_rate=1.0)
theory.calculate_measures()
theory.print_results()
```

**Step 3: Compare Results**
```python
sim_L = stats[0]['avg_queue_length']
theory_L = theory.Lq

print(f"Simulation Lq: {sim_L:.4f}")
print(f"Theoretical Lq: {theory_L:.4f}")
print(f"Difference: {abs(sim_L - theory_L)/theory_L * 100:.2f}%")
```

### Key Metrics for Comparison

- **L**: Average number of agents in system
- **Lq**: Average number of agents waiting in queue
- **Ls**: Average number of agents in service
- **W**: Average time in system
- **Wq**: Average waiting time in queue
- **Ws**: Average service time

### Validation Guidelines

**For Good Validation:**
1. **Run long simulations** (max_time ≥ 1000 for stable metrics)
2. **Ensure system is stable** (ρ < 1 for infinite capacity queues)
3. **Use multiple random seeds** to check consistency
4. **Expect 5-15% difference** due to:
   - Simulation transient period
   - Random variation
   - Finite simulation length

**Acceptable Tolerance:**
- **< 10% difference**: Excellent match
- **10-20% difference**: Acceptable (increase simulation time)
- **> 20% difference**: Investigate potential bug

### Validation Examples by Network Type

#### Example 1: M/M/1 Queue
```python
# Theoretical
theory = MM1Queue(arrival_rate=0.8, service_rate=1.0)
theory.calculate_measures()
# Expected: Lq = 3.2, Wq = 4.0

# Simulation equivalent
network = QueueingNetwork(
    arrival_rate=0.8,
    service_rates=[1.0],
    num_servers=[1],
    prob_matrix=[[0.0]],
    max_time=10000
)
```

#### Example 2: M/M/c Queue
```python
# Theoretical
theory = MMcQueue(arrival_rate=2.0, service_rate=1.0, c=3)
theory.calculate_measures()

# Simulation equivalent
network = QueueingNetwork(
    arrival_rate=2.0,
    service_rates=[1.0],
    num_servers=[3],  # 3 servers
    prob_matrix=[[0.0]],
    max_time=10000
)
```

#### Example 3: Jackson Network (Series)
```python
# Theoretical
theory = Jacksonnetwork(
    arrival_rate=1.0,
    service_rate=[1.5, 2.0, 2.5],
    num_servers=[1, 1, 1],
    prob_matrix=[[0.0, 1.0, 0.0],
                 [0.0, 0.0, 1.0],
                 [0.0, 0.0, 0.0]]
)
data, eff_arrival, rho = theory.calculate_measures()

# Simulation equivalent
network = QueueingNetwork(
    arrival_rate=1.0,
    service_rates=[1.5, 2.0, 2.5],
    num_servers=[1, 1, 1],
    prob_matrix=[[0.0, 1.0, 0.0],
                 [0.0, 0.0, 1.0],
                 [0.0, 0.0, 0.0]],
    max_time=10000
)
```

#### Example 4: M/M/1/k (Finite Capacity)
```python
# Theoretical
theory = MM1kQueue(arrival_rate=0.9, service_rate=1.0, k=10)
theory.calculate_measures()

# Simulation equivalent
network = QueueingNetwork(
    arrival_rate=0.9,
    service_rates=[1.0],
    num_servers=[1],
    prob_matrix=[[0.0]],
    max_time=10000,
    capacities=[10]  # Finite capacity
)
```

### Important Notes

**✅ Reliable for Validation:**
- M/M/1, M/M/c, M/M/1/k, M/M/c/k (single queue)
- Jackson networks with infinite capacity
- Series queues (after bug fixes)

**⚠️ Use with Caution:**
- Finite capacity Jackson networks (theory is approximate)
- Networks with very high utilization (ρ > 0.95)
- Short simulation runs (transient effects)

**❌ Not Suitable:**
- Networks with blocking (not rejection)
- Non-exponential service times
- Priority queues
- Time-varying arrival rates

### Bug Fixes in theoretical_validation.py

The following bugs have been fixed:
1. **Series class**: Dictionary indexing now starts from 0 (was 1)
2. **Jackson network**: Utilization formula corrected with proper parentheses
3. **Jackson network**: Traffic equations now solved using linear algebra
4. **All network classes**: Data dictionary keys now match stage indices

These fixes ensure theoretical calculations are accurate for validation purposes.

## Future Extensions

Potential enhancements (not yet implemented):
- [ ] Blocking (agent holds server when downstream is full)
- [ ] Priority scheduling policies
- [ ] Non-exponential service times
- [ ] Batch arrivals
- [ ] Time-varying arrival rates
- [ ] Closed queueing networks
- [ ] Confidence intervals
- [ ] Warm-up period detection

## Example Output

```
Starting simulation: max_time=100.0
Network configuration: 3 queues
------------------------------------------------------------
Time 0.234: Agent 0 ARRIVES at Queue 0, Server: 0
Time 1.456: Agent 0 DEPARTS from Queue 0, Server: 0
Time 1.456: Agent 0 ARRIVES at Queue 1, Server: 0
...
------------------------------------------------------------
Simulation complete: 95 departures recorded
Rejected agents: 0

======================================================================
SIMULATION STATISTICS
======================================================================

Queue 0:
  Agents Served:        32
  Avg Waiting Time:     0.0234
  Avg Service Time:     0.6543
  Avg System Time:      0.6777
  Avg Queue Length:     0.0312
  Max Queue Length:     2

Queue 1:
  Agents Served:        32
  Avg Waiting Time:     0.0156
  Avg Service Time:     0.6234
  Avg System Time:      0.6390
  Avg Queue Length:     0.0234
  Max Queue Length:     1
...
======================================================================
```

## License

Open source - feel free to use and modify for research or educational purposes.

## Contact

For questions or contributions, please contact the repository maintainer.
