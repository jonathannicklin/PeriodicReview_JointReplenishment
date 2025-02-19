import pandas as pd
import numpy as np

def load_historic_demand(file_path):
    # Load the demand data as a DataFrame
    demand_df = pd.read_csv(file_path, header=None)
    
    # Convert the DataFrame into a 2D numpy array, ensuring all values are numeric
    demand_data = []
    for row in demand_df.values:
        # Convert semicolon-separated string into a list of floats
        demand_data.append(list(map(int, row[0].split(';'))))
    
    # Convert to numpy array
    demand_data = np.array(demand_data)
    
    return demand_data

def create_empirical_distribution(demand_data, setup):
    num_items = setup['num_items']
    num_samples = setup['num_samples']
    
    empirical_distributions = []
    for i in range(num_items):

        if i >= demand_data.shape[0]:  # Check if i is within the bounds of the data
            raise IndexError(f"Item index {i} is out of bounds for demand_data with shape {demand_data.shape}.")
        
        item_demand = demand_data[i, :]  # Select the demand data for the ith item

        if item_demand.size == 0:
            raise ValueError(f"No demand data available for item {i}. Please check the input data.")
        
        # Generate empirical distribution by randomly sampling from historical data
        empirical_distribution = np.random.choice(item_demand, size=num_samples, replace=True)
        empirical_distributions.append(empirical_distribution)
    
    return np.array(empirical_distributions)
