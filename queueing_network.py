import numpy as np
import heapq
from agent import Agent
from queue import Queue
from config_loader import NetworkConfig

class QueueingNetwork:
    """
    Supports:
    - Jackson networks (infinite capacity)
    - Networks with finite capacity and rejection/loss
    - Multiple servers per queue
    - Probabilistic routing between queues
    - FIFO service discipline

    Parameters
    ----------
    arrival_rate : float
        External arrival rate to the first queue (lambda)
    service_rates : list of float
        Service rates (mu) for each queue
    num_servers : list of int
        Number of servers at each queue
    prob_matrix : 2D array-like
        Routing probability matrix. prob_matrix[i][j] is probability 
        of moving from queue i to queue j. Each row should sum to 1.0,
        with probability of leaving system being prob_matrix[i][i] = 0
        or routing to a sink state.
    max_time : float
        Maximum simulation time
    capacities : list of float/int, optional
        Capacity for each queue's waiting area (default: all infinite)

    Attributes
    ----------
    queues : list of Queue
        List of queue objects in the network
    event_queue : list
        Priority queue of events (time, event_type, agent_id, queue_id)
    agents_data : list
        Log of all agent statistics for analysis
    rejected_agents : list
        Log of agents rejected due to full queues
    time : float
        Current simulation time
    state_changes : dict
        Time-weighted state tracking for each queue
    server_busy_periods : list
        Log of all server busy periods
    arrival_counts : dict
        Total arrivals per queue
    accepted_arrival_counts : dict
        Accepted arrivals per queue
    """

    # Event type constants
    ARRIVAL = 0
    DEPARTURE = 1

    def __init__(self, config_path):
        """
        Initialize the queueing network from configuration file.
        
        Parameters
        ----------
        config_path : str
            Path to YAML configuration file
        """
        # Load and validate configuration
        self.config = NetworkConfig(config_path)
        self.config.load()
        self.config.validate()
        self.config.print_summary()
        
        # Extract parameters from config
        self.max_time = self.config.get_max_time()
        num_servers = self.config.get_num_servers()
        capacities = self.config.get_capacities()
        
        # Multi-class parameters
        self.categories = self.config.get_category_names()
        self.category_probs = self.config.get_category_arrival_probabilities()
        self.routing_matrices = {cat: self.config.get_routing_matrix(cat) for cat in self.categories}
        self.category_service_rates = {cat: self.config.get_service_rates(cat) for cat in self.categories}
        
        # Arrival parameters
        self.arrival_rate = self.config.get_external_arrival_rate()
        self.arrival_queue_id = self.config.get_arrival_queue()
        
        # Create queues (service rates will be category-specific, so use dummy values here)
        # We'll override service time generation in assign_server()
        self.queues = [
            Queue(i, num_servers[i], service_rate=1.0, capacity=capacities[i])
            for i in range(self.config.get_num_queues())
        ]
        
        # Simulation state
        self.time = 0.0
        self.event_queue = []
        self.agents_data = []
        self.rejected_agents = []
        self.agent_counter = 0
        
        # Store agent objects for event processing
        self._active_agents = {}
        
        # Time-weighted statistics tracking
        self.state_changes = {i: [] for i in range(len(self.queues))}
        self.server_busy_periods = []
        self.arrival_counts = {i: 0 for i in range(len(self.queues))}
        self.accepted_arrival_counts = {i: 0 for i in range(len(self.queues))}
        
        # NEW: Per-category tracking
        self.arrival_counts_by_category = {cat: {i: 0 for i in range(len(self.queues))} for cat in self.categories}
        self.accepted_arrival_counts_by_category = {cat: {i: 0 for i in range(len(self.queues))} for cat in self.categories}
        self.agents_data_by_category = {cat: [] for cat in self.categories}

    def record_state_change(self, queue_id):
        """
        Record the current state of a queue for time-weighted statistics.
        
        This should be called whenever the queue state changes:
        - Before/after an arrival
        - Before/after a departure
        - When an agent is assigned to a server
        
        Parameters
        ----------
        queue_id : int
            ID of the queue whose state changed
        """
        queue = self.queues[queue_id]
        
        # Get current state
        queue_length = queue.get_current_queue_length()
        system_length = queue.get_current_system_length()
        num_busy = queue.get_num_busy_servers()
        
        # Record: (time, queue_length, system_length, num_busy_servers)
        self.state_changes[queue_id].append(
            (self.time, queue_length, system_length, num_busy)
        )

    def schedule_next_arrival(self):
        """Schedule the next external arrival with random category assignment."""
        interarrival_time = Agent.generate_interarrival_time(self.arrival_rate)
        next_arrival_time = self.time + interarrival_time
        
        if next_arrival_time <= self.max_time:
            agent_id = self.agent_counter
            self.agent_counter += 1
            
            # NEW: Assign category based on arrival probabilities
            category = self._assign_category()
            
            heapq.heappush(
                self.event_queue, 
                (next_arrival_time, self.ARRIVAL, agent_id, self.arrival_queue_id, category)
            )
    
    def _assign_category(self):
        """
        Randomly assign a category based on arrival probabilities.
        
        Returns
        -------
        str
            Category name
        """
        categories = list(self.category_probs.keys())
        probabilities = list(self.category_probs.values())
        return np.random.choice(categories, p=probabilities)

    def handle_arrival(self, agent, queue_id):
        """
        Handle agent arrival at a queue.
        
        Parameters
        ----------
        agent : Agent
            The arriving agent
        queue_id : int
            ID of the queue being entered
        """
        # NEW: Increment arrival count for this queue and category
        self.arrival_counts[queue_id] += 1
        if agent.category:
            self.arrival_counts_by_category[agent.category][queue_id] += 1
        
        # Record state BEFORE arrival
        self.record_state_change(queue_id)
        
        queue = self.queues[queue_id]
        agent.queue_length_on_arrival = len(queue.waiting_queue)
        
        # Try to find free server
        free_server = queue.get_free_server()
        
        if free_server:
            # Assign to free server immediately
            self.assign_server(free_server, agent, queue_id)
            # NEW: Increment accepted arrival count
            self.accepted_arrival_counts[queue_id] += 1
            if agent.category:
                self.accepted_arrival_counts_by_category[agent.category][queue_id] += 1
        else:
            # Try to join waiting queue
            if queue.add_to_queue(agent):
                # Successfully added to queue
                self.accepted_arrival_counts[queue_id] += 1
                if agent.category:
                    self.accepted_arrival_counts_by_category[agent.category][queue_id] += 1
                self.record_state_change(queue_id)
            else:
                # Queue is full - reject agent
                print(f"Time {self.time:.3f}: Queue {queue_id} FULL - "
                    f"Agent {agent.agent_id} (Category: {agent.category}) REJECTED")
                self.rejected_agents.append({
                    'agent_id': agent.agent_id,
                    'rejection_time': self.time,
                    'queue_id': queue_id,
                    'category': agent.category
                })
                return  # Agent leaves system
        
        # Schedule next external arrival (only for arrival queue)
        if queue_id == self.arrival_queue_id:
            self.schedule_next_arrival()
        
        print(f"Time {self.time:.3f}: Agent {agent.agent_id} (Category: {agent.category}) ARRIVES at "
            f"Queue {queue_id}, Server: {agent.server_id}")

    def handle_departure(self, agent, queue_id):
        """
        Handle agent departure from a queue.
        
        Parameters
        ----------
        agent : Agent
            The departing agent
        queue_id : int
            ID of the queue being departed
        """
        # Record state BEFORE departure
        self.record_state_change(queue_id)
        
        queue = self.queues[queue_id]
        
        # Log departure statistics
        self.log_departure(agent, queue_id)
        
        # Release server and record busy period
        server = queue.servers[agent.server_id]
        
        self.server_busy_periods.append({
            'queue_id': queue_id,
            'server_id': server.server_id,
            'start_time': agent.service_start_time,
            'end_time': self.time,
            'category': agent.category  # NEW: track category
        })
        
        server.release_agent()
        
        # Record state AFTER server released
        self.record_state_change(queue_id)
        
        # Check if there's a waiting agent
        next_agent = queue.get_next_agent()
        if next_agent:
            self.assign_server(server, next_agent, queue_id)
        
        # NEW: Determine next destination using agent's category routing
        next_queue_id = self.route_agent(agent, queue_id)
        
        if next_queue_id is not None and next_queue_id != queue_id:
            # Agent moves to another queue
            agent.arrival_time = self.time
            agent.server_id = None
            self.handle_arrival(agent, next_queue_id)
        
        print(f"Time {self.time:.3f}: Agent {agent.agent_id} (Category: {agent.category}) DEPARTS from "
            f"Queue {queue_id}, Server: {server.server_id}")

    def assign_server(self, server, agent, queue_id):
        """
        Assign an agent to a server and schedule departure.
        
        Parameters
        ----------
        server : Server
            The server to assign
        agent : Agent
            The agent to serve
        queue_id : int
            ID of the current queue
        """
        server.assign_agent(agent)
        agent.service_start_time = self.time
        agent.server_id = server.server_id
        
        # Record state AFTER server assignment
        self.record_state_change(queue_id)
        
        # NEW: Generate service time based on agent category
        if agent.category:
            service_time = self.queues[queue_id].generate_service_time_for_category(
                agent.category, self.category_service_rates
            )
        else:
            service_time = self.queues[queue_id].generate_service_time()
        
        agent.departure_time = self.time + service_time
        
        heapq.heappush(
            self.event_queue,
            (agent.departure_time, self.DEPARTURE, agent.agent_id, queue_id)
        )

    def route_agent(self, agent, current_queue_id):
        """
        Determine next queue based on agent's category routing matrix.
        
        Parameters
        ----------
        agent : Agent
            The agent being routed
        current_queue_id : int
            Current queue ID
        
        Returns
        -------
        int or None
            Next queue ID, or None if agent leaves system
        """
        # Get routing probabilities for this agent's category
        if agent.category:
            prob_matrix = self.routing_matrices[agent.category]
            probabilities = prob_matrix[current_queue_id]
        else:
            # Fallback: exit system
            return None
        
        # Check if agent should exit the system
        if all(p == 0 for p in probabilities) or sum(probabilities) == 0:
            return None
        
        # If probabilities don't sum to 1, there's implicit exit probability
        prob_sum = sum(probabilities)
        if prob_sum < 1.0:
            if np.random.random() > prob_sum:
                return None
            probabilities = [p / prob_sum for p in probabilities]
        
        # Sample next queue
        next_queue_id = np.random.choice(len(probabilities), p=probabilities)
        
        return next_queue_id

    def log_departure(self, agent, queue_id):
        """
        Log agent statistics for analysis.
        
        Parameters
        ----------
        agent : Agent
            The departing agent
        queue_id : int
            Queue from which agent is departing
        """
        departure_record = [
            agent.agent_id,
            agent.arrival_time,
            agent.service_start_time,
            agent.departure_time,
            agent.server_id,
            queue_id,
            agent.queue_length_on_arrival
        ]
        self.agents_data.append(departure_record)
        
        # NEW: Also log by category
        if agent.category:
            self.agents_data_by_category[agent.category].append(departure_record)

    def calculate_time_weighted_metrics(self, queue_id):
        """
        Calculate time-weighted averages for L, Lq, and Ls.
        
        Parameters
        ----------
        queue_id : int
            Queue ID to calculate metrics for
        
        Returns
        -------
        dict
            Dictionary with keys: 'L', 'Lq', 'Ls' (time-weighted averages)
        """
        state_data = self.state_changes[queue_id]
        
        if len(state_data) < 2:
            # Not enough data
            return {'L': 0.0, 'Lq': 0.0, 'Ls': 0.0}
        
        total_L = 0.0
        total_Lq = 0.0
        total_Ls = 0.0
        
        # Calculate time-weighted averages
        for i in range(len(state_data) - 1):
            current_time, queue_length, system_length, num_busy = state_data[i]
            next_time = state_data[i + 1][0]
            
            duration = next_time - current_time
            
            # Time-weighted contributions
            total_Lq += queue_length * duration
            total_L += system_length * duration
            total_Ls += num_busy * duration
        
        # Add final period (from last state change to end of simulation)
        if state_data:
            last_time, queue_length, system_length, num_busy = state_data[-1]
            final_duration = self.max_time - last_time
            
            total_Lq += queue_length * final_duration
            total_L += system_length * final_duration
            total_Ls += num_busy * final_duration
        
        # Divide by total time
        time_weighted_L = total_L / self.max_time if self.max_time > 0 else 0.0
        time_weighted_Lq = total_Lq / self.max_time if self.max_time > 0 else 0.0
        time_weighted_Ls = total_Ls / self.max_time if self.max_time > 0 else 0.0
        
        return {
            'L': time_weighted_L,
            'Lq': time_weighted_Lq,
            'Ls': time_weighted_Ls
        }

    def calculate_server_utilization(self, queue_id):
        """
        Calculate server utilization (rho) for a queue.
        
        Parameters
        ----------
        queue_id : int
            Queue ID
        
        Returns
        -------
        float
            Server utilization (fraction of time servers are busy)
        """
        # Filter busy periods for this queue
        queue_busy_periods = [
            bp for bp in self.server_busy_periods 
            if bp['queue_id'] == queue_id
        ]
        
        if not queue_busy_periods:
            return 0.0
        
        # Sum total busy time across all servers
        total_busy_time = sum(
            bp['end_time'] - bp['start_time'] 
            for bp in queue_busy_periods
        )
        
        # Total available server time
        num_servers = self.queues[queue_id].num_servers
        total_available_time = num_servers * self.max_time
        
        utilization = total_busy_time / total_available_time if total_available_time > 0 else 0.0
        
        return utilization

    def calculate_effective_arrival_rate(self, queue_id):
        """
        Calculate effective arrival rate (accepted arrivals / time).
        
        Parameters
        ----------
        queue_id : int
            Queue ID
        
        Returns
        -------
        float
            Effective arrival rate (customers/time unit)
        """
        accepted_arrivals = self.accepted_arrival_counts[queue_id]
        lambda_eff = accepted_arrivals / self.max_time if self.max_time > 0 else 0.0
        return lambda_eff

    def calculate_loss_probability(self, queue_id):
        """
        Calculate loss/rejection probability for a queue.
        
        Parameters
        ----------
        queue_id : int
            Queue ID
        
        Returns
        -------
        float
            Loss probability (fraction of arrivals rejected)
        """
        total_arrivals = self.arrival_counts[queue_id]
        
        if total_arrivals == 0:
            return 0.0
        
        rejections = sum(
            1 for r in self.rejected_agents 
            if r['queue_id'] == queue_id
        )
        
        loss_prob = rejections / total_arrivals
        return loss_prob

    def get_statistics(self):
        """
        Compute comprehensive statistics from simulation results.
        
        Returns both time-averaged metrics (L, Lq, Ls, ρ) and 
        customer-averaged metrics (W, Wq, Ws).
        
        Returns
        -------
        dict
            Dictionary of performance metrics by queue, including:
            - Time-averaged: L, Lq, Ls, rho (server utilization)
            - Customer-averaged: W, Wq, Ws
            - Throughput: lambda_eff (effective arrival rate)
            - Loss: P_loss (rejection probability)
            - Verification: Little's Law ratios
        """
        if not self.agents_data:
            return {}
        
        data = np.array(self.agents_data)
        stats = {}
        
        for queue_id in range(len(self.queues)):
            queue_data = data[data[:, 5] == queue_id]
            
            # Initialize stats dictionary for this queue
            queue_stats = {}
            
            # ============================================================
            # CUSTOMER-AVERAGED METRICS (from agent data)
            # ============================================================
            if len(queue_data) > 0:
                waiting_times = queue_data[:, 2] - queue_data[:, 1]
                service_times = queue_data[:, 3] - queue_data[:, 2]
                system_times = queue_data[:, 3] - queue_data[:, 1]
                
                queue_stats['num_served'] = len(queue_data)
                queue_stats['W'] = np.mean(system_times)   # Avg time in system
                queue_stats['Wq'] = np.mean(waiting_times)  # Avg waiting time
                queue_stats['Ws'] = np.mean(service_times)  # Avg service time
                queue_stats['max_queue_length_observed'] = np.max(queue_data[:, 6])
            else:
                queue_stats['num_served'] = 0
                queue_stats['W'] = 0.0
                queue_stats['Wq'] = 0.0
                queue_stats['Ws'] = 0.0
                queue_stats['max_queue_length_observed'] = 0
            
            # ============================================================
            # TIME-AVERAGED METRICS
            # ============================================================
            time_metrics = self.calculate_time_weighted_metrics(queue_id)
            queue_stats['L'] = time_metrics['L']    # Avg number in system
            queue_stats['Lq'] = time_metrics['Lq']  # Avg number in queue
            queue_stats['Ls'] = time_metrics['Ls']  # Avg number in service
            
            # ============================================================
            # THROUGHPUT AND UTILIZATION
            # ============================================================
            queue_stats['lambda_eff'] = self.calculate_effective_arrival_rate(queue_id)
            queue_stats['rho'] = self.calculate_server_utilization(queue_id)
            
            # ============================================================
            # LOSS PROBABILITY (for finite capacity)
            # ============================================================
            queue_stats['P_loss'] = self.calculate_loss_probability(queue_id)
            queue_stats['total_arrivals'] = self.arrival_counts[queue_id]
            queue_stats['accepted_arrivals'] = self.accepted_arrival_counts[queue_id]
            queue_stats['rejected_arrivals'] = self.arrival_counts[queue_id] - self.accepted_arrival_counts[queue_id]
            
            # ============================================================
            # LITTLE'S LAW VERIFICATION
            # ============================================================
            # L = λ * W (should be approximately equal)
            if queue_stats['lambda_eff'] > 0 and queue_stats['W'] > 0:
                expected_L = queue_stats['lambda_eff'] * queue_stats['W']
                queue_stats['littles_law_L'] = expected_L
                queue_stats['littles_law_L_ratio'] = queue_stats['L'] / expected_L if expected_L > 0 else 0.0
            else:
                queue_stats['littles_law_L'] = 0.0
                queue_stats['littles_law_L_ratio'] = 0.0
            
            # Lq = λ * Wq
            if queue_stats['lambda_eff'] > 0 and queue_stats['Wq'] > 0:
                expected_Lq = queue_stats['lambda_eff'] * queue_stats['Wq']
                queue_stats['littles_law_Lq'] = expected_Lq
                queue_stats['littles_law_Lq_ratio'] = queue_stats['Lq'] / expected_Lq if expected_Lq > 0 else 0.0
            else:
                queue_stats['littles_law_Lq'] = 0.0
                queue_stats['littles_law_Lq_ratio'] = 0.0
            
            stats[queue_id] = queue_stats
        
        return stats

    def simulate(self):
        """
        Run the discrete-event simulation.
        
        Returns
        -------
        numpy.ndarray
            Array of agent statistics
        """
        print(f"Starting simulation: max_time={self.max_time}")
        print(f"Network configuration: {len(self.queues)} queues, {len(self.categories)} categories")
        print("-" * 60)
        
        # Record initial state
        for queue_id in range(len(self.queues)):
            self.record_state_change(queue_id)
        
        # Schedule first arrival
        self.schedule_next_arrival()
        
        # Main event loop
        while self.event_queue and self.time <= self.max_time:
            # NEW: Event now includes category
            event = heapq.heappop(self.event_queue)
            
            if len(event) == 5:  # ARRIVAL event with category
                self.time, event_type, agent_id, queue_id, category = event
            else:  # DEPARTURE event
                self.time, event_type, agent_id, queue_id = event
                category = None  # Will be retrieved from agent
            
            if self.time > self.max_time:
                break
            
            if event_type == self.ARRIVAL:
                # Create new agent with category
                if agent_id not in self._active_agents:
                    agent = Agent(self.time, agent_id, category=category)
                    self._active_agents[agent_id] = agent
                else:
                    agent = self._active_agents[agent_id]
                
                self.handle_arrival(agent, queue_id)
            
            elif event_type == self.DEPARTURE:
                agent = self._active_agents[agent_id]
                self.handle_departure(agent, queue_id)
        
        print("-" * 60)
        print(f"Simulation complete: {len(self.agents_data)} departures recorded")
        print(f"Rejected agents: {len(self.rejected_agents)}")
        
        return np.array(self.agents_data)
    
    def get_statistics_by_category(self):
        """
        Compute statistics separated by category.
        
        Returns
        -------
        dict
            Nested dictionary: {category: {queue_id: stats}}
        """
        if not self.agents_data:
            return {}
        
        data = np.array(self.agents_data)
        stats_by_category = {cat: {} for cat in self.categories}
        
        for category in self.categories:
            for queue_id in range(len(self.queues)):
                # Filter data for this category and queue
                # Note: agents_data doesn't have category info, need to track separately
                # This will be added to log_departure method
                queue_stats = {}
                
                # Use category-specific tracking
                queue_stats['total_arrivals'] = self.arrival_counts_by_category[category][queue_id]
                queue_stats['accepted_arrivals'] = self.accepted_arrival_counts_by_category[category][queue_id]
                queue_stats['rejected_arrivals'] = (
                    self.arrival_counts_by_category[category][queue_id] - 
                    self.accepted_arrival_counts_by_category[category][queue_id]
                )
                queue_stats['lambda_eff'] = (
                    self.accepted_arrival_counts_by_category[category][queue_id] / self.max_time 
                    if self.max_time > 0 else 0.0
                )
                
                stats_by_category[category][queue_id] = queue_stats
        
        return stats_by_category
    
