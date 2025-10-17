class Server:
    """
    Represents a service resource at a queue.
    
    Attributes
    ----------
    server_id : int
        Unique identifier for the server within its queue
    is_busy : bool
        Whether the server is currently serving an agent
    current_agent : Agent or None
        The agent currently being served (None if idle)
    """
    
    def __init__(self, server_id):
        """
        Initialize a server.
        
        Parameters
        ----------
        server_id : int
            Unique identifier for the server within its queue
        """
        self.server_id = server_id
        self.is_busy = False
        self.current_agent = None
    
    def assign_agent(self, agent):
        """
        Assign an agent to this server.
        
        Parameters
        ----------
        agent : Agent
            The agent to serve
        """
        self.is_busy = True
        self.current_agent = agent
    
    def release_agent(self):
        """
        Release the current agent and mark server as idle.
        
        Returns
        -------
        Agent
            The agent that was being served
        """
        agent = self.current_agent
        self.is_busy = False
        self.current_agent = None
        return agent
    
    def __repr__(self):
        """String representation for debugging."""
        status = "BUSY" if self.is_busy else "IDLE"
        return f"Server(id={self.server_id}, status={status})"
