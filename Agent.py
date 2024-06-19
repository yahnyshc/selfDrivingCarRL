from Brain import Brain
from ReplayBuffer import ReplayBuffer
from keras.models import load_model
import numpy as np

class Agent(object):
    """Agent interacting with and learning from the environment."""

    def __init__(self, alpha, gamma, n_actions, epsilon, batch_size,
                 input_dims, epsilon_dec, epsilon_min,
                 mem_size, replace_target, fname='model/model.keras'):
        """
        Initialize the agent.

        Args:
            alpha (float): Learning rate.
            gamma (float): Discount factor.
            n_actions (int): Number of possible actions.
            epsilon (float): Exploration rate.
            batch_size (int): Batch size for training the model.
            input_dims (tuple): Dimensions of the input state.
            epsilon_dec (float): Rate at which epsilon is decremented.
            epsilon_min (float): Minimum value of epsilon.
            mem_size (int): Size of the memory buffer.
            replace_target (float): Target for updating the target network.
            fname (str): File name for saving and loading the model.
        """
        self.action_space = [i for i in range(n_actions)]
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_dec = epsilon_dec
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.model_file = fname
        self.replace_target = replace_target
        self.memory = ReplayBuffer(mem_size, input_dims, n_actions, discrete=True)

        self.brain_eval = Brain(input_dims, n_actions, alpha, batch_size)
        self.brain_target = Brain(input_dims, n_actions, alpha, batch_size)

    def remember(self, state, action, reward, new_state, done):
        """Store a transition in the memory buffer."""
        self.memory.store_transition(state, action, reward, new_state, done)

    def get_action(self, state):
        """Return the action to be taken based on the current state."""
        state = np.array(state)
        state = state[np.newaxis, :]

        rand = np.random.random()
        if rand < self.epsilon:
            action = np.random.choice(self.action_space)
        else:
            actions = self.brain_eval.predict(state)
            action = np.argmax(actions)

        return action

    def learn(self):
        """Train the model using the experiences in the memory buffer."""
        if self.memory.mem_cntr > self.batch_size:
            state, action, reward, new_state, done = self.memory.sample_buffer(self.batch_size)

            action_values = np.array(self.action_space, dtype=np.int8)
            action_indices = np.dot(action, action_values)

            q_next = self.brain_target.predict(new_state)
            q_eval = self.brain_eval.predict(new_state)
            q_pred = self.brain_eval.predict(state)

            max_actions = np.argmax(q_eval, axis=1)

            q_target = q_pred

            batch_index = np.arange(self.batch_size, dtype=np.int32)

            q_target[batch_index, action_indices] = reward + self.gamma * q_next[
                batch_index, max_actions.astype(int)] * done

            _ = self.brain_eval.train(state, q_target)

            self.epsilon = max(self.epsilon * self.epsilon_dec, self.epsilon_min)

    def update_network_parameters(self):
        """Update the target network with the parameters of the evaluation network."""
        self.brain_target.copy_weights(self.brain_eval)

    def save_model(self):
        """Save the model to a file."""
        self.brain_eval.model.save(self.model_file)

    def load_model(self):
        """Load the model from a file."""
        self.brain_eval.model = load_model(self.model_file)
        self.brain_target.model = load_model(self.model_file)

        if self.epsilon == 0.0:
            self.update_network_parameters()


