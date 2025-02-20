import numpy as np
import json

def load_setup(file_path):
    """
    Load setup configuration from a JSON file.
    
    Parameters:
        file_path (str): Path to the JSON file containing setup configuration.
    
    Returns:
        dict: Dictionary containing setup configuration.
    """
    with open(file_path, 'r') as file:
        setup = json.load(file)
    print("Setup data loaded")
    return setup

def is_factor(a, b):
    """
    Check if 'a' is a factor of 'b'.
    
    Parameters:
        a (int): The potential factor.
        b (int): The number to be divided.
    
    Returns:
        bool: True if 'a' is a factor of 'b', False otherwise.
    """
    return b % a == 0

def simulate_policy(demand_distribution, policies, setup):
    """
    Simulate the inventory policy to calculate the total cost based on demand distribution.
    
    Parameters:
        demand_distribution (numpy.ndarray or list): Empirical demand distribution for items.
        policies (list): List of policy combinations for each item.
        setup (dict): Dictionary containing setup parameters.
    
    Returns:
        tuple: (average total cost per sample, service level)
    """
    review_period = setup['review_period']
    holding_cost = setup['holding_cost']
    backorder_cost = setup['backorder_cost']
    order_cost = setup['order_cost']
    num_items = setup['num_items']
    lead_time = setup['lead_time']
    num_samples = setup['num_samples']
    container_volume = setup['container_volume']
    pallet_volume = setup['pallet_volume']
    warm_up = setup['warm_up']
    
    # Ensure that demand_distribution is in the correct format
    if isinstance(demand_distribution, list) and isinstance(demand_distribution[0], str):
        demand_distribution = [list(map(float, dist.split(';'))) for dist in demand_distribution]
    elif isinstance(demand_distribution, np.ndarray):
        pass
    else:
        raise ValueError("demand_distribution is not in a recognizable format")
    
    # Initialize inventory for each item
    initial_inventory = [np.sum(np.random.choice(demand_distribution[i], size=30)) for i in range(num_items)]
    inventory_level = initial_inventory[:]
    total_cost = 0
    total_demand_met = 0
    total_demand = 0
    
    # Initialize pipeline inventory (2D array)
    pipeline_inventory = np.zeros((num_items, lead_time))
    
    # Warm-up period
    for j in range(warm_up):
        for i in range(num_items):
            demand = np.random.choice(demand_distribution[i])

            if demand < 0:
                raise ValueError("demand cannot be negative!")

            inventory_level[i] -= demand
            inventory_level[i] = max(0, inventory_level[i])

            # Review inventory when in review period
            if is_factor(review_period, j):
                r, s, S = policies[i]
                if inventory_level[i] < s:
                    order_quantity = S - inventory_level[i]

                    # Add order to pipeline inventory
                    pipeline_inventory[i, lead_time - 1] += order_quantity
        
        # Update pipeline inventory
        inventory_level += pipeline_inventory[:, 0]
        pipeline_inventory[:, 0] = 0
        pipeline_inventory = np.roll(pipeline_inventory, shift=-1, axis=1)

        # Do not count costs in warm-up!
    
    # Simulation period
    total_cost = 0
    total_demand = 0
    total_demand_met = 0

    for j in range(num_samples):
        for i in range(num_items):
            demand = np.random.choice(demand_distribution[i])

            if demand < 0:
                raise ValueError("demand cannot be negative!")

            total_demand += demand

            if inventory_level[i] >= demand:
                total_demand_met += demand
                inventory_level[i] -= demand
            else:
                total_demand_met += inventory_level[i]  # Partial demand fulfillment
                total_cost += -(demand-inventory_level[i]) * backorder_cost
                inventory_level[i] = 0  # Set inventory level to zero

            # Review inventory when in a review period
            if is_factor(review_period, j):
                r, s, S = policies[i]
                if inventory_level[i] < s:
                    order_quantity = S - inventory_level[i]

                    # Add order to pipeline inventory
                    pipeline_inventory[i, lead_time - 1] += order_quantity
        
        # Add holding costs
        for i in range(num_items):
            total_cost += inventory_level[i] * holding_cost
        
        # Add ordering costs
        if np.any(pipeline_inventory[:, -1] != 0):
            total_volume = 0
            for i in range(num_items):
                total_volume += pallet_volume[i] * pipeline_inventory[i, -1]
            total_cost += np.ceil(total_volume / container_volume) * order_cost
            
        # Update pipeline inventory
        inventory_level += pipeline_inventory[:, 0]
        pipeline_inventory[:, 0] = 0
        pipeline_inventory = np.roll(pipeline_inventory, shift=-1, axis=1)

    # Calculate the service level
    service_level = 100 * (total_demand_met / total_demand) if total_demand > 0 else 1.0

    # Calculate total cost
    total_cost = total_cost / num_samples

    return total_cost, service_level