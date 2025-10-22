import numpy as np
from queueing_network import QueueingNetwork
from visualization import plot_queue_lengths, plot_waiting_times, print_statistics


def example_mm1_queue():
    """
    Example 1: M/M/1 Queue
    Single server, infinite capacity, FIFO
    Theoretical comparison available
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: M/M/1 Queue")
    print("="*70)
    print("Configuration: Single server, infinite capacity")
    print("Notation: M/M/1 with λ=0.8, μ=1.0, ρ=0.8")
    
    # Network parameters
    arrival_rate = 0.8
    service_rates = [1.0]
    num_servers = [1]
    max_time = 1000.0
    
    # No routing (single queue, agents leave after service)
    prob_matrix = [[0.0]]  # Agent exits after service
    
    capacities = None  # Infinite capacity
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    print("\nTheoretical Values (use theoretical_validation.py):")
    print("  MM1Queue(arrival_rate=0.8, service_rate=1.0)")
    print("  Expected Lq ≈ 3.2, Wq ≈ 4.0")
    
    plot_queue_lengths(agents_data, "M/M/1 Queue - Queue Length Over Time")
    
    return network, agents_data


def example_mmc_queue():
    """
    Example 2: M/M/c Queue
    Multiple servers, infinite capacity, FIFO
    Theoretical comparison available
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: M/M/c Queue")
    print("="*70)
    print("Configuration: 3 servers, infinite capacity")
    print("Notation: M/M/3 with λ=2.0, μ=1.0, ρ=0.667")
    
    # Network parameters
    arrival_rate = 2.0
    service_rates = [1.0]
    num_servers = [3]  # 3 parallel servers
    max_time = 1000.0
    
    prob_matrix = [[0.0]]
    capacities = None
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    print("\nTheoretical Values (use theoretical_validation.py):")
    print("  MMcQueue(arrival_rate=2.0, service_rate=1.0, c=3)")
    
    plot_queue_lengths(agents_data, "M/M/3 Queue - Queue Length Over Time")
    
    return network, agents_data


def example_mm1k_queue():
    """
    Example 3: M/M/1/k Queue
    Single server, finite capacity k, FIFO with rejection
    Theoretical comparison available
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: M/M/1/k Queue")
    print("="*70)
    print("Configuration: Single server, capacity=10")
    print("Notation: M/M/1/10 with λ=0.9, μ=1.0, k=10")
    
    # Network parameters
    arrival_rate = 0.9
    service_rates = [1.0]
    num_servers = [1]
    max_time = 1000.0
    
    prob_matrix = [[0.0]]
    capacities = [10]  # Max 10 agents can wait
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    print(f"\nTotal Rejections: {len(network.rejected_agents)}")
    print("\nTheoretical Values (use theoretical_validation.py):")
    print("  MM1kQueue(arrival_rate=0.9, service_rate=1.0, k=10)")
    
    plot_queue_lengths(agents_data, "M/M/1/10 Queue - Queue Length Over Time")
    
    return network, agents_data


def example_mmck_queue():
    """
    Example 4: M/M/c/k Queue
    Multiple servers, finite capacity k, FIFO with rejection
    Theoretical comparison available
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: M/M/c/k Queue")
    print("="*70)
    print("Configuration: 2 servers, capacity=15")
    print("Notation: M/M/2/15 with λ=1.5, μ=1.0, c=2, k=15")
    
    # Network parameters
    arrival_rate = 1.5
    service_rates = [1.0]
    num_servers = [2]  # 2 parallel servers
    max_time = 1000.0
    
    prob_matrix = [[0.0]]
    capacities = [15]  # Max 15 agents can wait
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    print(f"\nTotal Rejections: {len(network.rejected_agents)}")
    print("\nTheoretical Values (use theoretical_validation.py):")
    print("  MMckQueue(arrival_rate=1.5, service_rate=1.0, c=2, k=15)")
    
    plot_queue_lengths(agents_data, "M/M/2/15 Queue - Queue Length Over Time")
    
    return network, agents_data


