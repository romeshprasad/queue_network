import numpy as np
from queueing_network import QueueingNetwork
from visualization import print_statistics, plot_queue_lengths, visualize_network

class CustomNetwork(QueueingNetwork):
    def __init__(self):
        super(CustomNetwork, self).__init__(arrival_rate=3.0, arrival_queue_id=0)

        # Queues with FILO selection order
        self.add_queue(2, dispatch_policy=(lambda q: q.pop(-1)))
        self.add_queue(3, dispatch_policy=(lambda q: q.pop(-1)))
        self.add_queue(2, dispatch_policy=(lambda q: q.pop(-1)))

        # Same categories as before
        self.add_category("express", 0.3, [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0]], [2.0, 2.5, 3.0])
        self.add_category("standard", 0.5, [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0]], [1.5, 2.0, 2.5])
        self.add_category("bulk", 0.2, [[0.0, 1.0, 0.0], [0.2, 0.0, 0.8], [0.0, 0.0, 0.0]], [1.2, 1.5, 2.0])


def run_from_class(seed=42):
    """
    Run simulation with a network defined from a class

    Parameters
    ----------
    seed : int, optional
        Random seed for reproducibility
    """
    # Set random seed
    np.random.seed(seed)

    print("\n" + "=" * 80)
    print("MULTI-CLASS QUEUEING NETWORK SIMULATION")
    print("=" * 80)

    # Create network from config
    network = CustomNetwork()

    # Run simulation
    agents_data = network.simulate(100.0)

    # Get overall statistics
    stats = network.get_statistics()

    # Display results
    print_statistics(stats)

    # Get per-category statistics
    print("\n" + "=" * 80)
    print("PER-CATEGORY STATISTICS")
    print("=" * 80)

    stats_by_category = network.get_statistics_by_category()

    for category in network.categories:
        print(f"\n{'-' * 80}")
        print(f"Category: {category}")
        print(f"{'-' * 80}")

        for queue_id in range(len(network.queues)):
            cat_stats = stats_by_category[category][queue_id]
            print(f"\n  Queue {queue_id}:")
            print(f"    Total arrivals:     {cat_stats['total_arrivals']:>6}")
            print(f"    Accepted arrivals:  {cat_stats['accepted_arrivals']:>6}")
            print(f"    Rejected arrivals:  {cat_stats['rejected_arrivals']:>6}")
            print(f"    Effective λ:        {cat_stats['lambda_eff']:>6.4f}")

    print("\n" + "=" * 80)

    # Optional: Plot queue lengths
    # plot_queue_lengths(agents_data, "Multi-Class Network - Queue Lengths")

    visualize_network(network, stats, stats_by_category)

    return network, agents_data, stats

def run_from_script(seed=42):
    """
    Run simulation with a network defined in a script

    Parameters
    ----------
    seed : int, optional
        Random seed for reproducibility
    """
    # Set random seed
    np.random.seed(seed)

    print("\n" + "=" * 80)
    print("MULTI-CLASS QUEUEING NETWORK SIMULATION")
    print("=" * 80)

    # Create network from config
    network = QueueingNetwork(arrival_rate=3.0, arrival_queue_id=0)

    # Queues with FILO selection order
    network.add_queue(2, dispatch_policy = (lambda q: q.pop(-1)))
    network.add_queue(3, dispatch_policy = (lambda q: q.pop(-1)))
    network.add_queue(2, dispatch_policy = (lambda q: q.pop(-1)))

    # Same categories as before
    network.add_category("express", 0.3, [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0]], [2.0, 2.5, 3.0])
    network.add_category("standard", 0.5, [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0]], [1.5, 2.0, 2.5])
    network.add_category("bulk", 0.2, [[0.0, 1.0, 0.0], [0.2, 0.0, 0.8], [0.0, 0.0, 0.0]], [1.2, 1.5, 2.0])

    # Run simulation
    agents_data = network.simulate(100.0)

    # Get overall statistics
    stats = network.get_statistics()

    # Display results
    print_statistics(stats)

    # Get per-category statistics
    print("\n" + "=" * 80)
    print("PER-CATEGORY STATISTICS")
    print("=" * 80)

    stats_by_category = network.get_statistics_by_category()

    for category in network.categories:
        print(f"\n{'-' * 80}")
        print(f"Category: {category}")
        print(f"{'-' * 80}")

        for queue_id in range(len(network.queues)):
            cat_stats = stats_by_category[category][queue_id]
            print(f"\n  Queue {queue_id}:")
            print(f"    Total arrivals:     {cat_stats['total_arrivals']:>6}")
            print(f"    Accepted arrivals:  {cat_stats['accepted_arrivals']:>6}")
            print(f"    Rejected arrivals:  {cat_stats['rejected_arrivals']:>6}")
            print(f"    Effective λ:        {cat_stats['lambda_eff']:>6.4f}")

    print("\n" + "=" * 80)

    # Optional: Plot queue lengths
    # plot_queue_lengths(agents_data, "Multi-Class Network - Queue Lengths")

    visualize_network(network, stats, stats_by_category)

    return network, agents_data, stats


if __name__ == "__main__":
    # Run with the example config
    # network, data, stats = run_from_config('configs/networks/jackson_branching.yaml')
    network, data, stats = run_from_class()

    print("\n✓ Simulation completed successfully!")