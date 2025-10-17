import numpy as np
from queueing_network import QueueingNetwork
from visualization import plot_queue_lengths, plot_waiting_times, print_statistics


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
    Run all examples.
    Comment out examples you don't want to run.
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
