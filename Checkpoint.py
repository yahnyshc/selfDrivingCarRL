import pygame


class Checkpoint:
    def __init__(self, position, capture_radius=10, reward_value=0, distance_to_previous=0, accumulated_distance=0,
                 accumulated_reward=0):
        self.position = position  # Position is a tuple (x, y)
        self.capture_radius = capture_radius
        self.reward_value = reward_value
        self.distance_to_previous = distance_to_previous
        self.accumulated_distance = accumulated_distance
        self.accumulated_reward = accumulated_reward
        self.is_visible = True

    def get_reward_value(self, current_distance):
        """Calculates the reward earned for the given distance to this checkpoint."""
        complete_perc = (self.distance_to_previous - current_distance) / self.distance_to_previous

        if complete_perc < 0:
            return 0
        else:
            return complete_perc * self.reward_value

    def draw(self, screen):
        """Draw the checkpoint on the screen if it is visible."""
        if self.is_visible:
            pygame.draw.circle(screen, (255, 0, 0), (int(self.position[0]), int(self.position[1])),
                               int(self.capture_radius), 1)
