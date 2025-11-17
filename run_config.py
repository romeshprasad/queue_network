import numpy as np
from queueing_network import QueueingNetwork
from visualization import print_statistics, plot_queue_lengths


def run_from_config(config_path, seed=42):
    """
    Run simulation from YAML config file.
    
    Parameters
    ----------
    config_path : str
        Path to YAML configuration file
    seed : int, optional
        Random seed for reproducibility
    """
    # Set random seed
    np.random.seed(seed)
    
    print("\n" + "="*80)
    print("MULTI-CLASS QUEUEING NETWORK SIMULATION")
    print("="*80)
    
    # Create network from config
    network = QueueingNetwork(config_path)
    
    # Run simulation
    agents_data = network.simulate()
    
    # Get overall statistics
    stats = network.get_statistics()
    
    # Display results
    print_statistics(stats)
    
    # Get per-category statistics
    print("\n" + "="*80)
    print("PER-CATEGORY STATISTICS")
    print("="*80)
    
    stats_by_category = network.get_statistics_by_category()
    
    for category in network.categories:
        print(f"\n{'-'*80}")
        print(f"Category: {category}")
        print(f"{'-'*80}")
        
        for queue_id in range(len(network.queues)):
            cat_stats = stats_by_category[category][queue_id]
            print(f"\n  Queue {queue_id}:")
            print(f"    Total arrivals:     {cat_stats['total_arrivals']:>6}")
            print(f"    Accepted arrivals:  {cat_stats['accepted_arrivals']:>6}")
            print(f"    Rejected arrivals:  {cat_stats['rejected_arrivals']:>6}")
            print(f"    Effective λ:        {cat_stats['lambda_eff']:>6.4f}")
    
    print("\n" + "="*80)
    
    # Optional: Plot queue lengths
    # plot_queue_lengths(agents_data, "Multi-Class Network - Queue Lengths")
    
    return network, agents_data, stats


if __name__ == "__main__":
    # Run with the example config
    network, data, stats = run_from_config('configs/multi_class/factory_three_class.yaml')
    
    print("\n✓ Simulation completed successfully!")