# Configuration Examples

This directory contains example YAML configurations for various queueing network scenarios.

## Quick Start
```bash
# Run any example
python run_config.py configs/basic/mm1_queue.yaml

# Run with custom random seed
python run_config.py configs/basic/mm1_queue.yaml --seed 123

# Run all basic examples
python examples/run_all_basic.py
```

## Directory Structure

### basic/ - Single Queue Examples

Standard M/M/* queues for learning and validation. These examples have exact theoretical solutions for comparison.

| File | Description | Theory Class | Key Metrics |
|------|-------------|--------------|-------------|
| `mm1_queue.yaml` | M/M/1: Single server, infinite capacity | `MM1Queue` | ρ=0.8, Lq≈3.2 |
| `mmc_queue.yaml` | M/M/c: 3 servers, infinite capacity | `MMcQueue` | ρ=0.667 |
| `mm1k_queue.yaml` | M/M/1/k: Single server, capacity=10 | `MM1kQueue` | Has rejections |
| `mmck_queue.yaml` | M/M/c/k: 2 servers, capacity=15 | `MMckQueue` | Has rejections |

**Use these for**: Learning basics, validating simulator, teaching queueing theory

---

### networks/ - Multi-Queue Networks

Jackson networks and complex routing patterns. Series networks have exact theory; others are approximate.

| File | Description | Queues | Features |
|------|-------------|--------|----------|
| `jackson_series.yaml` | Three queues in tandem | 3 | Series routing, theory available |
| `jackson_branching.yaml` | Branching and merging paths | 4 | Probabilistic splits |
| `series_multiserver.yaml` | Series with M/M/c queues | 3 | Variable server counts |
| `finite_capacity.yaml` | Limited buffers with rejection | 3 | Loss system, rejections |

**Use these for**: Network analysis, routing studies, capacity planning

---

### multiclass/ - Multi-Class Systems

Different customer categories with distinct routing and service rates. These demonstrate the power of multi-class modeling.

| File | Description | Categories | Real-World Analogy |
|------|-------------|------------|-------------------|
| `factory_three_class.yaml` | Express/Standard/Bulk parts | 3 | Manufacturing plant |
| `priority_fasttrack.yaml` | VIP fast-track system | 2 | Airport security |
| `manufacturing_rework.yaml` | Quality control with loops | 2 | Assembly line |
| `hospital_triage.yaml` | Emergency/Urgent/Routine | 3 | Emergency department |

**Use these for**: Multi-class analysis, priority systems, real-world modeling

---

### advanced/ - Complex Scenarios

Research-oriented configurations for advanced users.

| File | Description | Challenge |
|------|-------------|-----------|
| `feedback_loops.yaml` | Customers can loop back | Cyclic routing |
| `heavy_traffic.yaml` | High utilization (ρ>0.9) | Stability analysis |
| `mixed_capacity.yaml` | Some finite, some infinite | Mixed constraints |

**Use these for**: Research, edge cases, stress testing

---

## Validation Against Theory

Configs in `basic/` and `networks/` can be validated using `theoretical_validation.py`:
```python
from theoretical_validation import MM1Queue

# Run simulation
python run_config.py configs/basic/mm1_queue.yaml

# Compare with theory
theory = MM1Queue(arrival_rate=0.8, service_rate=1.0)
theory.calculate_measures()
theory.print_results()
```

Expected agreement: Within 5-15% for metrics like L, Lq, W, Wq.

---

## Creating Your Own Config

### Template Structure
```yaml
network:
  num_queues: <number>
  max_time: <simulation_time>

queues:
  - queue_id: <0 to num_queues-1>
    num_servers: <positive_integer>
    capacity: <positive_integer or 'inf'>

categories:
  <category_name>:
    arrival_probability: <0 to 1, must sum to 1.0 across categories>
    service_rates: [<rate_q0>, <rate_q1>, ...]  # Length = num_queues
    routing_matrix:
      - [<prob_q0_to_q0>, <prob_q0_to_q1>, ...]  # Row sums ≤ 1.0
      - [<prob_q1_to_q0>, <prob_q1_to_q1>, ...]
      # ... num_queues rows

arrivals:
  external_arrival_rate: <positive_number>
  arrival_queue: <queue_id where arrivals enter>
```

### Key Rules

1. **Category probabilities** must sum to exactly 1.0
2. **Routing matrix** rows can sum to < 1.0 (remainder = exit probability)
3. **Service rates** list must have exactly `num_queues` elements
4. **Queue IDs** must be consecutive: 0, 1, 2, ..., num_queues-1
5. **Stability**: For infinite capacity, ensure ρ < 1 (arrival_rate < service_rate × num_servers)

### Common Patterns

**Single-class network** (backwards compatible):
```yaml
categories:
  default:
    arrival_probability: 1.0
    # ... rest of config
```

**Fast-track system** (skip queues):
```yaml
categories:
  vip:
    routing_matrix:
      - [0.0, 0.0, 1.0]  # Skip queue 1, go directly to queue 2
```

**Rework loops** (quality control):
```yaml
categories:
  with_rework:
    routing_matrix:
      - [0.0, 1.0, 0.0]
      - [0.2, 0.0, 0.8]  # 20% return to queue 0, 80% continue
```

---

## Troubleshooting

### Error: "Category arrival probabilities sum to X, must sum to 1.0"

Check that all `arrival_probability` values add up to 1.0:
```yaml
categories:
  cat1:
    arrival_probability: 0.3
  cat2:
    arrival_probability: 0.7  # 0.3 + 0.7 = 1.0 ✓
```

### Error: "routing_matrix row X sums to Y > 1.0"

Each row in routing_matrix must sum to ≤ 1.0:
```yaml
routing_matrix:
  - [0.0, 0.6, 0.3]  # Sum = 0.9, exit prob = 0.1 ✓
  - [0.0, 0.0, 1.2]  # Sum = 1.2 > 1.0 ✗
```

### Error: "service_rates must have N values"

Service rates list must match number of queues:
```yaml
network:
  num_queues: 3

categories:
  default:
    service_rates: [1.5, 2.0, 2.5]  # 3 values ✓
```

---

## Tips for Effective Simulation

1. **Start simple**: Begin with configs in `basic/` before attempting `multiclass/`
2. **Run long enough**: Use `max_time ≥ 1000` for stable statistics
3. **Check stability**: Ensure ρ < 1 for infinite capacity queues
4. **Validate**: Compare with theory when possible (use `theoretical_validation.py`)
5. **Use version control**: Keep config files in Git for reproducibility
6. **Document changes**: Add comments in YAML to explain your scenario

---

## Further Reading

- Main README.md - Full simulator documentation
- theoretical_validation.py - Analytical solutions
- Paper: "Analysis of Multi-Class Queueing Networks" [add your citation]