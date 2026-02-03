import numpy as np
from server import Server
from distribution_model import DistributionModel


class Queue:
    """
    Represents a service station with multiple servers and a waiting queue.
    
    Attributes
    ----------
    queue_id : int
        Unique identifier for this queue
    num_servers : int
        Number of parallel servers at this queue
    service_rate : float
        Mean service rate (mu) for this queue
    capacity : float or int
        Maximum number of agents that can wait (default: infinite)
    servers : list of Server
        List of server objects
    waiting_queue : list of Agent
        List of agents waiting for service (FIFO order)
    """
    
    def __init__(self, queue_id, num_servers, service_rate = None, processing_time_model: DistributionModel = None, capacity=float('inf'), dispatch_policy=None):
        """
        Initialize a queue.
        
        Parameters
        ----------
        queue_id : int
            Unique identifier for this queue
        num_servers : int
            Number of parallel servers
        service_rate : float
            Mean service rate (mu)
        processing_time_model : ProcessingTimeModel
            service time model
            If none, use agent's value (Must not be None)
        capacity : float or int, optional
            Maximum waiting queue capacity (default: infinite)
        """
        self.queue_id = queue_id
        self.num_servers = num_servers
        self.service_rate = service_rate
        self.processing_time_model = processing_time_model
        self.capacity = capacity
        self.servers = [Server(i) for i in range(num_servers)]
        self.waiting_queue = []
        self.dispatch_policy = dispatch_policy or (lambda q: q.pop(0))
    
    def get_free_server(self):
        """
        Find an idle server.
        
        Returns
        -------
        Server or None
            First available idle server, or None if all busy
        """
        return next((server for server in self.servers if not server.is_busy), None)
    
    def is_full(self):
        """
        Check if waiting queue is at capacity.
        
        Returns
        -------
        bool
            True if queue is full, False otherwise
        """
        return len(self.waiting_queue) >= self.capacity
    
    def add_to_queue(self, agent):
        """
        Add an agent to the waiting queue.
        
        Parameters
        ----------
        agent : Agent
            Agent to add to queue
        
        Returns
        -------
        bool
            True if agent was added, False if queue is full
        """
        if self.is_full():
            return False
        self.waiting_queue.append(agent)
        return True
    
    def get_next_agent(self):
        """
        Get next agent from waiting queue (FIFO).
        
        Returns
        -------
        Agent or None
            Next agent in queue, or None if queue is empty
        """
        if not self.waiting_queue:
            return None
        
        return self.dispatch_policy(self.waiting_queue)
    
    def generate_service_time(self):
        """
        Generate exponentially distributed service time.
        
        Returns
        -------
        float
            Service time
        """
        if self.processing_time_model is not None:
            return self.processing_time_model.sample()
        elif self.service_rate is not None:
            return np.random.exponential(1.0 / self.service_rate)
        else:
            time = self.waiting_queue[0].estimate_processing_time()
            if time is None:
                raise ValueError(f"Cannot have None Processing Model for both queue and agents. At least one must be defined.")
            else:
                return time

        
    
    def get_current_queue_length(self):
        """
        Get current number of agents waiting in queue.
        
        Returns
        -------
        int
            Number of agents in waiting queue (not including those in service)
        """
        return len(self.waiting_queue)
    
    def get_current_system_length(self):
        """
        Get current total number of agents in the system.
        
        Returns
        -------
        int
            Total number of agents (waiting + in service)
        """
        busy_servers = sum(1 for s in self.servers if s.is_busy)
        return len(self.waiting_queue) + busy_servers
    
    def get_num_busy_servers(self):
        """
        Get current number of busy servers.
        
        Returns
        -------
        int
            Number of servers currently serving agents
        """
        return sum(1 for s in self.servers if s.is_busy)
    
    def __repr__(self):
        """String representation for debugging."""
        busy_servers = sum(1 for s in self.servers if s.is_busy)
        return (f"Queue(id={self.queue_id}, servers={busy_servers}/{self.num_servers}, "
                f"waiting={len(self.waiting_queue)}, capacity={self.capacity})")
    
    def generate_service_time_for_category(self, category, category_service_rates):
        """
        Generate exponentially distributed service time for a specific category.
        
        Parameters
        ----------
        category : str
            Category name
        category_service_rates : dict
            Dictionary mapping category names to service rate lists
            
        Returns
        -------
        float
            Service time
        """
        if category not in category_service_rates:
            # Fallback to base service rate
            return self.generate_service_time()
        
        service_rate = category_service_rates[category][self.queue_id]
        return np.random.exponential(1.0 / service_rate)