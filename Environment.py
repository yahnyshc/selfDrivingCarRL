import random

import pygame
from Car import Car
from DataLoader import DataLoader
from Checkpoint import Checkpoint
import math
import os

class Environment:

    def __init__(self, debugging=False):
        """
        Initialize the environment.

        Args:
            debugging (bool): Whether to enable debugging mode.
        """
        # remove this line if not windows is used
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (920, 100)
        pygame.init()
        pygame.display.set_caption("Self driving car")
        self.screen = pygame.display.set_mode((1000, 700))
        self.background_img = pygame.image.load("img/path1.png")
        self.debugging = debugging
        self.walls = DataLoader().get_walls()
        self.checkpoints = self.get_checkpoints()
        self.calculate_checkpoint_percentages()
        self.clock = pygame.time.Clock()
        self.car = Car(self.screen)
        self.distance = 0
        self.reset()

    def draw_walls(self):
        """
        Draw the walls on the screen.
        """
        for x1, y1, x2, y2 in self.walls:
            pygame.draw.line(self.screen, (0, 0, 0), (x1, y1), (x2, y2), 1)

    def get_checkpoints(self):
        """
        Get the checkpoints on the track.

        Returns:
            list: List of Checkpoint objects representing the checkpoints.
        """
        cps = []
        off = int(len(self.walls)/2)
        for i in range(0, off):
            x1, y1, x2, y2 = self.walls[i]
            x3, y3, x4, y4 = self.walls[i + off]
            c = Checkpoint(((x1 + x3)/2, (y1 + y3)/2))
            cps.append(c)
            if self.debugging:
                self.screen.blit(
                    pygame.font.SysFont('Comic Sans MS', 10).render(str(i),
                    False, (255, 0, 0)),((x1 + x3)/2-5, (y1 + y3)/2-10)
                )
                #c.draw(self.screen)
        return cps

    def calculate_checkpoint_percentages(self):
        """
        Calculate the checkpoint percentages.
        """
        self.checkpoints[0].accumulated_distance = 0  # First checkpoint is start
        # Iterate over remaining checkpoints and set distance to previous and accumulated track distance
        for i in range(1, len(self.checkpoints)):
            self.checkpoints[i].distance_to_previous = self.vector2_distance(
                self.checkpoints[i].position, self.checkpoints[i - 1].position
            )
            self.checkpoints[i].accumulated_distance = (
                self.checkpoints[i - 1].accumulated_distance + self.checkpoints[i].distance_to_previous
            )

        # Set track length to accumulated distance of last checkpoint
        track_length = self.checkpoints[-1].accumulated_distance

        # Calculate reward value for each checkpoint
        for i in range(1, len(self.checkpoints)):
            self.checkpoints[i].reward_value = (
                self.checkpoints[i].accumulated_distance / track_length
            ) - self.checkpoints[i - 1].accumulated_reward
            self.checkpoints[i].accumulated_reward = (
                self.checkpoints[i - 1].accumulated_reward + self.checkpoints[i].reward_value
            )

    def get_captured_checkpoint(self, car, cur_checkpoint_index):
        """
        Get the captured checkpoint.

        Args:
            car (Car): The car object.
            cur_checkpoint_index (int): The current checkpoint index.

        Returns:
            int: The index of the captured checkpoint.
        """
        # Already all checkpoints captured
        if cur_checkpoint_index >= len(self.checkpoints):
            return 1

        # Calculate distance to next checkpoint
        check_point_distance = self.vector2_distance((car.x, car.y), self.checkpoints[cur_checkpoint_index].position)

        # Check if checkpoint can be captured
        if check_point_distance <= self.checkpoints[cur_checkpoint_index].capture_radius + 10:
            self.car.checkpoint_captured()
            return self.get_captured_checkpoint(car, cur_checkpoint_index + 1)  # Recursively check next checkpoint
        else:
            # Return accumulated reward of last checkpoint + reward of distance to next checkpoint
            # return self.checkpoints[cur_checkpoint_index - 1].accumulated_reward + self.checkpoints[cur_checkpoint_index].get_reward_value(check_point_distance)

            # Return checkpoint index instead of completion percentage
            return cur_checkpoint_index

    @staticmethod
    def vector2_distance(position1, position2):
        """
        Calculate the Euclidean distance between two points.

        Args:
            position1 (tuple): The first position.
            position2 (tuple): The second position.

        Returns:
            float: The distance between the two points.
        """
        return math.sqrt((position2[0] - position1[0]) ** 2 + (position2[1] - position1[1]) ** 2)

    def step(self, action):
        """
        Take a step in the environment.

        Args:
            action (int): The action to take.

        Returns:
            tuple: The reward and game over flag.
        """
        reward = 0

        # move car
        m = self.car.move(action)
        self.distance += m

        # game end
        game_over = False

        # check for collision
        rc = self.car.raytrace_cameras()
        if self.car.is_collision(rc):
            pen = -1
            game_over = True
            return pen, game_over

        checkpoint_captured = self.get_captured_checkpoint(self.car, self.car.nextCheckpoint)
        reward += checkpoint_captured - 1

        if self.car.nextCheckpoint == len(self.checkpoints):
            game_over = True

        return reward, game_over

    def render(self, reward, epsilon):
        """
        Render the environment.

        Args:
            reward (float): The reward.
            epsilon (float): The epsilon value.
        """
        self.screen.blit(self.background_img, (0, 0))

        if self.debugging:
            self.draw_walls()

        self.get_checkpoints()

        # draw car
        self.car.draw()

        if self.debugging:
            self.car.draw_cameras()
            self.car.draw_LiDAR()

        if self.debugging:
            self.screen.blit(
                pygame.font.SysFont('Comic Sans MS', 20).render("Reward: "+str(reward),
                False, (255, 255, 255)), (450, 10)
            )

            self.screen.blit(
                pygame.font.SysFont('Comic Sans MS', 20).render("Randomness: "+str(round(epsilon, 4)),
                False, (255, 255, 255)),(450, 30)
            )

        # update ui and clock
        pygame.display.update()
        self.clock.tick()

    def reset(self):
        """
        Reset the environment.
        """
        self.distance = 0
        self.car.reset()

