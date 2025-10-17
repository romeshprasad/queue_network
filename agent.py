import numpy as np


class Agent:
    """
    Represents an entity moving through the queueing network.
    
    Attributes
    ----------
    agent_id : int
        Unique identifier for the agent
    arrival_time : float
        Time when agent arrives at current queue
    service_start_time : float
        Time when agent begins service
    departure_time : float
        Time when agent completes service and departs
    queue_length_on_arrival : int
        Number of agents waiting when this agent arrived
    server_id : int
        ID of server providing service to this agent
    """
    
    def __init__(self, arrival_time, agent_id):
        """
        Initialize an agent.
        
        Parameters
        ----------
        arrival_time : float
            Time when agent enters the system or current queue
        agent_id : int
            Unique identifier for the agent
        """
        self.arrival_time = arrival_time
        self.service_start_time = None
        self.departure_time = None
        self.queue_length_on_arrival = None
        self.server_id = None
        self.agent_id = agent_id
    
    def __lt__(self, other):
        """
        Comparison operator for heap queue operations.
        Agents are ordered by arrival time.
        """
        return self.arrival_time < other.arrival_time
    
    def __repr__(self):
        """String representation for debugging."""
        return f"Agent(id={self.agent_id}, arrival={self.arrival_time:.3f})"
    
    @staticmethod
    def generate_interarrival_time(arrival_rate):
        """
        Generate exponentially distributed inter-arrival time.
        
        Parameters
        ----------
        arrival_rate : float
            Mean arrival rate (lambda)
        
        Returns
        -------
        float
            Inter-arrival time
        """
        return np.random.exponential(1.0 / arrival_rate)
