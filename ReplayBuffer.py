import numpy as np


class ReplayBuffer(object):
    """
    Class for storing and sampling past experiences from an agent.
    """
    def __init__(self, max_size, input_shape, n_actions, discrete=False):
        """
        Initialize the replay buffer.

        Args:
            max_size (int): Maximum size of the buffer.
            input_shape (tuple): Shape of the input state.
            n_actions (int): Number of possible actions.
            discrete (bool): Whether the actions are discrete or continuous.
        """
        # Maximum size of the buffer
        self.mem_size = max_size

        # Counter for the current memory index
        self.mem_cntr = 0

        # Whether the actions are discrete or continuous
        self.discrete = discrete

        # Memory for storing states
        self.state_memory = np.zeros((self.mem_size, input_shape))

        # Memory for storing new states
        self.new_state_memory = np.zeros((self.mem_size, input_shape))

        # Data type for storing actions
        dtype = np.int8 if self.discrete else np.float32

        # Memory for storing actions
        self.action_memory = np.zeros((self.mem_size, n_actions), dtype=dtype)

        # Memory for storing rewards
        self.reward_memory = np.zeros(self.mem_size)

        # Memory for storing terminal flags
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.float32)

    def store_transition(self, state, action, reward, state_, done):
        """
        Store a transition in the buffer.

        Args:
            state (ndarray): Current state.
            action (int or ndarray): Taken action.
            reward (float): Received reward.
            state_ (ndarray): New state.
            done (bool): Whether the episode is done.
        """
        # Get the index for the current memory
        index = self.mem_cntr % self.mem_size

        # Store the current state, action, reward, new state, and terminal flag
        self.state_memory[index] = state
        self.new_state_memory[index] = state_

        if self.discrete:
            # If the actions are discrete, store one hot encoding of actions
            actions = np.zeros(self.action_memory.shape[1])
            actions[action] = 1.0
            self.action_memory[index] = actions
        else:
            # If the actions are continuous, store the actions directly
            self.action_memory[index] = action

        self.reward_memory[index] = reward
        self.terminal_memory[index] = 1 - done

        # Increment the memory counter
        self.mem_cntr += 1

    def sample_buffer(self, batch_size):
        """
        Sample a batch from the buffer.

        Args:
            batch_size (int): Size of the batch.

        Returns:
            tuple: Tuple containing states, actions, rewards,
                   next states, and terminal flags.
        """
        # Get the maximum memory size
        max_mem = min(self.mem_cntr, self.mem_size)

        # Sample indices for the batch
        batch = np.random.choice(max_mem, batch_size)

        # Get the states, actions, rewards, next states, and terminal flags
        states = self.state_memory[batch]
        actions = self.action_memory[batch]
        rewards = self.reward_memory[batch]
        states_ = self.new_state_memory[batch]
        terminal = self.terminal_memory[batch]

        # Return the sampled batch
        return states, actions, rewards, states_, terminal
