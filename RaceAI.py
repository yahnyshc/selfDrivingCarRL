import pygame
from Car import Car
from DataLoader import DataLoader
from Checkpoint import Checkpoint
import math

class RaceAI:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pygame window")
        self.screen = pygame.display.set_mode((1000, 700))
        self.walls = DataLoader().get_walls()
        self.checkpoints = self.get_checkpoints()
        self.calculate_checkpoint_percentages()
        self.track_length = 0
        self.iteration = 0
        self.clock = pygame.time.Clock()
        self.car = Car(self.screen)
        self.distance = 0
        self.reset()

    def draw_walls(self):
        for x1, y1, x2, y2 in self.walls:
            pygame.draw.line(self.screen, (0, 0, 0), (x1, y1), (x2, y2), 1)

    def get_checkpoints(self):
        checkpoints = []
        for i in range(0, 20):
            if i >= 10:
                i = i + 10
            x1, y1, x2, y2 = self.walls[i]
            x3, y3, x4, y4 = self.walls[i + 10]
            c = Checkpoint(((x1 + x3)/2, (y1 + y3)/2))
            checkpoints.append(c)
            c.draw(self.screen)
        return checkpoints

    def calculate_checkpoint_percentages(self):
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
        self.track_length = self.checkpoints[-1].accumulated_distance

        # Calculate reward value for each checkpoint
        for i in range(1, len(self.checkpoints)):
            self.checkpoints[i].reward_value = (
                self.checkpoints[i].accumulated_distance / self.track_length
            ) - self.checkpoints[i - 1].accumulated_reward
            self.checkpoints[i].accumulated_reward = (
                self.checkpoints[i - 1].accumulated_reward + self.checkpoints[i].reward_value
            )

    def get_complete_perc(self, car, cur_checkpoint_index):
        # Already all checkpoints captured
        if cur_checkpoint_index >= len(self.checkpoints):
            return 1

        # Calculate distance to next checkpoint
        check_point_distance = self.vector2_distance((car.x, car.y), self.checkpoints[cur_checkpoint_index].position)

        # Check if checkpoint can be captured
        if check_point_distance <= self.checkpoints[cur_checkpoint_index].capture_radius:
            return self.get_complete_perc(car, cur_checkpoint_index + 1)  # Recursively check next checkpoint
        else:
            # Return accumulated reward of last checkpoint + reward of distance to next checkpoint
            return self.checkpoints[cur_checkpoint_index - 1].accumulated_reward + self.checkpoints[cur_checkpoint_index].get_reward_value(check_point_distance)

    @staticmethod
    def vector2_distance(position1, position2):
        return math.sqrt((position2[0] - position1[0]) ** 2 + (position2[1] - position1[1]) ** 2)

    def play_step(self, action):
        self.iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        reward = 0.0

        # move car
        m = self.car.move(action)
        self.distance += m

        # game end
        gameOver = False
        # check for collision
        rc = self.car.raytrace_camera()
        if self.car.is_collision(rc):
            gameOver = True
            reward = -100
            return reward, gameOver, self.distance

        reward += self.get_complete_perc(self.car, 1) * 500
        print("reward " + str(reward))

        print("rc: " + str(rc))
        avg_rc = sum(rc)/len(rc)
        if (min(rc) > 0.7):
            print("positive")
            reward += min(rc) * 10
        else:
            print("negative: "+ str(min(rc)))
            reward -= (1-min(rc)) * 30

        # # Additional reward for smooth turning
        # if abs(action) < 7:
        #     reward += 3  # Additional reward for smooth turns

        print("reward " + str(reward))
        # draw car
        self.car.draw()

        self.get_checkpoints()

        self.screen.blit(pygame.font.SysFont('Comic Sans MS', 30).render(str(reward), False, (0, 0, 0)), (0,0))

        # update ui and clock
        pygame.display.update()
        self.clock.tick(60)

        #print(reward)

        return reward, gameOver, self.distance

    def reset(self):
        self.iteration = 0
        self.distance = 0
        self.car.reset()