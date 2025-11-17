# Open Queueing Network Simulator

A modular, discrete-event simulation framework for open queueing networks in Python with support for multi-class systems.

## Features

- **Jackson Networks**: Classical infinite capacity networks
- **Finite Capacity**: Networks with rejection/loss when queues are full
- **Multi-Server Queues**: Support for M/M/c/k configurations
- **Multi-Class Support**: Different customer categories with distinct routing and service rates
- **Flexible Routing**: Probabilistic routing between queues (category-specific)
- **FIFO Scheduling**: First-In-First-Out service discipline
- **Comprehensive Statistics**: Time-averaged and customer-averaged metrics with Little's Law verification
- **Visualization**: Built-in plotting functions
- **YAML Configuration**: Easy-to-use configuration files for complex scenarios

## Project Structure
```
queueing_network/
├── agent.py              # Agent (customer/job) class
├── server.py             # Server (service resource) class
├── queue.py              # Queue (service station) class
├── queueing_network.py   # Main simulation engine
├── config_loader.py      # YAML configuration loader and validator
├── visualization.py      # Plotting and statistics functions
├── main.py               # This is legacy: Example usage scripts
├── run_config.py         # Run simulations from config files
├── configs               # Folder consisting of differnt example
```

## Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Quick Start

1. **Clone/download all module files** to the same directory

2. **Run multi-class example from config file**:
```bash
python run_config.py
```

<!-- 3. **Run built-in examples**:
```bash
python main.py
``` -->

---

## 🆕 Multi-Class Queueing Networks

### What are Multi-Class Networks?

Multi-class networks allow you to simulate systems where different types of entities (customers, jobs, parts) have:
- **Different routing paths** through the network
- **Different service rates** at each queue
- **Different arrival probabilities**

**Real-world examples:**
- **Manufacturing**: Express parts (fast track), standard parts, bulk orders
- **Healthcare**: Emergency patients, scheduled appointments, walk-ins
- **Call centers**: VIP customers, regular customers, technical support
- **Logistics**: Priority shipping, standard shipping, economy shipping
---

## Using Configuration Files

### Basic Usage

Create a YAML configuration file and run:
```python
from queueing_network import QueueingNetwork
from visualization import print_statistics
import numpy as np

np.random.seed(42)

# Load and run simulation
network = QueueingNetwork('my_config.yaml')
agents_data = network.simulate()
stats = network.get_statistics()

# Display results
print_statistics(stats)

# Get per-category statistics
stats_by_category = network.get_statistics_by_category()
```

To run a simple example:
```bash
python run_config.py  # Uses config.yaml by default
```

There are more examples inside the configs folder.

---

### Configuration File Structure

A multi-class configuration file has four main sections:
```yaml
network:
  num_queues: 3
  max_time: 1000.0

queues:
  - queue_id: 0
    num_servers: 2
    capacity: inf
  - queue_id: 1
    num_servers: 3
    capacity: 10
  - queue_id: 2
    num_servers: 2
    capacity: inf

categories:
  express:
    arrival_probability: 0.3
    service_rates: [2.0, 2.5, 3.0]
    routing_matrix:
      - [0.0, 0.0, 1.0]  # Q0 -> Q2 (skip Q1)
      - [0.0, 0.0, 1.0]  # Q1 -> Q2
      - [0.0, 0.0, 0.0]  # Q2 -> Exit
  
  standard:
    arrival_probability: 0.5
    service_rates: [1.5, 2.0, 2.5]
    routing_matrix:
      - [0.0, 1.0, 0.0]  # Q0 -> Q1 (normal flow)
      - [0.0, 0.0, 1.0]  # Q1 -> Q2
      - [0.0, 0.0, 0.0]  # Q2 -> Exit
  
  bulk:
    arrival_probability: 0.2
    service_rates: [1.2, 1.5, 2.0]
    routing_matrix:
      - [0.0, 1.0, 0.0]  # Q0 -> Q1
      - [0.2, 0.0, 0.8]  # Q1 -> Q0 (20% rework) or Q2 (80%)
      - [0.0, 0.0, 0.0]  # Q2 -> Exit

arrivals:
  external_arrival_rate: 3.0
  arrival_queue: 0
```

---

### Configuration Sections Explained

#### 1. **Network Section**
```yaml
network:
  num_queues: 3        # Total number of queues in the network
  max_time: 1000.0     # Simulation duration
```

