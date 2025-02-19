import matplotlib.pyplot as plt

def plot_cost(cost_progression, num_generations):
    """
    Plot the cost progression over generations.
    
    Parameters:
        cost_progression (list): List of costs for each generation.
        num_generations (int): Total number of generations.
    """
    plt.plot(range(1, num_generations + 1), cost_progression)
    plt.xlabel('Generation')
    plt.ylabel('Cost')
    plt.title('Cost Progression Over Generations')
    plt.grid(True)
    plt.show()

def live_plot_cost(cost_progression, num_generations, ax=None):
    """
    Plot the cost progression live during the algorithm execution.
    
    Parameters:
        cost_progression (list): List of costs for each generation.
        num_generations (int): Total number of generations.
        ax (matplotlib.axes._axes.Axes, optional): The axis to plot on. Defaults to None.
    """
    if ax is None:
        # If no axis is passed, create a new one
        fig, ax = plt.subplots()

    ax.clear()  # Clear the previous plot
    ax.plot(range(1, len(cost_progression) + 1), cost_progression, color='blue')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Cost')
    ax.set_title('Live Cost Progression')
    ax.grid(True)
    plt.pause(0.1)  # Pause for a short time to allow the plot to update