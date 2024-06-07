import torch
import random
import numpy as np
from collections import deque
from RaceAI import RaceAI
from Model import Linear_QNet, QTrainer
from Helper import plot
import time

MAX_MEMORY = 200_000
BATCH_SIZE = 128
LR = 0.0005

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 1.0 # randomness
        self.min_epsilon = 0.10
        self.epsilon_decay = 0.997
        self.gamma = 0.9775 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(5, 128, 128, 1)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
         state = [
             *game.car.camera_distances
         ]

         return np.array(state, dtype=float)
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        final_move = 0
        if random.random() > self.epsilon:
            move = (random.random() * 10) - 5
            final_move = move
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = prediction[0].item()
            final_move = move

        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = RaceAI()
    while True:
        game.screen.fill((255, 255, 255))
        game.draw_walls()
        # get old state
        state_old = agent.get_state(game)
        # get move
        final_move = agent.get_action(state_old)
        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)
        if done:
            # train long memory
            game.reset()
            agent.n_games += 1
            agent.epsilon = max(agent.min_epsilon, agent.epsilon_decay * agent.epsilon)
            print( "\n\nepsilon: " + str(agent.epsilon) )
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            print(plot_scores, plot_mean_scores)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()