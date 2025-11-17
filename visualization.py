import numpy as np
import matplotlib.pyplot as plt


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
    plt.ylabel('Queue Length (at arrival)', fontsize=12)
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
    Print comprehensive formatted statistics from simulation.
    
    Parameters
    ----------
    stats_dict : dict
        Dictionary of statistics from get_statistics()
    """
    print("\n" + "="*80)
    print("SIMULATION STATISTICS")
    print("="*80)
    
    for queue_id, stats in stats_dict.items():
        print(f"\n{'='*80}")
        print(f"Queue {queue_id} Statistics")
        print(f"{'='*80}")
        
        # ============================================================
        # ARRIVAL STATISTICS
        # ============================================================
        print(f"\n{'Arrival Statistics:':^80}")
        print(f"{'-'*80}")
        print(f"  {'Total arrivals:':<40} {stats['total_arrivals']:>10}")
        print(f"  {'Accepted arrivals:':<40} {stats['accepted_arrivals']:>10}")
        print(f"  {'Rejected arrivals:':<40} {stats['rejected_arrivals']:>10}")
        print(f"  {'Effective arrival rate (λ_eff):':<40} {stats['lambda_eff']:>10.4f}")
        print(f"  {'Loss probability (P_loss):':<40} {stats['P_loss']:>10.4f}")
        
        # ============================================================
        # TIME-AVERAGED METRICS
        # ============================================================
        print(f"\n{'Time-Averaged Metrics:':^80}")
        print(f"{'-'*80}")
        print(f"  {'Avg customers in system (L):':<40} {stats['L']:>10.4f}")
        print(f"  {'Avg customers in queue (Lq):':<40} {stats['Lq']:>10.4f}")
        print(f"  {'Avg customers in service (Ls):':<40} {stats['Ls']:>10.4f}")
        print(f"  {'Server utilization (rho):':<40} {stats['rho']:>10.4f}")
        
        # ============================================================
        # CUSTOMER-AVERAGED METRICS
        # ============================================================
        print(f"\n{'Customer-Averaged Metrics:':^80}")
        print(f"{'-'*80}")
        print(f"  {'Agents served:':<40} {stats['num_served']:>10}")
        print(f"  {'Avg time in system (W):':<40} {stats['W']:>10.4f}")
        print(f"  {'Avg waiting time (Wq):':<40} {stats['Wq']:>10.4f}")
        print(f"  {'Avg service time (Ws):':<40} {stats['Ws']:>10.4f}")
        print(f"  {'Max queue length observed:':<40} {stats['max_queue_length_observed']:>10.0f}")
        
        # ============================================================
        # LITTLE'S LAW VERIFICATION
        # ============================================================
        print(f"\n{'Littles Law Verification:':^80}")
        print(f"{'-'*80}")
        
        # L = λ * W
        if stats['lambda_eff'] > 0 and stats['W'] > 0:
            l_actual = stats['L']
            l_expected = stats['littles_law_L']
            l_ratio = stats['littles_law_L_ratio']
            l_diff_pct = abs(1 - l_ratio) * 100
            
            l_status = "✓" if 0.90 <= l_ratio <= 1.10 else "⚠"
            
            print(f"  L = λ_eff * W:")
            print(f"    {'Simulated L:':<38} {l_actual:>10.4f}")
            print(f"    {'Expected L (λ_eff * W):':<38} {l_expected:>10.4f}")
            print(f"    {'Ratio (L_sim / L_expected):':<38} {l_ratio:>10.4f} {l_status}")
            print(f"    {'Difference:':<38} {l_diff_pct:>9.2f}%")
        else:
            print(f"  L = λ_eff * W: N/A (insufficient data)")
        
        print()
        
        # Lq = λ * Wq
        if stats['lambda_eff'] > 0 and stats['Wq'] > 0:
            lq_actual = stats['Lq']
            lq_expected = stats['littles_law_Lq']
            lq_ratio = stats['littles_law_Lq_ratio']
            lq_diff_pct = abs(1 - lq_ratio) * 100
            
            lq_status = "✓" if 0.90 <= lq_ratio <= 1.10 else "⚠"
            
            print(f"  Lq = λ_eff × Wq:")
            print(f"    {'Simulated Lq:':<38} {lq_actual:>10.4f}")
            print(f"    {'Expected Lq (λ_eff × Wq):':<38} {lq_expected:>10.4f}")
            print(f"    {'Ratio (Lq_sim / Lq_expected):':<38} {lq_ratio:>10.4f} {lq_status}")
            print(f"    {'Difference:':<38} {lq_diff_pct:>9.2f}%")
        else:
            print(f"  Lq = λ_eff × Wq: N/A (insufficient data)")
    
    print("\n" + "="*80)
    print("Legend: ✓ = Within 10% (Good)  |  ⚠ = Outside 10% (Check)")
    print("="*80 + "\n")


def print_littles_law_verification(stats_dict):
    """
    Print detailed Little's Law verification for all queues.
    
    Parameters
    ----------
    stats_dict : dict
        Dictionary of statistics from get_statistics()
    """
    print("\n" + "="*80)
    print("LITTLE'S LAW VERIFICATION SUMMARY")
    print("="*80)
    
    print(f"\n{'Queue':<8} {'Metric':<6} {'Simulated':<12} {'Expected':<12} {'Ratio':<10} {'Status':<8}")
    print("-"*80)
    
    for queue_id, stats in stats_dict.items():
        # L = λ * W
        if stats['lambda_eff'] > 0 and stats['W'] > 0:
            l_ratio = stats['littles_law_L_ratio']
            l_status = "✓ Good" if 0.90 <= l_ratio <= 1.10 else "⚠ Check"
            
            print(f"{queue_id:<8} {'L':<6} {stats['L']:<12.4f} "
                  f"{stats['littles_law_L']:<12.4f} {l_ratio:<10.4f} {l_status:<8}")
        
        # Lq = λ * Wq
        if stats['lambda_eff'] > 0 and stats['Wq'] > 0:
            lq_ratio = stats['littles_law_Lq_ratio']
            lq_status = "✓ Good" if 0.90 <= lq_ratio <= 1.10 else "⚠ Check"
            
            print(f"{queue_id:<8} {'Lq':<6} {stats['Lq']:<12.4f} "
                  f"{stats['littles_law_Lq']:<12.4f} {lq_ratio:<10.4f} {lq_status:<8}")
    
    print("\n" + "="*80)
    print("Ratio = Simulated / Expected (should be close to 1.0)")
    print("✓ Good = Within 10%  |  ⚠ Check = Outside 10%")
    print("="*80 + "\n")


def print_comparison_table(stats_dict, theoretical_stats=None):
    """
    Print comparison table between simulation and theoretical results.
    
    Parameters
    ----------
    stats_dict : dict
        Dictionary of simulation statistics
    theoretical_stats : dict, optional
        Dictionary of theoretical statistics for comparison
    """
    print("\n" + "="*80)
    print("SIMULATION vs THEORETICAL COMPARISON")
    print("="*80)
    
    if theoretical_stats is None:
        print("\nNo theoretical results provided for comparison.")
        print("Use theoretical_validation.py to compute expected values.")
        return
    
    print(f"\n{'Queue':<8} {'Metric':<6} {'Simulated':<12} {'Theoretical':<12} "
          f"{'Difference':<12} {'Status':<8}")
    print("-"*80)
    
    metrics = ['L', 'Lq', 'Ls', 'W', 'Wq', 'rho']
    
    for queue_id in stats_dict.keys():
        if queue_id not in theoretical_stats:
            continue
        
        sim = stats_dict[queue_id]
        theory = theoretical_stats[queue_id]
        
        for metric in metrics:
            if metric in sim and metric in theory:
                sim_val = sim[metric]
                theory_val = theory[metric]
                
                if theory_val > 0:
                    diff_pct = abs(sim_val - theory_val) / theory_val * 100
                    status = "✓ Good" if diff_pct < 10 else "⚠ Check" if diff_pct < 20 else "✗ Large"
                else:
                    diff_pct = 0.0
                    status = "N/A"
                
                print(f"{queue_id:<8} {metric:<6} {sim_val:<12.4f} {theory_val:<12.4f} "
                      f"{diff_pct:<11.2f}% {status:<8}")
    
    print("\n" + "="*80)
    print("✓ Good = < 10% difference  |  ⚠ Check = 10-20%  |  ✗ Large = > 20%")
    print("="*80 + "\n")


def plot_time_weighted_metrics(network, title="Time-Weighted Queue Metrics"):
    """
    Plot time-weighted queue length evolution over time.
    
    Parameters
    ----------
    network : QueueingNetwork
        The network object after simulation (must have state_changes data)
    title : str, optional
        Plot title
    """
    if not hasattr(network, 'state_changes') or not network.state_changes:
        print("No time-weighted data available. Run simulation first.")
        return
    
    n_queues = len(network.queues)
    
    fig, axes = plt.subplots(n_queues, 1, figsize=(12, 4*n_queues), squeeze=False)
    
    for queue_id in range(n_queues):
        state_data = network.state_changes[queue_id]
        
        if not state_data:
            continue
        
        # Extract time series
        times = [s[0] for s in state_data]
        queue_lengths = [s[1] for s in state_data]  # Lq
        system_lengths = [s[2] for s in state_data]  # L
        num_busy = [s[3] for s in state_data]  # Ls
        
        ax = axes[queue_id, 0]
        
        # Plot step functions
        ax.step(times, queue_lengths, where='post', label='Lq (in queue)', 
                linewidth=1.5, alpha=0.8)
        ax.step(times, system_lengths, where='post', label='L (in system)', 
                linewidth=1.5, alpha=0.8)
        ax.step(times, num_busy, where='post', label='Ls (in service)', 
                linewidth=1.5, alpha=0.8)
        
        # Add average lines
        stats = network.get_statistics()[queue_id]
        ax.axhline(stats['Lq'], color='blue', linestyle='--', 
                   linewidth=1, alpha=0.5, label=f"Avg Lq = {stats['Lq']:.2f}")
        ax.axhline(stats['L'], color='orange', linestyle='--', 
                   linewidth=1, alpha=0.5, label=f"Avg L = {stats['L']:.2f}")
        
        ax.set_xlabel('Time', fontsize=11)
        ax.set_ylabel('Number of Customers', fontsize=11)
        ax.set_title(f'Queue {queue_id} - Time Evolution', fontsize=12)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
    
    fig.suptitle(title, fontsize=14, y=1.00)
    plt.tight_layout()
    plt.show()


def plot_utilization_comparison(stats_dict, title="Server Utilization by Queue"):
    """
    Plot server utilization for all queues.
    
    Parameters
    ----------
    stats_dict : dict
        Dictionary of statistics from get_statistics()
    title : str, optional
        Plot title
    """
    queue_ids = list(stats_dict.keys())
    utilizations = [stats_dict[qid]['rho'] for qid in queue_ids]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(queue_ids, utilizations, color='steelblue', alpha=0.7, edgecolor='black')
    
    # Add value labels on bars
    for bar, util in zip(bars, utilizations):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{util:.3f}',
                ha='center', va='bottom', fontsize=10)
    
    # Add reference line at ρ=1
    plt.axhline(1.0, color='red', linestyle='--', linewidth=2, 
                label='ρ = 1.0 (Full utilization)', alpha=0.7)
    
    plt.xlabel('Queue ID', fontsize=12)
    plt.ylabel('Server Utilization (ρ)', fontsize=12)
    plt.title(title, fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.ylim(0, max(1.2, max(utilizations) * 1.1))
    plt.tight_layout()
    plt.show()


def export_statistics_to_csv(stats_dict, filename="simulation_statistics.csv"):
    """
    Export statistics to CSV file.
    
    Parameters
    ----------
    stats_dict : dict
        Dictionary of statistics from get_statistics()
    filename : str, optional
        Output filename
    """
    import csv
    
    with open(filename, 'w', newline='') as csvfile:
        # Define all possible fields
        fieldnames = [
            'queue_id', 'num_served', 'total_arrivals', 'accepted_arrivals', 
            'rejected_arrivals', 'lambda_eff', 'P_loss',
            'L', 'Lq', 'Ls', 'rho', 'W', 'Wq', 'Ws',
            'max_queue_length_observed',
            'littles_law_L', 'littles_law_L_ratio',
            'littles_law_Lq', 'littles_law_Lq_ratio'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for queue_id, stats in stats_dict.items():
            row = {'queue_id': queue_id}
            row.update(stats)
            writer.writerow(row)
    
    print(f"Statistics exported to {filename}")


def create_summary_report(stats_dict, network, filename="simulation_report.txt"):
    """
    Create a comprehensive text report of simulation results.
    
    Parameters
    ----------
    stats_dict : dict
        Dictionary of statistics from get_statistics()
    network : QueueingNetwork
        The network object
    filename : str, optional
        Output filename
    """
    with open(filename, 'w') as f:
        f.write("="*80 + "\n")
        f.write("QUEUEING NETWORK SIMULATION REPORT\n")
        f.write("="*80 + "\n\n")
        
        # Network configuration
        f.write("Network Configuration:\n")
        f.write("-"*80 + "\n")
        f.write(f"  Number of queues: {len(network.queues)}\n")
        f.write(f"  Simulation time: {network.max_time}\n")
        f.write(f"  External arrival rate: {network.arrival_rate}\n")
        f.write(f"  Service rates: {network.service_rates}\n")
        f.write(f"  Number of servers: {network.num_servers}\n")
        f.write("\n")
        
        # Queue statistics
        for queue_id, stats in stats_dict.items():
            f.write("="*80 + "\n")
            f.write(f"Queue {queue_id} Statistics\n")
            f.write("="*80 + "\n\n")
            
            f.write("Arrival Statistics:\n")
            f.write(f"  Total arrivals: {stats['total_arrivals']}\n")
            f.write(f"  Accepted arrivals: {stats['accepted_arrivals']}\n")
            f.write(f"  Rejected arrivals: {stats['rejected_arrivals']}\n")
            f.write(f"  Effective arrival rate (λ_eff): {stats['lambda_eff']:.4f}\n")
            f.write(f"  Loss probability (P_loss): {stats['P_loss']:.4f}\n\n")
            
            f.write("Time-Averaged Metrics:\n")
            f.write(f"  L (avg in system): {stats['L']:.4f}\n")
            f.write(f"  Lq (avg in queue): {stats['Lq']:.4f}\n")
            f.write(f"  Ls (avg in service): {stats['Ls']:.4f}\n")
            f.write(f"  ρ (server utilization): {stats['rho']:.4f}\n\n")
            
            f.write("Customer-Averaged Metrics:\n")
            f.write(f"  W (avg time in system): {stats['W']:.4f}\n")
            f.write(f"  Wq (avg waiting time): {stats['Wq']:.4f}\n")
            f.write(f"  Ws (avg service time): {stats['Ws']:.4f}\n\n")
            
            f.write("Little's Law Verification:\n")
            f.write(f"  L = λ_eff × W: {stats['L']:.4f} ≈ {stats['littles_law_L']:.4f} "
                   f"(ratio: {stats['littles_law_L_ratio']:.4f})\n")
            f.write(f"  Lq = λ_eff × Wq: {stats['Lq']:.4f} ≈ {stats['littles_law_Lq']:.4f} "
                   f"(ratio: {stats['littles_law_Lq_ratio']:.4f})\n\n")
    
    print(f"Report saved to {filename}")