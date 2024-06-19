from keras.layers import Dense, Activation
from keras.models import Sequential
from keras.optimizers import Adam
import tensorflow as tf

class Brain:
    def __init__(self, NbrStates, NbrActions, alpha, batch_size=256):
        """
        Initialize the Brain.

        Args:
            NbrStates (int): Number of states.
            NbrActions (int): Number of actions.
            alpha (float): Learning rate.
            batch_size (int): Batch size for training the model.
        """
        self.NbrStates = NbrStates
        self.NbrActions = NbrActions
        self.alpha = alpha
        self.batch_size = batch_size
        self.model = self.createModel()

    def createModel(self):
        """
        Create the model for the Brain.

        Returns:
            model (Sequential): The created sequential model.
        """
        # Create a simple neural network with 256 hidden units and softmax output
        model = Sequential()
        model.add(Dense(256, activation=tf.nn.relu))  # prev 256
        model.add(Dense(self.NbrActions, activation="softmax"))
        # Use Adam optimizer with the learning rate set to alpha
        optimizer = Adam(learning_rate=self.alpha)  # Use alpha as the learning rate
        model.compile(loss="mse", optimizer=optimizer)

        return model

    def train(self, x, y, epoch=1, verbose=0):
        """
        Train the model using the given input and output.

        Args:
            x (numpy.ndarray): Input data.
            y (numpy.ndarray): Output data.
            epoch (int): Number of epochs to train.
            verbose (int): Verbosity mode.
        """
        self.model.fit(x, y, batch_size=self.batch_size, verbose=verbose)

    def predict(self, s):
        """
        Predict the output for the given input.

        Args:
            s (numpy.ndarray): Input data.

        Returns:
            numpy.ndarray: Predicted output.
        """
        return self.model.predict(s)

    def predictOne(self, s):
        """
        Predict the output for a single input.

        Args:
            s (numpy.ndarray): Input data.

        Returns:
            numpy.ndarray: Predicted output.
        """
        return self.model.predict(tf.reshape(s, [1, self.NbrStates])).flatten()

    def copy_weights(self, TrainNet):
        """
        Copy the weights from another Brain object.

        Args:
            TrainNet (Brain): The Brain object to copy the weights from.
        """
        variables1 = self.model.trainable_variables
        variables2 = TrainNet.model.trainable_variables
        for v1, v2 in zip(variables1, variables2):
            v1.assign(v2.numpy())
