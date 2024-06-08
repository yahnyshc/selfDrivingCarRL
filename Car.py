import math
import pygame
from DataLoader import DataLoader

class Car:

    def __init__(self, screen):
        self.screen = screen
        self.walls = DataLoader().get_walls()
        self.x = self.walls[0][0] + 18
        self.y = self.walls[0][1]
        self.size = (15, 30)
        self.angle = 180
        self.camera_angles = [-90, -45, 0, 45, 90]
        self.speed = 2
        self.max_turning = 5
        self.camera_distances = []
        self.MAX_CAMERA_DISTANCE = 60
        self.nextCheckpoint = 1

        # Load car image
        self.image = pygame.image.load("img/car.png")
        # Make car smaller proportionally to the image
        self.image = pygame.transform.scale(self.image, self.size)
        self.raytrace_camera()

    # reset the Car initial state
    def reset(self):
        self.x = self.walls[0][0] + 18
        self.y = self.walls[0][1]
        self.nextCheckpoint = 1
        self.angle = 180

    # Move the car forward and turn it in the direction of movement
    # action is array of size 11 with the distribution of actions
    def move(self, action):
        speed, angle = 0, 0
        if action[0]:
            speed, angle = 0, -1
        elif action[1]:
            speed, angle = 1, -1
        elif action[2]:
            speed, angle = 1, 0
        elif action[3]:
            speed, angle = 1, 1
        elif action[4]:
            speed, angle = 0, 1
        # find index of maximum element in action array
        self.speed = speed
        self.angle += angle
        (old_x, old_y) = (self.x, self.y)
        self.x -= self.speed * math.sin(math.radians(self.angle))
        self.y -= self.speed * math.cos(math.radians(self.angle))
        return self.distance((old_x, old_y), (self.x, self.y))


    def CheckpointCaptured(self):
        self.nextCheckpoint += 1

    # get center of the car coordinates
    def get_centre(self):
        return (self.x+self.size[0]/2, self.y+self.size[1]/2)

    # Draw car on the screen under angle
    def draw(self):
        car1 = pygame.transform.rotate(self.image, self.angle)
        car_rect = car1.get_rect(center = self.get_centre())
        self.screen.blit(car1, car_rect)

    # detect whether the car crosses checkpoint
    def crosses_checkpoint(self, checkpoint):
        # get car rectangle using x, y, angle and size
        car_rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

        start, end = checkpoint
        start, end = self.rotate_line(start, end, self.angle)
        if car_rect.clipline(start, end):
            return True
        return False

    # rotate the line by angle inverse to given
    def rotate_line(self, start, end, angle):
        angle = (angle + 180) % 360
        rad = math.radians(angle)
        # rotate the line around car's self.x and self.y
        start = (start[0] - self.x, start[1] - self.y)
        end = (end[0] - self.x, end[1] - self.y)
        start = (start[0] * math.cos(rad) - start[1] * math.sin(rad), start[0] * math.sin(rad) + start[1] * math.cos(rad))
        end = (end[0] * math.cos(rad) - end[1] * math.sin(rad), end[0] * math.sin(rad) + end[1] * math.cos(rad))
        start = (start[0] + self.x, start[1] + self.y)
        end = (end[0] + self.x, end[1] + self.y)
        return start, end

    # detect whether the car collides the wall segment
    def is_collision(self, raytrace_output):
        for i in range(len(raytrace_output)):
            # if i == 0 or i == len(raytrace_output) - 1:
            #     dist = 2
            # elif i == 1 or i == len(raytrace_output) - 2:
            #     dist = 2
            # else:
            #     dist = 2
            if raytrace_output[i] < 2:
                return True
        return False


    def rotate(self, origin, point, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle) * (px - ox) + math.sin(angle) * (py - oy)
        qy = oy - math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy

    # rotate line around the point counterclockwise
    def rotate_line_around(self, start, end, origin, angle):
        rad = math.radians(angle)
        return self.rotate(origin, start, rad), self.rotate(origin, end, rad)

    # function to get an array of cameras starting at edges of the car and ending under 90, 45 and 0 degrees
    def get_cameras(self):
        c = self.get_centre()
        for angle in self.camera_angles:
            # get camera end coordinates
            _, (xe, ye) = self.rotate_line_around(c, (c[0], c[1] - self.MAX_CAMERA_DISTANCE), self.get_centre(), angle)
            # form car rectangle
            rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
            # get camera start coordinates
            _, (xs, ys) = rect.clipline(c, (xe, ye))
            yield (xs, ys), (xe, ye)

    # intersection between line(p1, p2) and line(p3, p4)
    def line_intersection(self, p1, p2, p3, p4):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if denom == 0:  # parallel
            return None
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
        if ua < 0 or ua > 1:  # out of range
            return None
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
        if ub < 0 or ub > 1:  # out of range
            return None
        x = x1 + ua * (x2 - x1)
        y = y1 + ua * (y2 - y1)
        return x, y

    # raytrace
    def raytrace(self, start, end, camera_s, camera_e):
        i = self.line_intersection(start, end, camera_s, camera_e)
        if i:
            return i
        return None

    def distance(self, p1, p2):
        # distance between p1 and p2
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    # raytrace vector to find the find distances to walls
    def raytrace_camera(self):
        output = []
        for (cx1, cy1), (cx2, cy2) in self.get_cameras():
            camera_s, camera_e = self.rotate_line_around((cx1, cy1), (cx2, cy2), self.get_centre(), self.angle)
            f = False
            for x1, y1, x2, y2 in self.walls:
                start, end = (x1, y1), (x2, y2)
                rt = self.raytrace(start, end, camera_s, camera_e)
                if rt:
                    pygame.draw.line(self.screen, (0, 255, 0), camera_s, rt, 1)
                    d = self.distance(camera_s, rt)
                    output.append(d)
                    f = True
                    break
            if not f:
                pygame.draw.line(self.screen, (0, 255, 0), camera_s, camera_e, 1)
                d = self.distance(camera_s, camera_e)
                output.append(d)
        self.camera_distances = output
        return output



