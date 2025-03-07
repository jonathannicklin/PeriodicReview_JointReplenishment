import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PeriodicReview_JointReplenishment.demand import load_historic_demand, create_empirical_distribution
from PeriodicReview_JointReplenishment.simulation import load_setup
from PeriodicReview_JointReplenishment.genetic_algorithm import genetic_algorithm

def main():
    # Load demand data and setup configuration
    demand_data = load_historic_demand('data/sample_data.csv')
    setup = load_setup('data/setup.json')
    num_cores = os.cpu_count()
    print(f"Number of CPU cores available: {num_cores}")

    # Create the empirical demand distribution
    demand_distribution = create_empirical_distribution(demand_data, setup)
    
    # Run the genetic algorithm to get the best policies
    best_policies = genetic_algorithm(demand_distribution, setup)

    # Save the best policies to a .txt file
    with open('best_policies.txt', 'w') as file:
        file.write("Best Policies, Costs, and Service Levels:\n")
        for policies, cost, service_level, container_fill_rate, periodicity in best_policies:
            file.write(f"Policies: {policies}, Cost = {cost:.2f}, Service Level = {service_level:.2f}%, Fill Rate = {container_fill_rate:.2f}%, Periodicity = {periodicity:.2f}\n")
    
    # Print the top 10 best policies along with their costs and service levels
    print("Top 10 Best Policies, Costs, and Service Levels:")
    for policies, cost, service_level, container_fill_rate, periodicity in best_policies:
        print(f"Policies: {policies}, Cost = {cost:.2f}, Service Level = {service_level:.2f}%, Fill Rate = {container_fill_rate:.2f}%, Periodicity = {periodicity:.3f}")

if __name__ == "__main__":
    main()
