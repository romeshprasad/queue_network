from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import csv
import os


def plot_queue_lengths(agents_data, title="Queue Length Over Time"):
    """
    Plot queue length over time for each queue in the network.
    
    Parameters
    ----------
    agents_data : numpy.ndarray
        Array of agent statistics from simulation
    title : str, optional
        Plot title
    """
    if len(agents_data) == 0:
        print("No data to visualize")
        return
    
    data = np.array(agents_data)
    queue_ids = np.unique(data[:, 5]).astype(int)
    
    plt.figure(figsize=(12, 6))
    
    for queue_id in queue_ids:
        queue_data = data[data[:, 5] == queue_id]
        arrival_times = queue_data[:, 1]
        queue_lengths = queue_data[:, 6]
        
        plt.plot(arrival_times, queue_lengths, 
                drawstyle='steps-post', 
                label=f'Queue {queue_id}',
                linewidth=1.5)
    
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Queue Length', fontsize=12)
    plt.title(title, fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_waiting_times(agents_data, title="Waiting Time Distribution"):
    """
    Plot histogram of waiting times for each queue.
    
    Parameters
    ----------
    agents_data : numpy.ndarray
        Array of agent statistics from simulation
    title : str, optional
        Plot title
    """
    if len(agents_data) == 0:
        print("No data to visualize")
        return
    
    data = np.array(agents_data)
    queue_ids = np.unique(data[:, 5]).astype(int)
    
    n_queues = len(queue_ids)
    fig, axes = plt.subplots(1, n_queues, figsize=(5*n_queues, 4))
    
    if n_queues == 1:
        axes = [axes]
    
    for idx, queue_id in enumerate(queue_ids):
        queue_data = data[data[:, 5] == queue_id]
        waiting_times = queue_data[:, 2] - queue_data[:, 1]
        
        axes[idx].hist(waiting_times, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
        axes[idx].set_xlabel('Waiting Time', fontsize=11)
        axes[idx].set_ylabel('Frequency', fontsize=11)
        axes[idx].set_title(f'Queue {queue_id}', fontsize=12)
        axes[idx].grid(True, alpha=0.3)
        axes[idx].axvline(np.mean(waiting_times), color='red', 
                         linestyle='--', linewidth=2, label=f'Mean: {np.mean(waiting_times):.3f}')
        axes[idx].legend()
    
    fig.suptitle(title, fontsize=14, y=1.02)
    plt.tight_layout()
    plt.show()


def plot_system_times(agents_data, title="System Time by Agent"):
    """
    Plot system time (total time in network) for each agent.
    
    Parameters
    ----------
    agents_data : numpy.ndarray
        Array of agent statistics from simulation
    title : str, optional
        Plot title
    """
    if len(agents_data) == 0:
        print("No data to visualize")
        return
    
    data = np.array(agents_data)
    
    # Calculate system time for each agent
    agent_ids = data[:, 0]
    system_times = data[:, 3] - data[:, 1]
    
    plt.figure(figsize=(12, 6))
    plt.scatter(agent_ids, system_times, alpha=0.6, s=20)
    plt.xlabel('Agent ID', fontsize=12)
    plt.ylabel('System Time', fontsize=12)
    plt.title(title, fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # Add mean line
    mean_time = np.mean(system_times)
    plt.axhline(mean_time, color='red', linestyle='--', 
                linewidth=2, label=f'Mean: {mean_time:.3f}')
    plt.legend()
    plt.tight_layout()
    plt.show()


def print_statistics(stats_dict):
    """
    Print formatted statistics from simulation.
    
    Parameters
    ----------
    stats_dict : dict
        Dictionary of statistics from get_statistics()
    """
    print("\n" + "="*70)
    print("SIMULATION STATISTICS")
    print("="*70)
    
    for queue_id, stats in stats_dict.items():
        print(f"\nQueue {queue_id}:")
        print(f"  Agents Served:        {stats['num_served']}")
        print(f"  Avg Waiting Time:     {stats['avg_waiting_time']:.4f}")
        print(f"  Avg Service Time:     {stats['avg_service_time']:.4f}")
        print(f"  Avg System Time:      {stats['avg_system_time']:.4f}")
        print(f"  Avg Queue Length:     {stats['avg_queue_length']:.4f}")
        print(f"  Max Queue Length:     {stats['max_queue_length']:.0f}")
    
    print("\n" + "="*70)

def statistics_to_csv(network_type, stats_dict, output_file):
    """
    Save simulation statistics to a CSV file.
    
    Parameters
    ----------
    network_type : str
        The type of network this is
    stats_dict : dict
        Dictionary of statistics from get_statistics()
    output_file : str
        Path to the output CSV file
    """
    
    # Define the header and the order of fields
    fieldnames = [
        "timestamp",
        "type",
        "queue_id",
        "num_served",
        "avg_waiting_time",
        "avg_service_time",
        "avg_system_time",
        "avg_queue_length",
        "max_queue_length"
    ]

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Check if the file already exists
    file_exists = os.path.isfile(output_file)

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Open in append mode if exists, write mode otherwise
    with open(output_file, "a" if file_exists else "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header only if file is new
        if not file_exists:
            writer.writeheader()
        
        # Write each queue’s stats
        for queue_id, stats in stats_dict.items():
            row = {
                "timestamp": timestamp,
                "type": network_type,
                "queue_id": queue_id,
                "num_served": stats["num_served"],
                "avg_waiting_time": stats["avg_waiting_time"],
                "avg_service_time": stats["avg_service_time"],
                "avg_system_time": stats["avg_system_time"],
                "avg_queue_length": stats["avg_queue_length"],
                "max_queue_length": stats["max_queue_length"]
            }
            writer.writerow(row)