def example_jackson_series():
    """
    Example 5: Jackson Network - Series Configuration
    Three M/M/1 queues in series (tandem)
    Theoretical comparison available
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Jackson Network - Series (Tandem) Queues")
    print("="*70)
    print("Configuration: 3 queues in series, all M/M/1")
    print("Notation: λ_ext=1.0, μ=[1.5, 2.0, 2.5], routing: Q0→Q1→Q2→Exit")
    
    # Network parameters
    arrival_rate = 1.0
    service_rates = [1.5, 2.0, 2.5]
    num_servers = [1, 1, 1]
    max_time = 1000.0
    
    # Series routing: Queue 0 → Queue 1 → Queue 2 → Exit
    prob_matrix = [
        [0.0, 1.0, 0.0],  # Q0 → Q1 (100%)
        [0.0, 0.0, 1.0],  # Q1 → Q2 (100%)
        [0.0, 0.0, 0.0]   # Q2 → Exit
    ]
    
    capacities = None  # Infinite capacity (true Jackson network)
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    print("\nTheoretical Values (use theoretical_validation.py):")
    print("  Jacksonnetwork(arrival_rate=1.0, service_rate=[1.5,2.0,2.5],")
    print("                 num_servers=[1,1,1], prob_matrix=...)")
    print("  Effective arrival rates: [1.0, 1.0, 1.0]")
    
    plot_queue_lengths(agents_data, "Jackson Series Network - Queue Lengths")
    plot_waiting_times(agents_data, "Jackson Series Network - Waiting Times")
    
    return network, agents_data


def example_jackson_branching():
    """
    Example 6: Jackson Network - Branching Configuration
    Network with probabilistic routing (not simple series)
    Theoretical comparison available
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Jackson Network - Branching/Merging")
    print("="*70)
    print("Configuration: 4 queues with branching")
    print("Notation: Q0 branches to Q1(20%) or Q3(80%), then merge at Q3")
    
    # Network parameters
    arrival_rate = 1.0
    service_rates = [1.5, 1.5, 2.0, 2.0]
    num_servers = [1, 1, 1, 1]
    max_time = 1000.0
    
    # Branching routing:
    # Q0 → Q1 (20%) or Q3 (80%)
    # Q1 → Q2 (100%)
    # Q2 → Q3 (100%)
    # Q3 → Exit
    prob_matrix = [
        [0.0, 0.2, 0.0, 0.8],  # Q0 branches
        [0.0, 0.0, 1.0, 0.0],  # Q1 → Q2
        [0.0, 0.0, 0.0, 1.0],  # Q2 → Q3
        [0.0, 0.0, 0.0, 0.0]   # Q3 → Exit
    ]
    
    capacities = None
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    print("\nTheoretical Values (use theoretical_validation.py):")
    print("  Jacksonnetwork(arrival_rate=1.0, service_rate=[1.5,1.5,2.0,2.0],")
    print("                 num_servers=[1,1,1,1], prob_matrix=...)")
    print("  Effective arrival rates: [1.0, 0.2, 0.2, 1.0]")
    
    plot_queue_lengths(agents_data, "Jackson Branching Network - Queue Lengths")
    
    return network, agents_data


def example_series_multiserver():
    """
    Example 7: Series Network with Multi-Server Queues
    M/M/c queues in series
    Theoretical comparison available
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Series of M/M/c Queues")
    print("="*70)
    print("Configuration: 3 queues in series with multiple servers")
    print("Notation: Servers=[2,3,2], μ=[1.5,1.5,2.0], λ=3.0")
    
    # Network parameters
    arrival_rate = 3.0
    service_rates = [1.5, 1.5, 2.0]
    num_servers = [2, 3, 2]  # Different number of servers per queue
    max_time = 1000.0
    
    # Series routing
    prob_matrix = [
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0]
    ]
    
    capacities = None
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    print("\nTheoretical Values (use theoretical_validation.py):")
    print("  series(arrival_rate=3.0, service_rate=[1.5,1.5,2.0],")
    print("         num_servers=[2,3,2])")
    
    plot_queue_lengths(agents_data, "Multi-Server Series - Queue Lengths")
    
    return network, agents_data


def example_finite_capacity_network():
    """
    Example 8: Jackson-type Network with Finite Capacity
    Series queues with limited buffers and rejection
    NOTE: Theoretical validation is approximate only
    """
    print("\n" + "="*70)
    print("EXAMPLE 8: Finite Capacity Network (with Rejection)")
    print("="*70)
    print("Configuration: 3 queues in series with capacity limits")
    print("Notation: Capacities=[5,10,15], rejection when full")
    print("WARNING: Theoretical values are approximate!")
    
    # Network parameters
    arrival_rate = 1.0
    service_rates = [1.5, 1.5, 2.0]
    num_servers = [1, 1, 1]
    max_time = 1000.0
    
    # Series routing
    prob_matrix = [
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0]
    ]
    
    capacities = [5, 10, 15]  # Limited capacity per queue
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    print(f"\nTotal Rejections: {len(network.rejected_agents)}")
    if network.rejected_agents:
        rejection_by_queue = {}
        for rej in network.rejected_agents:
            qid = rej['queue_id']
            rejection_by_queue[qid] = rejection_by_queue.get(qid, 0) + 1
        print("Rejections by queue:")
        for qid, count in rejection_by_queue.items():
            print(f"  Queue {qid}: {count} rejections")
    
    print("\nTheoretical Values (use with caution):")
    print("  Jacksonnetworkfinitecapacity(...)")
    print("  Note: Theory does NOT account for rejection effects properly")
    
    plot_queue_lengths(agents_data, "Finite Capacity Network - Queue Lengths")
    
    return network, agents_data


def example_jackson_network():
    """
    Example 1: Classical Jackson Network (infinite capacity)
    Three queues in series with probabilistic routing.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Jackson Network (Infinite Capacity)")
    print("="*70)
    
    # Network parameters
    arrival_rate = 1.0
    service_rates = [1.5, 1.5, 2.0]
    num_servers = [1, 1, 1]
    max_time = 100.0
    
    # Routing: Queue 0 -> Queue 1 (100%), Queue 1 -> Queue 2 (100%), Queue 2 -> Exit
    prob_matrix = [
        [0.0, 1.0, 0.0],  # From Queue 0
        [0.0, 0.0, 1.0],  # From Queue 1
        [0.0, 0.0, 0.0]   # From Queue 2 (exit)
    ]
    
    # No capacity limits (infinite)
    capacities = None
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    plot_queue_lengths(agents_data, "Jackson Network - Queue Lengths")
    
    return network, agents_data


