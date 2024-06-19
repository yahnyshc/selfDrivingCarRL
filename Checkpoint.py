import pygame


class Checkpoint:
    def __init__(self, position, capture_radius=25, reward_value=0, distance_to_previous=0,
                 accumulated_distance=0, accumulated_reward=0):
        """
        Initializes a Checkpoint object with the given position, capture radius, reward value,
        distance to previous checkpoint, accumulated distance, and accumulated reward.

        Args:
            position (tuple): The (x, y) position of the checkpoint.
            capture_radius (int): The radius within which the checkpoint is considered captured.
            reward_value (int): The reward earned when the checkpoint is captured.
            distance_to_previous (int): The distance to the previous checkpoint.
            accumulated_distance (int): The accumulated distance traveled since the start.
            accumulated_reward (int): The accumulated reward earned.
        """
        self.position = position
        self.capture_radius = capture_radius
        self.reward_value = reward_value
        self.distance_to_previous = distance_to_previous
        self.accumulated_distance = accumulated_distance
        self.accumulated_reward = accumulated_reward
        self.is_visible = True

    def get_reward_value(self, current_distance):
        """
        Calculates the reward earned for the given distance to this checkpoint.

        Args:
            current_distance (int): The distance to this checkpoint.

        Returns:
            int: The reward earned for the given distance.
        """
        complete_perc = (self.distance_to_previous - current_distance) / self.distance_to_previous

        if complete_perc < 0:
            return 0
        else:
            return complete_perc * self.reward_value

    def draw(self, screen):
        """
        Draws the checkpoint on the screen if it is visible.

        Args:
            screen (pygame.Surface): The surface to draw the checkpoint on.
        """
        if self.is_visible:
            pygame.draw.circle(screen, (255, 0, 0), (int(self.position[0]), int(self.position[1])),
                               int(self.capture_radius), 1)

