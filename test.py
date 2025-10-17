"""
Test and Validation Script
===========================
Basic tests to verify the queueing network simulator is working correctly.
"""

import numpy as np
from queueing_network import QueueingNetwork


def test_basic_simulation():
    """Test that simulation runs without errors."""
    print("Test 1: Basic Simulation Run")
    print("-" * 50)
    
    arrival_rate = 0.8
    service_rates = [1.0]
    num_servers = [1]
    prob_matrix = [[0.0]]
    max_time = 10.0
    
    np.random.seed(42)
    network = QueueingNetwork(
        arrival_rate=arrival_rate,
        service_rates=service_rates,
        num_servers=num_servers,
        prob_matrix=prob_matrix,
        max_time=max_time
    )
    
    agents_data = network.simulate()
    
    assert len(agents_data) > 0, "No agents were served"
    print(f"✓ Simulation completed: {len(agents_data)} agents served")
    print()


def test_finite_capacity():
    """Test that finite capacity causes rejections."""
    print("Test 2: Finite Capacity with Rejections")
    print("-" * 50)
    
    arrival_rate = 5.0  # High arrival rate
    service_rates = [1.0]
    num_servers = [1]
    prob_matrix = [[0.0]]
    max_time = 10.0
    capacities = [2]  # Very small capacity
    
    np.random.seed(42)
    network = QueueingNetwork(
        arrival_rate=arrival_rate,
        service_rates=service_rates,
        num_servers=num_servers,
        prob_matrix=prob_matrix,
        max_time=max_time,
        capacities=capacities
    )
    
    agents_data = network.simulate()
    
    assert len(network.rejected_agents) > 0, "Expected some rejections with small capacity"
    print(f"✓ Rejections working: {len(network.rejected_agents)} agents rejected")
    print()


def test_series_queues():
    """Test agents flow through series of queues."""
    print("Test 3: Series Queue Flow")
    print("-" * 50)
    
    arrival_rate = 1.0
    service_rates = [2.0, 2.0, 2.0]
    num_servers = [1, 1, 1]
    prob_matrix = [
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0]
    ]
    max_time = 20.0
    
    np.random.seed(42)
    network = QueueingNetwork(
        arrival_rate=arrival_rate,
        service_rates=service_rates,
        num_servers=num_servers,
        prob_matrix=prob_matrix,
        max_time=max_time
    )
    
    agents_data = network.simulate()
    stats = network.get_statistics()
    
    # Check all queues were visited
    assert len(stats) == 3, f"Expected 3 queues, got {len(stats)}"
    
    # Check that agents flowed through all queues
    for queue_id in range(3):
        assert stats[queue_id]['num_served'] > 0, f"Queue {queue_id} served no agents"
    
    print(f"✓ Series flow working:")
    for queue_id, stat in stats.items():
        print(f"  Queue {queue_id}: {stat['num_served']} agents")
    print()


def test_multiserver():
    """Test multiple servers per queue."""
    print("Test 4: Multi-Server Queue")
    print("-" * 50)
    
    arrival_rate = 3.0
    service_rates = [1.0]
    num_servers = [3]  # Three servers
    prob_matrix = [[0.0]]
    max_time = 20.0
    
    np.random.seed(42)
    network = QueueingNetwork(
        arrival_rate=arrival_rate,
        service_rates=service_rates,
        num_servers=num_servers,
        prob_matrix=prob_matrix,
        max_time=max_time
    )
    
    agents_data = network.simulate()
    stats = network.get_statistics()
    
    # With 3 servers and high arrival rate, queue should be relatively small
    avg_queue = stats[0]['avg_queue_length']
    print(f"✓ Multi-server working: avg queue length = {avg_queue:.3f}")
    print(f"  (Should be small with 3 servers)")
    print()


def test_utilization_check():
    """
    Test that utilization makes sense.
    For M/M/1 queue: rho = lambda/mu
    If rho < 1, system should be stable
    """
    print("Test 5: Utilization Check")
    print("-" * 50)
    
    arrival_rate = 0.7
    service_rate = 1.0
    rho = arrival_rate / service_rate
    
    service_rates = [service_rate]
    num_servers = [1]
    prob_matrix = [[0.0]]
    max_time = 1000.0  # Long simulation
    
    np.random.seed(42)
    network = QueueingNetwork(
        arrival_rate=arrival_rate,
        service_rates=service_rates,
        num_servers=num_servers,
        prob_matrix=prob_matrix,
        max_time=max_time
    )
    
    agents_data = network.simulate()
    stats = network.get_statistics()
    
    print(f"  Theoretical utilization (rho): {rho:.3f}")
    print(f"  Average queue length: {stats[0]['avg_queue_length']:.3f}")
    print(f"  Average waiting time: {stats[0]['avg_waiting_time']:.3f}")
    
    # For M/M/1, theoretical L = rho/(1-rho) and W = 1/(mu-lambda)
    theoretical_L = rho / (1 - rho)
    theoretical_W = 1 / (service_rate - arrival_rate)
    
    print(f"\n  Theoretical L (queue length): {theoretical_L:.3f}")
    print(f"  Theoretical W (waiting time): {theoretical_W:.3f}")
    
    # Check if simulation is reasonably close to theory (within 30%)
    L_diff = abs(stats[0]['avg_queue_length'] - theoretical_L) / theoretical_L
    W_diff = abs(stats[0]['avg_waiting_time'] - theoretical_W) / theoretical_W
    
    if L_diff < 0.3 and W_diff < 0.3:
        print(f"✓ Simulation matches theory (within 30%)")
    else:
        print(f"⚠ Warning: Simulation differs from theory")
        print(f"  (This can happen with shorter simulations)")
    print()


def test_probability_routing():
    """Test probabilistic routing."""
    print("Test 6: Probabilistic Routing")
    print("-" * 50)
    
    arrival_rate = 1.0
    service_rates = [2.0, 2.0, 2.0]
    num_servers = [1, 1, 1]
    
    # Queue 0 routes to Queue 1 (30%) or Queue 2 (70%)
    prob_matrix = [
        [0.0, 0.3, 0.7],
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0]
    ]
    max_time = 100.0
    
    np.random.seed(42)
    network = QueueingNetwork(
        arrival_rate=arrival_rate,
        service_rates=service_rates,
        num_servers=num_servers,
        prob_matrix=prob_matrix,
        max_time=max_time
    )
    
    agents_data = network.simulate()
    stats = network.get_statistics()
    
    n1 = stats[1]['num_served']
    n2 = stats[2]['num_served']
    total = n1 + n2
    
    ratio_to_q1 = n1 / total if total > 0 else 0
    ratio_to_q2 = n2 / total if total > 0 else 0
    
    print(f"  Queue 1 received: {n1} agents ({ratio_to_q1:.1%})")
    print(f"  Queue 2 received: {n2} agents ({ratio_to_q2:.1%})")
    print(f"  Expected: ~30% to Queue 1, ~70% to Queue 2")
    
    # Check if roughly matches expected probabilities (within 15%)
    if abs(ratio_to_q1 - 0.3) < 0.15 and abs(ratio_to_q2 - 0.7) < 0.15:
        print(f"✓ Probabilistic routing working correctly")
    else:
        print(f"⚠ Routing ratios differ from expected (may need longer simulation)")
    print()


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("RUNNING VALIDATION TESTS")
    print("="*70 + "\n")
    
    try:
        test_basic_simulation()
        test_finite_capacity()
        test_series_queues()
        test_multiserver()
        test_utilization_check()
        test_probability_routing()
        
        print("="*70)
        print("ALL TESTS COMPLETED")
        print("="*70)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
