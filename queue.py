import numpy as np
from server import Server


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
    
    def __init__(self, queue_id, num_servers, service_rate, capacity=float('inf')):
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
        capacity : float or int, optional
            Maximum waiting queue capacity (default: infinite)
        """
        self.queue_id = queue_id
        self.num_servers = num_servers
        self.service_rate = service_rate
        self.capacity = capacity
        self.servers = [Server(i) for i in range(num_servers)]
        self.waiting_queue = []
    
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
        if self.waiting_queue:
            return self.waiting_queue.pop(0)
        return None
    
    def generate_service_time(self):
        """
        Generate exponentially distributed service time.
        
        Returns
        -------
        float
            Service time
        """
        return np.random.exponential(1.0 / self.service_rate)
    
    def __repr__(self):
        """String representation for debugging."""
        busy_servers = sum(1 for s in self.servers if s.is_busy)
        return (f"Queue(id={self.queue_id}, servers={busy_servers}/{self.num_servers}, "
                f"waiting={len(self.waiting_queue)}, capacity={self.capacity})")
