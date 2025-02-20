import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PeriodicReview_JointReplenishment.demand import load_historic_demand, create_empirical_distribution
from PeriodicReview_JointReplenishment.simulation import load_setup
from PeriodicReview_JointReplenishment.genetic_algorithm import genetic_algorithm

def main():
    demand_data = load_historic_demand('data/sample_data.csv')
    setup = load_setup('data/setup.json')
    num_cores = os.cpu_count()
    print(f"Number of CPU cores available: {num_cores}")

    demand_distribution = create_empirical_distribution(demand_data, setup)
    
    best_policies = genetic_algorithm(demand_distribution, setup)
    
    print("Top 10 Best Policies and Costs per Period:")
    for policies, cost in best_policies:
        print(f"Policies: {policies}, Cost = {cost}")

if __name__ == "__main__":
    main()