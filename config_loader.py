import yaml
import numpy as np


class NetworkConfig:
    """
    Loads and validates multi-class queueing network configuration from YAML.
    
    The config file should define:
    - Network parameters (num_queues, max_time)
    - Queue specifications (servers, service rates, capacity)
    - Categories (arrival probabilities, routing matrices, service rates)
    - External arrival settings
    """
    
    def __init__(self, config_path):
        """
        Initialize config loader.
        
        Parameters
        ----------
        config_path : str
            Path to YAML configuration file
        """
        self.config_path = config_path
        self.config_data = None
        self.is_loaded = False
        self.is_valid = False
    
    def load(self):
        """
        Load YAML configuration file.
        
        Raises
        ------
        FileNotFoundError
            If config file doesn't exist
        yaml.YAMLError
            If YAML parsing fails
        """
        try:
            with open(self.config_path, 'r') as f:
                self.config_data = yaml.safe_load(f)
            self.is_loaded = True
            print(f"✓ Configuration loaded from: {self.config_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"✗ Config file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"✗ Invalid YAML format: {e}")
    
    def validate(self):
        """
        Validate configuration structure and values.
        
        Checks:
        - Required sections exist
        - Category arrival probabilities sum to 1.0
        - Routing matrices are valid probability matrices
        - Service rates are positive
        - Queue IDs are consistent
        
        Raises
        ------
        ValueError
            If validation fails with specific error message
        """
        if not self.is_loaded:
            raise ValueError("✗ Config not loaded. Call load() first.")
        
        # Check required top-level sections
        required_sections = ['network', 'queues', 'categories', 'arrivals']
        for section in required_sections:
            if section not in self.config_data:
                raise ValueError(f"✗ Missing required section: '{section}'")
        
        # Validate network section
        self._validate_network_section()
        
        # Validate queues section
        self._validate_queues_section()
        
        # Validate categories section
        self._validate_categories_section()
        
        # Validate arrivals section
        self._validate_arrivals_section()
        
        self.is_valid = True
        print("✓ Configuration validation passed")
    
    def _validate_network_section(self):
        """Validate network parameters."""
        network = self.config_data['network']
        
        if 'num_queues' not in network:
            raise ValueError("✗ 'network.num_queues' is required")
        if 'max_time' not in network:
            raise ValueError("✗ 'network.max_time' is required")
        
        num_queues = network['num_queues']
        max_time = network['max_time']
        
        if not isinstance(num_queues, int) or num_queues <= 0:
            raise ValueError(f"✗ 'network.num_queues' must be positive integer, got: {num_queues}")
        if not isinstance(max_time, (int, float)) or max_time <= 0:
            raise ValueError(f"✗ 'network.max_time' must be positive number, got: {max_time}")
    
    def _validate_queues_section(self):
        """Validate queue specifications."""
        queues = self.config_data['queues']
        num_queues = self.config_data['network']['num_queues']
        
        if not isinstance(queues, list):
            raise ValueError("✗ 'queues' must be a list")
        
        if len(queues) != num_queues:
            raise ValueError(f"✗ Number of queue definitions ({len(queues)}) doesn't match "
                           f"network.num_queues ({num_queues})")
        
        queue_ids_seen = set()
        
        for i, queue in enumerate(queues):
            # Check required fields
            required_fields = ['queue_id', 'num_servers']
            for field in required_fields:
                if field not in queue:
                    raise ValueError(f"✗ Queue {i}: missing required field '{field}'")
            
            queue_id = queue['queue_id']
            num_servers = queue['num_servers']
            
            # Validate queue_id
            if not isinstance(queue_id, int) or queue_id < 0:
                raise ValueError(f"✗ Queue {i}: 'queue_id' must be non-negative integer, got: {queue_id}")
            
            if queue_id in queue_ids_seen:
                raise ValueError(f"✗ Duplicate queue_id: {queue_id}")
            queue_ids_seen.add(queue_id)
            
            if queue_id >= num_queues:
                raise ValueError(f"✗ Queue {i}: queue_id {queue_id} exceeds num_queues-1 ({num_queues-1})")
            
            # Validate num_servers
            if not isinstance(num_servers, int) or num_servers <= 0:
                raise ValueError(f"✗ Queue {queue_id}: 'num_servers' must be positive integer, got: {num_servers}")
            
            # Validate capacity (optional)
            if 'capacity' in queue:
                capacity = queue['capacity']
                if capacity != 'inf' and (not isinstance(capacity, int) or capacity <= 0):
                    raise ValueError(f"✗ Queue {queue_id}: 'capacity' must be positive integer or 'inf', got: {capacity}")
        
        # Check all queue_ids from 0 to num_queues-1 are present
        if queue_ids_seen != set(range(num_queues)):
            missing = set(range(num_queues)) - queue_ids_seen
            raise ValueError(f"✗ Missing queue IDs: {sorted(missing)}")
    
    def _validate_categories_section(self):
        """Validate category specifications."""
        categories = self.config_data['categories']
        num_queues = self.config_data['network']['num_queues']
        
        if not isinstance(categories, dict):
            raise ValueError("✗ 'categories' must be a dictionary")
        
        if len(categories) == 0:
            raise ValueError("✗ At least one category must be defined")
        
        # Check arrival probabilities sum to 1.0
        total_prob = 0.0
        category_names = []
        
        for cat_name, cat_spec in categories.items():
            category_names.append(cat_name)
            
            # Check required fields
            required_fields = ['arrival_probability', 'routing_matrix', 'service_rates']
            for field in required_fields:
                if field not in cat_spec:
                    raise ValueError(f"✗ Category '{cat_name}': missing required field '{field}'")
            
            # Validate arrival_probability
            arrival_prob = cat_spec['arrival_probability']
            if not isinstance(arrival_prob, (int, float)) or arrival_prob < 0 or arrival_prob > 1:
                raise ValueError(f"✗ Category '{cat_name}': 'arrival_probability' must be in [0, 1], got: {arrival_prob}")
            total_prob += arrival_prob
            
            # Validate routing_matrix
            routing_matrix = cat_spec['routing_matrix']
            if not isinstance(routing_matrix, list):
                raise ValueError(f"✗ Category '{cat_name}': 'routing_matrix' must be a list")
            
            if len(routing_matrix) != num_queues:
                raise ValueError(f"✗ Category '{cat_name}': 'routing_matrix' must have {num_queues} rows, got: {len(routing_matrix)}")
            
            for i, row in enumerate(routing_matrix):
                if not isinstance(row, list):
                    raise ValueError(f"✗ Category '{cat_name}': routing_matrix row {i} must be a list")
                
                if len(row) != num_queues:
                    raise ValueError(f"✗ Category '{cat_name}': routing_matrix row {i} must have {num_queues} columns, got: {len(row)}")
                
                # Check probabilities are valid
                for j, prob in enumerate(row):
                    if not isinstance(prob, (int, float)) or prob < 0 or prob > 1:
                        raise ValueError(f"✗ Category '{cat_name}': routing_matrix[{i}][{j}] must be in [0, 1], got: {prob}")
                
                # Check row sum <= 1.0
                row_sum = sum(row)
                if row_sum > 1.0 + 1e-6:  # Small tolerance for floating point
                    raise ValueError(f"✗ Category '{cat_name}': routing_matrix row {i} sums to {row_sum} > 1.0")
            
            # Validate service_rates
            service_rates = cat_spec['service_rates']
            if not isinstance(service_rates, list):
                raise ValueError(f"✗ Category '{cat_name}': 'service_rates' must be a list")
            
            if len(service_rates) != num_queues:
                raise ValueError(f"✗ Category '{cat_name}': 'service_rates' must have {num_queues} values, got: {len(service_rates)}")
            
            for i, rate in enumerate(service_rates):
                if not isinstance(rate, (int, float)) or rate <= 0:
                    raise ValueError(f"✗ Category '{cat_name}': service_rates[{i}] must be positive, got: {rate}")
        
        # Check total probability sums to 1.0
        if abs(total_prob - 1.0) > 1e-6:
            raise ValueError(f"✗ Category arrival probabilities sum to {total_prob}, must sum to 1.0")
    
    def _validate_arrivals_section(self):
        """Validate arrival parameters."""
        arrivals = self.config_data['arrivals']
        num_queues = self.config_data['network']['num_queues']
        
        if 'external_arrival_rate' not in arrivals:
            raise ValueError("✗ 'arrivals.external_arrival_rate' is required")
        if 'arrival_queue' not in arrivals:
            raise ValueError("✗ 'arrivals.arrival_queue' is required")
        
        arrival_rate = arrivals['external_arrival_rate']
        arrival_queue = arrivals['arrival_queue']
        
        if not isinstance(arrival_rate, (int, float)) or arrival_rate <= 0:
            raise ValueError(f"✗ 'arrivals.external_arrival_rate' must be positive, got: {arrival_rate}")
        
        if not isinstance(arrival_queue, int) or arrival_queue < 0 or arrival_queue >= num_queues:
            raise ValueError(f"✗ 'arrivals.arrival_queue' must be valid queue ID (0 to {num_queues-1}), got: {arrival_queue}")
    
    def get_num_queues(self):
        """Get number of queues."""
        self._check_valid()
        return self.config_data['network']['num_queues']
    
    def get_max_time(self):
        """Get simulation max time."""
        self._check_valid()
        return self.config_data['network']['max_time']
    
    def get_queue_specs(self):
        """
        Get queue specifications.
        
        Returns
        -------
        list of dict
            List of queue specifications sorted by queue_id
        """
        self._check_valid()
        queues = self.config_data['queues']
        # Sort by queue_id to ensure correct order
        return sorted(queues, key=lambda q: q['queue_id'])
    
    def get_num_servers(self):
        """Get list of num_servers for each queue."""
        self._check_valid()
        queue_specs = self.get_queue_specs()
        return [q['num_servers'] for q in queue_specs]
    
    def get_capacities(self):
        """Get list of capacities for each queue."""
        self._check_valid()
        queue_specs = self.get_queue_specs()
        capacities = []
        for q in queue_specs:
            cap = q.get('capacity', 'inf')
            if cap == 'inf':
                capacities.append(float('inf'))
            else:
                capacities.append(cap)
        return capacities
    
    def get_category_names(self):
        """Get list of category names."""
        self._check_valid()
        return list(self.config_data['categories'].keys())
    
    def get_category_arrival_probabilities(self):
        """
        Get dictionary of category arrival probabilities.
        
        Returns
        -------
        dict
            {category_name: arrival_probability}
        """
        self._check_valid()
        categories = self.config_data['categories']
        return {name: spec['arrival_probability'] for name, spec in categories.items()}
    
    def get_routing_matrix(self, category):
        """
        Get routing matrix for a specific category.
        
        Parameters
        ----------
        category : str
            Category name
        
        Returns
        -------
        list of list
            Routing probability matrix
        """
        self._check_valid()
        if category not in self.config_data['categories']:
            raise ValueError(f"✗ Unknown category: {category}")
        return self.config_data['categories'][category]['routing_matrix']
    
    def get_service_rates(self, category):
        """
        Get service rates for a specific category.
        
        Parameters
        ----------
        category : str
            Category name
        
        Returns
        -------
        list
            Service rates for each queue
        """
        self._check_valid()
        if category not in self.config_data['categories']:
            raise ValueError(f"✗ Unknown category: {category}")
        return self.config_data['categories'][category]['service_rates']
    
    def get_external_arrival_rate(self):
        """Get external arrival rate."""
        self._check_valid()
        return self.config_data['arrivals']['external_arrival_rate']
    
    def get_arrival_queue(self):
        """Get queue where external arrivals enter."""
        self._check_valid()
        return self.config_data['arrivals']['arrival_queue']
    
    def _check_valid(self):
        """Check if config is loaded and validated."""
        if not self.is_loaded:
            raise RuntimeError("✗ Config not loaded. Call load() first.")
        if not self.is_valid:
            raise RuntimeError("✗ Config not validated. Call validate() first.")
    
    def print_summary(self):
        """Print a summary of the configuration."""
        self._check_valid()
        
        print("\n" + "="*80)
        print("CONFIGURATION SUMMARY")
        print("="*80)
        
        print(f"\nNetwork:")
        print(f"  Number of queues: {self.get_num_queues()}")
        print(f"  Simulation time: {self.get_max_time()}")
        
        print(f"\nQueues:")
        for q in self.get_queue_specs():
            cap = q.get('capacity', 'inf')
            print(f"  Queue {q['queue_id']}: {q['num_servers']} server(s), capacity={cap}")
        
        print(f"\nCategories:")
        for cat_name in self.get_category_names():
            prob = self.get_category_arrival_probabilities()[cat_name]
            print(f"  {cat_name}: {prob*100:.1f}% of arrivals")
        
        print(f"\nArrivals:")
        print(f"  External arrival rate: {self.get_external_arrival_rate()}")
        print(f"  Arrival queue: {self.get_arrival_queue()}")
        
        print("="*80 + "\n")