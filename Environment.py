import pygame
from Car import Car
from DataLoader import DataLoader
from Checkpoint import Checkpoint
import math

WIDTH = 1000
HEIGHT = 700

class Environment:

    def __init__(self, debugging=False):
        """
        Initialize the environment.

        Args:
            debugging (bool): Whether to enable debugging mode.
        """
        pygame.init()
        pygame.display.set_caption("Self driving car")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.background_img = pygame.image.load("img/path1.png")
        self.debugging = debugging
        self.walls = DataLoader().get_walls()
        self.checkpoints = self.get_checkpoints()
        self.calculate_checkpoint_percentages()
        self.clock = pygame.time.Clock()
        self.car = Car(self.screen)
        self.distance = 0
        self.steering_angle = 0
        self.steering_wheel = pygame.image.load("img/wheel.png")
        # Resize the car image to the specified size
        self.steering_wheel = pygame.transform.scale(self.steering_wheel, (50, 50))
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
                if i != off-1:
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
            return 0

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

    def get_completion_percentage(self, checkpoint):
        """
        Calculate the completion percentage of the track.

        Returns:
            float: The completion percentage.
        """
        return (self.checkpoints[checkpoint - 1].accumulated_reward +
                self.checkpoints[checkpoint].get_reward_value(checkpoint))

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

        checkpoint_captured = self.get_captured_checkpoint(self.car, self.car.next_checkpoint)
        reward += checkpoint_captured - 1

        if checkpoint_captured == 0:
            game_over = True

        return reward, game_over

    def render(self, action, reward, epsilon):
        """
        Render the environment.

        Args:
            action (float): The action taken.
            reward (float): The reward.
            epsilon (float): The epsilon value.
        """
        self.screen.blit(self.background_img, (0, 0))

        # if self.debugging:
        #     self.draw_walls()

        self.get_checkpoints()

        # draw the sensors
        if self.debugging:
            self.car.draw_cameras()
            self.car.draw_LiDAR()

        # draw car
        self.car.draw()

        if self.debugging:
            self.screen.blit(
                pygame.font.SysFont('Comic Sans MS', 15).render("Reward: "+str(reward),
                False, (255, 255, 255)), (WIDTH/2-60, 10)
            )

            self.screen.blit(
                pygame.font.SysFont('Comic Sans MS', 15).render("Randomness: "+str(round(epsilon, 4)),
                False, (255, 255, 255)),(WIDTH/2-60, 30)
            )

        try:
            completion = round(self.get_completion_percentage(self.car.next_checkpoint), 2)
            self.screen.blit(
            pygame.font.SysFont('Comic Sans MS', 15).
                render(str(round(completion*100, 2)) + "%",
                False, (255, 255, 255)),(WIDTH/2-10, HEIGHT-30)
            )

            pygame.draw.rect(
                self.screen,
                self.car.percentage_to_color(int(completion*100)), pygame.Rect(0, 695, 1000*completion, 5)
            )
        except:
            pass

        # rotate car steering wheel and print on the screen
        angle = self.car.actions[action][1] * 2
        resistance = -int(self.steering_angle / 30)
        if resistance == 0:
            if self.steering_angle < 0:
                resistance = 1
            elif self.steering_angle > 0:
                resistance = -1
        self.steering_angle += (angle + resistance)
        wheel = pygame.transform.rotate(self.steering_wheel, self.steering_angle)

        wheel_rect = wheel.get_rect(center=(WIDTH-50, 50))
        self.screen.blit(wheel, wheel_rect)

        # update ui and clock
        pygame.display.update()
        self.clock.tick()

    def reset(self):
        """
        Reset the environment.
        """
        self.distance = 0
        self.steering_angle = 0
        self.car.reset()