def example_finite_capacity_network():
    """
    Example 2: Network with Finite Capacity (rejection/loss)
    Three queues with limited waiting room.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Network with Finite Capacity (Rejection)")
    print("="*70)
    
    # Network parameters
    arrival_rate = 1.0
    service_rates = [1.5, 1.5, 2.0]
    num_servers = [1, 1, 1]
    max_time = 100.0
    
    # Routing: Series configuration
    prob_matrix = [
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0]
    ]
    
    # Set capacity limits
    capacities = [5, 10, 15]  # Max waiting agents per queue
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    print(f"\nTotal Rejections: {len(network.rejected_agents)}")
    
    plot_queue_lengths(agents_data, "Finite Capacity Network - Queue Lengths")
    
    return network, agents_data


def example_complex_routing():
    """
    Example 3: Complex routing with feedback
    Agents can loop back or skip queues based on probabilities.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Complex Routing with Feedback")
    print("="*70)
    
    # Network parameters
    arrival_rate = 1.0
    service_rates = [1.5, 1.5, 2.0, 2.0]
    num_servers = [1, 1, 1, 1]
    max_time = 100.0
    
    # Complex routing:
    # Queue 0 -> Queue 1 (20%) or Queue 3 (80%)
    # Queue 1 -> Queue 2 (100%)
    # Queue 2 -> Queue 3 (100%)
    # Queue 3 -> Exit
    prob_matrix = [
        [0.0, 0.2, 0.0, 0.8],  # From Queue 0
        [0.0, 0.0, 1.0, 0.0],  # From Queue 1
        [0.0, 0.0, 0.0, 1.0],  # From Queue 2
        [0.0, 0.0, 0.0, 0.0]   # From Queue 3 (exit)
    ]
    
    capacities = None  # Infinite capacity
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    plot_queue_lengths(agents_data, "Complex Routing - Queue Lengths")
    plot_waiting_times(agents_data, "Complex Routing - Waiting Times")
    
    return network, agents_data


def example_multiserver_network():
    """
    Example 4: Network with multiple servers per queue
    Demonstrates M/M/c queues in a network.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Multi-Server Network")
    print("="*70)
    
    # Network parameters
    arrival_rate = 3.0  # Higher arrival rate
    service_rates = [2.0, 2.0, 2.0]
    num_servers = [2, 3, 2]  # Multiple servers per queue
    max_time = 100.0
    
    # Simple series routing
    prob_matrix = [
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0]
    ]
    
    capacities = None
    
    # Run simulation
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
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    plot_queue_lengths(agents_data, "Multi-Server Network - Queue Lengths")
    
    return network, agents_data


if __name__ == "__main__":
    """
    Run all examples demonstrating M/M/* network configurations.
    Comment out examples you don't want to run.
    """
    
    print("\n" + "="*70)
    print("QUEUEING NETWORK SIMULATOR - VALIDATION EXAMPLES")
    print("Each example maps to standard M/M/* queueing notation")
    print("Compare simulation results with theoretical_validation.py")
    print("="*70)
    
    # Single Queue Examples (Direct M/M/* mapping)
    # Please comment out if you wish to run simple models
    # network1, data1 = example_mm1_queue()           # M/M/1
    # network2, data2 = example_mmc_queue()           # M/M/c
    # network3, data3 = example_mm1k_queue()          # M/M/1/k
    # network4, data4 = example_mmck_queue()          # M/M/c/k
    
    # Network Examples (Jackson networks)
    network5, data5 = example_jackson_series()      # Series Jackson
    network6, data6 = example_jackson_branching()   # Branching Jackson
    network7, data7 = example_series_multiserver()  # M/M/c series
    
    # Finite Capacity Network (approximate theory)
    network8, data8 = example_finite_capacity_network()
    
    print("\n" + "="*70)
    print("All validation examples completed!")
    print("Use theoretical_validation.py to compute theoretical values")
    print("="*70)
    
    """
    Run complex examples.
    """
    
    # Example 1: Classical Jackson Network
    network1, data1 = example_jackson_network()
    
    # Example 2: Finite Capacity with Rejection
    network2, data2 = example_finite_capacity_network()
    
    # Example 3: Complex Routing
    network3, data3 = example_complex_routing()
    
    # Example 4: Multi-Server Network
    network4, data4 = example_multiserver_network()
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)