#### 2. **Queues Section**
Define each queue's characteristics:
```yaml
queues:
  - queue_id: 0           # Unique queue identifier (0 to num_queues-1)
    num_servers: 2        # Number of parallel servers
    capacity: inf         # Max waiting queue size ('inf' or integer)
```

**Note**: Service rates are specified per category (see below), not in the queues section.

#### 3. **Categories Section**
Define each customer class:
```yaml
categories:
  express:                      # Category name (user-defined)
    arrival_probability: 0.3    # Fraction of arrivals (must sum to 1.0)
    service_rates: [2.0, 2.5, 3.0]  # Service rate at each queue
    routing_matrix:             # Routing probabilities between queues
      - [0.0, 0.0, 1.0]        # From Q0: go to Q2 with prob 1.0
      - [0.0, 0.0, 1.0]        # From Q1: go to Q2 with prob 1.0
      - [0.0, 0.0, 0.0]        # From Q2: exit system
```

**Key Rules:**
- All `arrival_probability` values must sum to **exactly 1.0**
- Each `service_rates` list must have `num_queues` elements
- Each `routing_matrix` must be `num_queues × num_queues`
- Each row in `routing_matrix` can sum to ≤ 1.0 (remainder = exit probability)
- Category names are user-defined strings (use meaningful names)

#### 4. **Arrivals Section**
```yaml
arrivals:
  external_arrival_rate: 3.0  # Total arrival rate (λ) to the system
  arrival_queue: 0            # Queue where external arrivals enter
```

---

### Example Configurations

#### Example 1: Single-Class Network (Backwards Compatible)

If you only want one category:
```yaml
network:
  num_queues: 2
  max_time: 1000.0

queues:
  - queue_id: 0
    num_servers: 1
    capacity: inf
  - queue_id: 1
    num_servers: 1
    capacity: inf

categories:
  standard:
    arrival_probability: 1.0  # 100% of arrivals
    service_rates: [1.5, 2.0]
    routing_matrix:
      - [0.0, 1.0]
      - [0.0, 0.0]

arrivals:
  external_arrival_rate: 1.0
  arrival_queue: 0
```

#### Example 2: Priority Fast-Track System
```yaml
categories:
  vip:
    arrival_probability: 0.2
    service_rates: [3.0, 4.0, 5.0]  # Faster service
    routing_matrix:
      - [0.0, 0.0, 1.0]  # Skip queue 1 (fast track)
      - [0.0, 0.0, 1.0]
      - [0.0, 0.0, 0.0]
  
  regular:
    arrival_probability: 0.8
    service_rates: [1.5, 2.0, 2.5]  # Normal service
    routing_matrix:
      - [0.0, 1.0, 0.0]  # Go through all queues
      - [0.0, 0.0, 1.0]
      - [0.0, 0.0, 0.0]
```

#### Example 3: Manufacturing with Rework
```yaml
categories:
  first_pass:
    arrival_probability: 1.0
    service_rates: [2.0, 2.5]
    routing_matrix:
      - [0.0, 1.0]      # Q0 -> Q1
      - [0.1, 0.0]      # Q1 -> Q0 (10% rework) or exit (90%)
```

---

### Configuration Validation

The simulator automatically validates your configuration and provides helpful error messages:
```
✗ Category arrival probabilities sum to 0.8, must sum to 1.0
✗ Queue 0: 'num_servers' must be positive integer, got: 0
✗ Category 'express': routing_matrix row 0 sums to 1.2 > 1.0
✗ Missing required section: 'arrivals'
```

If validation passes, you'll see:
```
✓ Configuration loaded from: config.yaml
✓ Configuration validation passed
```

---

## Statistics Output

### Time-Averaged Metrics (NEW)

The simulator now tracks **time-weighted** statistics:

- **L**: Average number of customers in system (waiting + in service)
- **Lq**: Average number of customers in queue (waiting only)
- **Ls**: Average number of customers in service
- **ρ**: Server utilization (fraction of time servers are busy)

### Customer-Averaged Metrics

- **W**: Average time in system
- **Wq**: Average waiting time in queue
- **Ws**: Average service time

### Throughput & Loss

- **λ_eff**: Effective arrival rate (accepted arrivals per time unit)
- **P_loss**: Loss/rejection probability (for finite capacity queues)

### Little's Law Verification

