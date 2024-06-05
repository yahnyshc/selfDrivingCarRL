from Car import Car
import pygame
from Car import Car
from DataLoader import DataLoader

#will start the simulation
class Race:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pygame window")
        self.screen = pygame.display.set_mode((1000, 700))
        self.walls = DataLoader().get_walls()
        self.iteration = 0
        self.clock = pygame.time.Clock()
        self.car = Car(self.screen)

    def draw_walls(self):
        for x1, y1, x2, y2 in self.walls:
            pygame.draw.line(self.screen, (0, 0, 0), (x1, y1), (x2, y2), 1)

    def run(self):
        while True:
            self.screen.fill((255, 255, 255))
            self.draw_walls()
            print(self.car.is_collision(self.car.raytrace_camera()))
            self.car.draw()



            pygame.display.update()
            self.clock.tick(60)

game = Race()
game.run()