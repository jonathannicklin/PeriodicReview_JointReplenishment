import random
import sys
from src.PeriodicReview_JointReplenishment.simulation import simulate_policy

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

def genetic_algorithm(demand_distribution, setup, pop_size=200, num_generations=20, num_parents=50, mutation_rate=0.2):
    population = initialize_population(pop_size, setup['num_items'], setup)

    for generation in range(num_generations):
        # Calculate fitness, select parents, perform crossover and mutation
        fitness_scores = evaluate_fitness(population, demand_distribution, setup)
        parents = select_parents(fitness_scores, num_parents)
        offspring = crossover(parents, pop_size - num_parents)
        offspring = mutate(offspring, mutation_rate, setup)
        population = [p[0] for p in parents] + offspring
        
        # Progress bar
        progress = (generation + 1) / num_generations * 100
        sys.stdout.write(f'\rGeneration {generation + 1}/{num_generations} - Progress: {progress:.2f}%')
        sys.stdout.flush()

    print()  # Move to the next line after the progress bar is done
    best_policies = select_parents(evaluate_fitness(population, demand_distribution, setup), 10)
    return best_policies