The simulator automatically verifies Little's Law:
- **L = λ_eff × W** (should be ≈ 1.0)
- **Lq = λ_eff × Wq** (should be ≈ 1.0)

Ratios within 10% are marked ✓, outside 10% are marked ⚠

### Per-Category Statistics

For multi-class networks, get statistics by category:
```python
stats_by_category = network.get_statistics_by_category()

# Access specific category and queue
express_stats = stats_by_category['express'][0]  # Queue 0 for 'express' category
print(f"Express arrivals at Q0: {express_stats['total_arrivals']}")
print(f"Express effective λ at Q0: {express_stats['lambda_eff']:.4f}")
```

---

## Module Descriptions

### `agent.py`
Defines the `Agent` class representing entities moving through the network.
- Tracks arrival time, service times, queue positions
- **NEW**: Tracks category/class membership
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
- **NEW**: Category-specific service time generation

### `queueing_network.py`
Main simulation engine implementing discrete-event simulation.
- Event scheduling using priority queue
- Handles arrivals, departures, and routing
- **NEW**: Category-aware routing and service
- **NEW**: Time-weighted statistics tracking
- Logs comprehensive statistics
- Supports both infinite and finite capacity

### `config_loader.py` (NEW)
Configuration file loader and validator.
- Parses YAML configuration files
- Validates all parameters with helpful error messages
- Provides clean interface to simulation engine

### `visualization.py`
Functions for analyzing and visualizing results.
- Queue length over time plots
- Waiting time distributions
- System time analysis
- **NEW**: Little's Law verification display
- **NEW**: Server utilization comparisons
- Formatted statistics output

### `run_config.py` (NEW)
Command-line script for running config files.
- Loads YAML configuration
- Runs simulation
- Displays results including per-category statistics

---

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
The `get_statistics()` method returns comprehensive metrics per queue:

**Arrival Statistics:**
- `total_arrivals`: Total arrivals to the queue
- `accepted_arrivals`: Arrivals that were accepted
- `rejected_arrivals`: Arrivals that were rejected (finite capacity)
- `lambda_eff`: Effective arrival rate
- `P_loss`: Loss probability

**Time-Averaged Metrics:**
- `L`: Average number in system
- `Lq`: Average number in queue
- `Ls`: Average number in service
- `rho`: Server utilization

**Customer-Averaged Metrics:**
- `num_served`: Total agents served
- `W`: Average time in system
- `Wq`: Average waiting time
- `Ws`: Average service time
- `max_queue_length_observed`: Maximum queue length

**Little's Law Verification:**
- `littles_law_L`: Expected L from λ×W
- `littles_law_L_ratio`: L_simulated / L_expected
- `littles_law_Lq`: Expected Lq from λ×Wq
- `littles_law_Lq_ratio`: Lq_simulated / Lq_expected

---

## Theoretical Background

### Jackson Networks
When capacity is infinite, this simulator implements classical Jackson networks:
- External arrivals follow Poisson process
- Service times are exponentially distributed
- Routing is Markovian (memoryless)
- Each queue operates as M/M/c queue

**Key Property**: Product-form solution exists for steady-state probabilities.

### Multi-Class Networks
With multiple customer classes:
- Each class has independent routing probabilities
- Each class has category-specific service rates
- Classes are assigned at arrival and remain fixed
- Overall system still follows Markovian properties
- Enables modeling of realistic heterogeneous systems

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
| **Series** | `series` | Series of M/M/c queues | ✅ Yes - Fixed |
| **Jackson Network** | `Jacksonnetwork` | Open network, infinite capacity | ✅ Yes - Fixed |
| **Finite Jackson** | `Jacksonnetworkfinitecapacity` | Open network, finite capacity | ⚠️ Approximate only |

### Key Metrics for Comparison

- **L**: Average number of agents in system
- **Lq**: Average number of agents waiting in queue
- **Ls**: Average number of agents in service
- **W**: Average time in system
- **Wq**: Average waiting time in queue
- **Ws**: Average service time
- **ρ**: Server utilization

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
- **< 10% difference**: Excellent match ✓
- **10-20% difference**: Acceptable (increase simulation time)
- **> 20% difference**: Investigate potential bug

---

## Example Output

