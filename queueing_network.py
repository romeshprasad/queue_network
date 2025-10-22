import numpy as np
import heapq
from agent import Agent
from queue import Queue


class QueueingNetwork:
    """
    Discrete-event simulator for open queueing networks.
    
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
    """
    
    # Event type constants
    ARRIVAL = 0
    DEPARTURE = 1
    
    def __init__(self, arrival_rate, service_rates, num_servers, prob_matrix, 
                 max_time, capacities=None):
        """Initialize the queueing network simulation."""
        self.arrival_rate = arrival_rate
        self.service_rates = service_rates
        self.num_servers = num_servers
        self.prob_matrix = prob_matrix
        self.max_time = max_time
        
        # Set capacities (default to infinite)
        if capacities is None:
            capacities = [float('inf')] * len(num_servers)
        
        # Create queues
        self.queues = [
            Queue(i, num_servers[i], service_rates[i], capacities[i])
            for i in range(len(num_servers))
        ]
        
        # Simulation state
        self.time = 0.0
        self.event_queue = []
        self.agents_data = []
        self.rejected_agents = []
        self.agent_counter = 0
        
        # Store agent objects for event processing
        self._active_agents = {}
    
    def schedule_next_arrival(self):
        """Schedule the next external arrival to the first queue."""
        interarrival_time = Agent.generate_interarrival_time(self.arrival_rate)
        next_arrival_time = self.time + interarrival_time
        
        if next_arrival_time <= self.max_time:
            agent_id = self.agent_counter
            self.agent_counter += 1
            heapq.heappush(
                self.event_queue, 
                (next_arrival_time, self.ARRIVAL, agent_id, 0)
            )
    
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
        queue = self.queues[queue_id]
        agent.queue_length_on_arrival = len(queue.waiting_queue)
        
        # Try to find free server
        free_server = queue.get_free_server()
        
        if free_server:
            # Assign to free server immediately
            self.assign_server(free_server, agent, queue_id)
        else:
            # Try to join waiting queue
            if queue.add_to_queue(agent):
                # Successfully added to queue
                pass
            else:
                # Queue is full - reject agent
                print(f"Time {self.time:.3f}: Queue {queue_id} FULL - "
                      f"Agent {agent.agent_id} REJECTED")
                self.rejected_agents.append({
                    'agent_id': agent.agent_id,
                    'rejection_time': self.time,
                    'queue_id': queue_id
                })
                return  # Agent leaves system
        
        # Schedule next external arrival (only for first queue)
        if queue_id == 0:
            self.schedule_next_arrival()
        
        print(f"Time {self.time:.3f}: Agent {agent.agent_id} ARRIVES at "
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
        queue = self.queues[queue_id]
        
        # Log departure statistics
        self.log_departure(agent, queue_id)
        
        # Release server
        server = queue.servers[agent.server_id]
        server.release_agent()
        
        # Check if there's a waiting agent
        next_agent = queue.get_next_agent()
        if next_agent:
            self.assign_server(server, next_agent, queue_id)
        
        # Determine next destination using routing probability
        next_queue_id = self.route_agent(queue_id)
        
        if next_queue_id is not None and next_queue_id != queue_id:
            # Agent moves to another queue
            agent.arrival_time = self.time
            agent.server_id = None  # Will be reassigned at next queue
            self.handle_arrival(agent, next_queue_id)
        
        print(f"Time {self.time:.3f}: Agent {agent.agent_id} DEPARTS from "
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
        
        # Generate service time and schedule departure
        service_time = self.queues[queue_id].generate_service_time()
        agent.departure_time = self.time + service_time
        
        heapq.heappush(
            self.event_queue,
            (agent.departure_time, self.DEPARTURE, agent.agent_id, queue_id)
        )
    
    def route_agent(self, current_queue_id):
        """
        Determine next queue based on routing probability matrix.
        
        Parameters
        ----------
        current_queue_id : int
            Current queue ID
        
        Returns
        -------
        int or None
            Next queue ID, or None if agent leaves system
        """
        probabilities = self.prob_matrix[current_queue_id]
        
        # Check if agent should exit the system BEFORE sampling
        # Exit if all probabilities are 0 or sum to 0
        if all(p == 0 for p in probabilities) or sum(probabilities) == 0:
            return None
        
        # If probabilities don't sum to 1, normalize them or check for exit probability
        prob_sum = sum(probabilities)
        if prob_sum < 1.0:
            # There's an implicit exit probability of (1 - prob_sum)
            # Decide if agent exits or routes to another queue
            if np.random.random() > prob_sum:
                return None
            # Otherwise, normalize and sample from remaining probabilities
            probabilities = [p / prob_sum for p in probabilities]
        
        # Sample next queue from the probability distribution
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
        self.agents_data.append([
            agent.agent_id,
            agent.arrival_time,
            agent.service_start_time,
            agent.departure_time,
            agent.server_id,
            queue_id,
            agent.queue_length_on_arrival
        ])
    
    def simulate(self):
        """
        Run the discrete-event simulation.
        
        Returns
        -------
        numpy.ndarray
            Array of agent statistics with columns:
            [agent_id, arrival_time, service_start_time, departure_time, 
             server_id, queue_id, queue_length_on_arrival]
        """
        print(f"Starting simulation: max_time={self.max_time}")
        print(f"Network configuration: {len(self.queues)} queues")
        print("-" * 60)
        
        # Schedule first arrival
        self.schedule_next_arrival()
        
        # Main event loop
        while self.event_queue and self.time <= self.max_time:
            # Get next event
            self.time, event_type, agent_id, queue_id = heapq.heappop(self.event_queue)
            
            if self.time > self.max_time:
                break
            
            if event_type == self.ARRIVAL:
                # Create new agent or retrieve existing one
                if agent_id not in self._active_agents:
                    agent = Agent(self.time, agent_id)
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
    
    def get_statistics(self):
        """
        Compute summary statistics from simulation results.
        
        Returns
        -------
        dict
            Dictionary of performance metrics by queue
        """
        if not self.agents_data:
            return {}
        
        data = np.array(self.agents_data)
        stats = {}
        
        for queue_id in range(len(self.queues)):
            queue_data = data[data[:, 5] == queue_id]
            
            if len(queue_data) > 0:
                waiting_times = queue_data[:, 2] - queue_data[:, 1]
                service_times = queue_data[:, 3] - queue_data[:, 2]
                system_times = queue_data[:, 3] - queue_data[:, 1]
                queue_lengths = queue_data[:, 6]
                
                stats[queue_id] = {
                    'num_served': len(queue_data),
                    'avg_waiting_time': np.mean(waiting_times),
                    'avg_service_time': np.mean(service_times),
                    'avg_system_time': np.mean(system_times),
                    'avg_queue_length': np.mean(queue_lengths),
                    'max_queue_length': np.max(queue_lengths)
                }
        
        return stats
