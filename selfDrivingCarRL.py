# Import necessary libraries
import pygame
import numpy as np
from Agent import Agent
from Helper import plot
from Environment import Environment

# Initialize the game environment
game = Environment(debugging=False)

# If training is True, the agent will learn from scratch
# If training is False, the agent will load an existing model
training = False

# Constants for the agent
REPLACE_TARGET = 25  # Frequency to update the target network
MAX_MEMORY = 25000  # Maximum number of experiences stored in the memory
BATCH_SIZE = 512  # Batch size for training the model
LR = 0.001  # Learning rate for the optimizer

# Initialize the agent
agent = Agent(alpha=LR,  # Learning rate
              gamma=0.99,  # Discount factor
              n_actions=7,  # Number of actions
              epsilon=1.00 if training else 0.00,  # Exploration rate
              epsilon_min=0.10 if training else 0.00,  # Minimum exploration rate
              epsilon_dec=0.9997,  # Exponential decay rate for exploration rate
              replace_target=REPLACE_TARGET,  # Frequency to update the target network
              batch_size=BATCH_SIZE,  # Batch size for training the model
              mem_size=MAX_MEMORY,  # Maximum number of experiences stored in the memory
              input_dims=7)  # Input dimensions for the agent

# Load an existing model if not in training mode
if not training:
    agent.load_model()


def start():
    """
    Starts the game and the agent.
    """
    global training
    n_games = 1  # Number of games played
    plot_scores = []  # List to store the scores of each game
    plot_mean_scores = []  # List to store the mean scores of each game
    total_score = 0  # Total score accumulated over all games
    record = 0  # Record score achieved

    # Function to switch between learning and evaluating modes
    def switch_mode():
        """
        Switches between learning and evaluating modes.
        """
        global training
        nonlocal n_games, record
        agent.save_model()
        training = not training
        record = 0

    while True:
        game.reset()  # Reset the game environment

        score = 0  # Initialize the game score

        action = agent.get_action(game.car.raytrace_cameras())
        reward, done = game.step(action)
        state_ = game.car.get_state()
        state = np.array(state_)

        while not done:
            action = agent.get_action(state)
            reward, done = game.step(action)
            state_ = game.car.get_state()
            state_ = np.array(state_)

            agent.remember(state, action, reward, state_, int(done))
            state = state_

            if training:
                agent.learn()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        # Switch mode
                        switch_mode()
                    if event.key == pygame.K_d:
                        # Set the debug mode
                        game.debugging = not game.debugging

            score = max(reward, score)

            game.render(action, reward, agent.epsilon)

        if n_games % REPLACE_TARGET == 0 and n_games > REPLACE_TARGET:
            agent.update_network_parameters()

        if training:
            if score > record and n_games % 5 == 0:
                record = score
                agent.save_model()
                print("Record beaten. Saved model.")

            print('Game', n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / n_games
            plot_mean_scores.append(mean_score)
            print(plot_scores, plot_mean_scores)
            plot(plot_scores, plot_mean_scores)

        n_games += 1
        game.reset()


if __name__ == '__main__':
    start()