### Multi-Class Simulation Output
```
================================================================================
CONFIGURATION SUMMARY
================================================================================

Network:
  Number of queues: 3
  Simulation time: 1000.0

Queues:
  Queue 0: 2 server(s), capacity=inf
  Queue 1: 3 server(s), capacity=inf
  Queue 2: 2 server(s), capacity=inf

Categories:
  express: 30.0% of arrivals
  standard: 50.0% of arrivals
  bulk: 20.0% of arrivals

Arrivals:
  External arrival rate: 3.0
  Arrival queue: 0
================================================================================

Starting simulation: max_time=1000.0
Network configuration: 3 queues, 3 categories
------------------------------------------------------------
...
------------------------------------------------------------
Simulation complete: 2847 departures recorded
Rejected agents: 0

================================================================================
SIMULATION STATISTICS
================================================================================

================================================================================
Queue 0 Statistics
================================================================================

                              Arrival Statistics:                               
--------------------------------------------------------------------------------
  Total arrivals:                               3012
  Accepted arrivals:                            3012
  Rejected arrivals:                               0
  Effective arrival rate (λ_eff):             3.0120
  Loss probability (P_loss):                  0.0000

                             Time-Averaged Metrics:                             
--------------------------------------------------------------------------------
  Avg customers in system (L):                1.2456
  Avg customers in queue (Lq):                0.4123
  Avg customers in service (Ls):              0.8333
  Server utilization (ρ):                     0.4167

                           Customer-Averaged Metrics:                           
--------------------------------------------------------------------------------
  Agents served:                                2985
  Avg time in system (W):                     0.4135
  Avg waiting time (Wq):                      0.1369
  Avg service time (Ws):                      0.2766
  Max queue length observed:                      8

                           Little's Law Verification:                            
--------------------------------------------------------------------------------
  L = λ_eff × W:
    Simulated L:                              1.2456
    Expected L (λ_eff × W):                   1.2455
    Ratio (L_sim / L_expected):               1.0001 ✓
    Difference:                                0.01%

  Lq = λ_eff × Wq:
    Simulated Lq:                             0.4123
    Expected Lq (λ_eff × Wq):                 0.4123
    Ratio (Lq_sim / Lq_expected):             1.0000 ✓
    Difference:                                0.00%

================================================================================
PER-CATEGORY STATISTICS
================================================================================

--------------------------------------------------------------------------------
Category: express
--------------------------------------------------------------------------------

  Queue 0:
    Total arrivals:        903
    Accepted arrivals:     903
    Rejected arrivals:       0
    Effective λ:         0.9030

  Queue 2:
    Total arrivals:        903
    Accepted arrivals:     903
    Rejected arrivals:       0
    Effective λ:         0.9030
...
```

---

## Future Extensions

Potential enhancements:
- [ ] Priority scheduling policies (preemptive/non-preemptive)
- [ ] Non-exponential service times (general distributions)
- [ ] Batch arrivals
- [ ] Time-varying arrival rates
- [ ] Closed queueing networks
- [ ] Confidence intervals via multiple replications
- [ ] Warm-up period detection and removal
- [ ] Dynamic category changes (agents changing class)
- [ ] Blocking systems (vs. loss systems)

---

## Troubleshooting

### Common Configuration Errors

**Error: Category probabilities don't sum to 1.0**
```yaml
# ❌ Wrong (sums to 0.8)
categories:
  cat1:
    arrival_probability: 0.5
  cat2:
    arrival_probability: 0.3

# ✓ Correct (sums to 1.0)
categories:
  cat1:
    arrival_probability: 0.5
  cat2:
    arrival_probability: 0.5
```

**Error: Duplicate category names**
```yaml
# ❌ Wrong (YAML only keeps last definition)
categories:
  standard:
    arrival_probability: 0.3
  standard:  # Overwrites previous!
    arrival_probability: 0.7

# ✓ Correct (unique names)
categories:
  express:
    arrival_probability: 0.3
  standard:
    arrival_probability: 0.7
```

**Error: Service rates list wrong length**
```yaml
# For 3 queues:
# ❌ Wrong
service_rates: [1.5, 2.0]  # Only 2 values!

# ✓ Correct
service_rates: [1.5, 2.0, 2.5]  # 3 values for 3 queues
```

---

## License

Open source - feel free to use and modify for research or educational purposes.

## Citation

If you use this simulator in your research, please cite:
```
[Your citation information here]
```

## Contact

For questions, bug reports, or contributions, please contact the repository maintainer or open an issue on GitHub.