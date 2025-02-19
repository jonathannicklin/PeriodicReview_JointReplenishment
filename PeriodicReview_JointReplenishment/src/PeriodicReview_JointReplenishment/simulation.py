import numpy as np
import json

def load_setup(file_path):
    with open(file_path, 'r') as file:
        setup = json.load(file)
    print("Setup data loaded")
    return setup

def is_factor(a, b):
    return b % a == 0

def simulate_policy(demand_distribution, policies, setup):
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
    
    # Ensure that demand_distribution is correct format
    if isinstance(demand_distribution, list) and isinstance(demand_distribution[0], str):
        demand_distribution = [list(map(float, dist.split(';'))) for dist in demand_distribution]

    elif isinstance(demand_distribution, np.ndarray):
        pass
    else:
        raise ValueError("demand_distribution is not in a recognizable format")
    
    # Initialize inventory for each item
    initial_inventory = [np.sum(np.random.choice(demand_distribution[i], size=30)) for i in range(num_items)]
    inventory_position = initial_inventory[:]
    inventory_level = initial_inventory[:]
    total_cost = 0
    
    # Initialize pipeline inventory (2D array)
    pipeline_inventory = np.zeros((num_items, lead_time))
    
    # Warm-up period
    for j in range(warm_up):
        for i in range(num_items):
            demand = np.random.choice(demand_distribution[i])
            inventory_level[i] -= demand
            inventory_level[i] = max(0, inventory_level[i])
            inventory_position[i] -= demand

            # Review inventory when in review period
            if is_factor(review_period, j) == True:
                r, s, S = policies[i]
                if inventory_position[i] < s:
                    order_quantity = S - max(0, inventory_position[i]) # Inventory position can be negative
                    inventory_position[i] += order_quantity

                    # Add order to pipeline inventory
                    pipeline_inventory[i, lead_time - 1] += order_quantity
                inventory_level[i] = max(0, inventory_level[i])
        
        # Update pipeline inventory
        pipeline_inventory = np.roll(pipeline_inventory, shift=-1, axis=1)
        inventory_position += pipeline_inventory[:, 0]
        pipeline_inventory[:, 0] = 0

        # Do not count costs in warm-up!
    
    # Simulation period
    for j in range(num_samples):
        for i in range(num_items):
            demand = np.random.choice(demand_distribution[i])
            inventory_level[i] -= demand
            inventory_level[i] = max(0, inventory_level[i])
            inventory_position[i] -= demand

            # Review inventory when in a review period
            if is_factor(review_period, j) == True:
                r, s, S = policies[i]
                if inventory_position[i] < s:
                    order_quantity = S - max(0, inventory_position[i]) # Inventory position can be negative
                    inventory_position[i] += order_quantity

                    # Add order to pipeline inventory
                    pipeline_inventory[i, lead_time - 1] += order_quantity
        
        # Calculate costs
        for i in range(num_items):
            total_cost += inventory_level[i] * holding_cost
            total_cost += min(0, inventory_position[i]) * -1 * backorder_cost # use of negative inventory position to induce proper costing

        if np.any(pipeline_inventory[:, -1] != 0):
            
            # Product sum over all items
            total_volume = 0
            for i in range(num_items):
                total_volume += pallet_volume[i] * pipeline_inventory[i,-1]
            total_cost += np.ceil(total_volume/container_volume) * order_cost
            
        # Update pipeline inventory
        pipeline_inventory = np.roll(pipeline_inventory, shift=-1, axis=1)
        inventory_level += pipeline_inventory[:, 0]
        pipeline_inventory[:, 0] = 0

    return total_cost / num_samples