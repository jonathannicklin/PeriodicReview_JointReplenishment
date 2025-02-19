import random
import sys
import time
from src.PeriodicReview_JointReplenishment.simulation import simulate_policy
from src.PeriodicReview_JointReplenishment.graph import plot_cost, live_plot_cost
import matplotlib.pyplot as plt

def initialize_population(pop_size, num_items, setup):
    population = []

    # Generate random population of (r, s, S) policy combinations for all items
    for _ in range(pop_size):
        policies = []
        for _ in range(num_items):
            s = random.randint(1, 50)  # Generate a unique 's' for each item
            S = random.randint(s + 1, 100)  # Ensure 's' is smaller than 'S'
            # Nest the (s, S) inside a list or dictionary
            policies.append([setup['review_period'], s, S])  # [review_period, s, S] for each policy item
        population.append(policies)
    return population

def evaluate_fitness(population, demand_distribution, setup):
    fitness_scores = []

    # Determine performance of inventory policy combinations
    for policies in population:
        cost = simulate_policy(demand_distribution, policies, setup)
        fitness_scores.append((policies, cost))
    return fitness_scores

def select_parents(fitness_scores, num_parents):
    fitness_scores.sort(key=lambda x: x[1])
    return fitness_scores[:num_parents]

def crossover(parents, num_offspring):
    offspring = []

    # Combine (r, s, S) policies to generate a new policy
    for _ in range(num_offspring):
        parent1 = random.choice(parents)[0]  # Select a parent and get its policies
        parent2 = random.choice(parents)[0]  # Select another parent and get its policies

        # Create a new child by combining policies from both parents
        child = []
        valid_child = True  # Flag to check if the child is valid
        
        for p1_item, p2_item in zip(parent1, parent2):
            # Randomly select 's' and 'S'
            s = random.choice([p1_item[1], p2_item[1]])  # Select 's'
            S = random.choice([p1_item[2], p2_item[2]])  # Select 'S'

            # Ensure that s < S by checking the condition
            if s >= S:
                valid_child = False  # If invalid, mark the child as invalid
                break  # No need to continue with this child
        
            child.append([p1_item[0], s, S])  # Add the new policy to the child

        # Only add the child to the offspring if it's valid
        if valid_child:
            offspring.append(child)

    return offspring

def mutate(offspring, mutation_rate, setup):
    # Randomly modify some policies to introduce variability
    for policies in offspring:
        if random.random() < mutation_rate:
            item_index = random.randint(0, len(policies) - 1)
            s = random.randint(1, 50)
            S = random.randint(s+1, 100)
            policies[item_index] = [setup['review_period'], s, S]
    return offspring

def genetic_algorithm(demand_distribution, setup, pop_size=1000, num_generations=100, num_parents=50, mutation_rate=0.15, decay_rate=0.90, parent_fraction=0.05):
    population = initialize_population(pop_size, setup['num_items'], setup)
    cost_progression = []  # List to track cost at each generation

    # Create the initial plot
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()  # Create the plot
    live_plot_cost(cost_progression, num_generations, ax)  # Initial plot

    for generation in range(num_generations):
        # Exponentially shrink the population size
        current_pop_size = max(50, int(pop_size * (decay_rate ** generation)))  # Shrinks by decay_rate each generation, minimum 50
        
        # Adjust the number of parents based on current population size
        num_parents = max(10, int(current_pop_size * parent_fraction))  # Ensure a minimum of 10 parents
        
        # Start measuring time for the generation evaluation
        start_time = time.time()

        # Calculate fitness, select parents, perform crossover and mutation
        fitness_scores = evaluate_fitness(population, demand_distribution, setup)
        parents = select_parents(fitness_scores, num_parents)
        offspring = crossover(parents, current_pop_size - num_parents)
        offspring = mutate(offspring, mutation_rate, setup)
        population = [p[0] for p in parents] + offspring

        # Get the cost of the best policy in this generation
        best_policy = parents[0]  # Best parent based on fitness
        best_cost = best_policy[1]  # Cost is the second element in the tuple
        cost_progression.append(best_cost)

        # End measuring time for the generation evaluation
        end_time = time.time()
        generation_time = end_time - start_time  # Time taken for the evaluation of this generation

        # Update the live plot
        live_plot_cost(cost_progression, num_generations, ax)

        # Progress bar
        progress = (generation + 1) / num_generations * 100
        sys.stdout.write(f'\rGeneration {generation + 1}/{num_generations} - Progress: {progress:.2f}% - Time for evaluation: {generation_time:.2f} seconds')
        sys.stdout.flush()

    print()  # Move to the next line after the progress bar is done

    # After the loop, turn off interactive mode and show the final plot
    plt.ioff()  # Turn off interactive mode
    plt.show()

    # Save the final plot
    fig.savefig('GeneticAlgorithm_Convergence', dpi=300)

    # Return the best policies
    best_policies = select_parents(evaluate_fitness(population, demand_distribution, setup), 10)
    return best_policies