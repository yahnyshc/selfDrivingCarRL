import math
import pygame
from DataLoader import DataLoader
import numpy as np
from shapely.geometry import LineString

# If the car detect distance to the wall is less than 7 percent
# then it is considered as collision
COLLISION_THRESHOLD = 0.07

class Car:

    def __init__(self, screen):
        """
        Initialize the Car object.

        Args:
            screen (pygame.Surface): The screen surface to draw the car on.
        """
        # Initialize the screen surface
        self.screen = screen

        # Load the walls from the data loader
        self.walls = DataLoader().get_walls()

        # Set the initial position of the car to the first wall
        self.x = self.walls[0][0] + 30
        self.y = self.walls[0][1]

        # Set the size of the car
        self.size = (17, 35)

        # Set the initial angle of the car to 180 degrees (facing backward)
        self.angle = 180

        # Set the camera angles of the car
        self.camera_angles = [-90, -60, -30, 0, 30, 60, 90]

        # Define the actions with format (speed, angle_change)
        self.actions = [
            (1, -3),  # Turn left sharply
            (2, -2),  # Turn left
            (3, -1),  # Turn left slightly
            (4, 0),  # Move forward
            (3, 1),  # Turn right slightly
            (2, 2),  # Turn right
            (1, 3)  # Turn right sharply
        ]

        # Initialize the camera distances list
        self.camera_distances = []

        # Set the maximum distance for the camera
        self.MAX_CAMERA_DISTANCE = 60

        # Initialize the next checkpoint counter
        self.next_checkpoint = 1

        # Load the car image
        self.image = pygame.image.load("img/car3.png")

        # Resize the car image to the specified size
        self.image = pygame.transform.scale(self.image, self.size)

    # reset the Car initial position
    def reset(self):
        """
        Reset the car to its initial position and reset the next checkpoint counter.

        This function resets the car's position to the first wall in the list of walls.
        It also sets the angle of the car to 180 degrees and resets the next checkpoint counter to 1.
        """
        # Reset the car's position to the first wall
        self.x = self.walls[0][0] + 30
        self.y = self.walls[0][1]

        # Reset the next checkpoint counter
        self.next_checkpoint = 1

        # Set the angle of the car to 180 degrees
        self.angle = 180

    def get_state(self):
        """
        Get the state of the car which is the list of distances from each camera to the walls or the end point of the camera.

        Returns:
            list: List of distances from each camera to the walls or the end point of the camera.
        """
        # Get the state of the car
        # The state is a list of distances from each camera to the walls or the end point of the camera
        return self.camera_distances

    def move(self, action):
        """
        Move the car forward and turn it in the direction of movement.

        Args:
            action (int): The index of the action to perform.

        Returns:
            float: The distance travelled by the car.
        """
        # Get the speed and angle change for the selected action
        speed, angle_change = self.actions[action]

        # Store the current position
        old_position = (self.x, self.y)

        # Update the position of the car
        self.angle += angle_change
        self.x -= speed * math.sin(math.radians(self.angle))
        self.y -= speed * math.cos(math.radians(self.angle))

        # Calculate and return the distance travelled by the car
        return self.distance_between_points(old_position, (self.x, self.y))

    def checkpoint_captured(self):
        """
        Increment the counter for the next checkpoint to be captured.

        This function is called when a checkpoint is captured by the car. It
        increments the 'next_checkpoint' counter to keep track of the next
        checkpoint to be visited.

        Returns:
            None
        """
        # Increment the counter for the next checkpoint to be captured
        self.next_checkpoint += 1

    def get_centre(self):
        """
        Get the center coordinates of the car.

        Returns:
            tuple: Coordinates of the center of the car.
        """
        # Calculate the x-coordinate of the center
        x_center = self.x + self.size[0] / 2
        # Calculate the y-coordinate of the center
        y_center = self.y + self.size[1] / 2

        # Return the center coordinates
        return x_center, y_center

    # Draw car on the screen under angle
    def draw(self):
        """
        Draw the car on the screen rotated to the specified angle.
        """
        # Rotate the car image
        car = pygame.transform.rotate(self.image, self.angle)

        # Get the center of the car
        car_center = self.get_centre()

        # Get the rectangle of the rotated car
        car_rect = car.get_rect(center=car_center)

        # Blit the rotated car onto the screen
        self.screen.blit(car, car_rect)

    def is_collision(self, raytrace_output):
        """
        Check if there is a collision between the car and the walls.

        Args:
            raytrace_output (list): List of distances from the car to the walls.

        Returns:
            bool: True if there is a collision, False otherwise.
        """
        # Iterate over each distance in the raytrace output
        for i in range(len(raytrace_output)):
            # If the distance is less than a COLLISION_THRESHOLD, there is a collision
            if raytrace_output[i] < COLLISION_THRESHOLD:
                return True
        # If no collision is found, return False
        return False

    def rotate_point(self, origin, point, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle) * (px - ox) + math.sin(angle) * (py - oy)
        qy = oy - math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy

    def rotate_line_around(self, start, end, origin, angle):
        """
        Rotate a line around a point counterclockwise by a given angle.

        Args:
            start (tuple): The starting coordinates of the line.
            end (tuple): The ending coordinates of the line.
            origin (tuple): The origin coordinates of the rotation.
            angle (float): The angle of rotation in degrees.

        Returns:
            tuple: The rotated start and end coordinates of the line.
        """
        # Convert angle to radians
        rad = math.radians(angle)
        # Rotate the start and end coordinates around the origin
        return self.rotate_point(origin, start, rad), self.rotate_point(origin, end, rad)

    def get_cameras(self):
        """
        Get the cameras for the car.

        Yields:
            tuple: Tuple containing the start and end coordinates of each camera.
        """
        # Get the center of the car
        c = self.get_centre()

        # Iterate over each camera angle
        for angle in self.camera_angles:
            # Get the camera end coordinates
            # Rotate the line around the center of the car
            _, (xe, ye) = self.rotate_line_around(c, (c[0], c[1] - self.MAX_CAMERA_DISTANCE), self.get_centre(), angle)

            # Get the car rectangle
            rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

            # Get the camera start coordinates
            # Clip the line with the car rectangle
            _, (xs, ys) = rect.clipline(c, (xe, ye))

            # Yield the camera start and end coordinates
            yield self.rotate_line_around((xs, ys), (xe, ye), self.get_centre(), self.angle)

    def line_intersection(self, p1, p2, p3, p4):
        """
        Calculate the intersection point of two line segments.

        Args:
            p1 (tuple): Coordinates of the first point of the first line segment.
            p2 (tuple): Coordinates of the second point of the first line segment.
            p3 (tuple): Coordinates of the first point of the second line segment.
            p4 (tuple): Coordinates of the second point of the second line segment.

        Returns:
            tuple or None: The coordinates of the intersection point, or None if the lines are parallel or do not intersect.
        """
        # Decompose the points into individual coordinates
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        # Calculate the denominator of the line equations
        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

        # If the denominator is zero, the lines are parallel
        if denom == 0:
            return None

        # Calculate the numerators of the line equations
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom

        # If the numerators are outside the range [0, 1], the lines do not intersect
        if ua < 0 or ua > 1 or ub < 0 or ub > 1:
            return None

        # Calculate the intersection point
        x = x1 + ua * (x2 - x1)
        y = y1 + ua * (y2 - y1)

        return x, y

    def raytrace(self, start, end, camera_s, camera_e):
        """
        Calculate the intersection point between a line segment and a ray.

        Args:
            start (tuple): Coordinates of the start point of the line segment.
            end (tuple): Coordinates of the end point of the line segment.
            camera_s (tuple): Coordinates of the start point of the ray.
            camera_e (tuple): Coordinates of the end point of the ray.

        Returns:
            tuple or None: The intersection point between the line segment and the ray,
                           or None if the lines are parallel or do not intersect.
        """
        # Calculate the intersection point between the line segment and the ray
        i = self.line_intersection(start, end, camera_s, camera_e)

        # If the lines intersect, return the intersection point
        if i:
            return i

        # Otherwise, return None
        return None

    def distance_between_points(self, p1, p2):
        """
        Calculate the Euclidean distance between two points.

        Args:
            p1 (tuple): Coordinates of the first point.
            p2 (tuple): Coordinates of the second point.

        Returns:
            float: The distance between p1 and p2.
        """
        # Calculate the Euclidean distance between p1 and p2
        # using the formula: sqrt((x2 - x1)^2 + (y2 - y1)^2)
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    def raytrace_cameras(self):
        """
        Compute the distances from each camera to the walls or the end point of the camera.

        This function iterates over each camera, computes the distances to the walls,
        and returns a list of distances. The distances are computed as a percentage of
        the maximum distance.

        Returns:
            list: List of distances from each camera to the walls or the end point of the camera.
        """
        # List to store the distances for each camera
        output = []
        # Iterate over each camera
        for camera_s, camera_e in self.get_cameras():
            flag = False
            # Compute the maximum distance to the camera
            max_distance = self.MAX_CAMERA_DISTANCE - self.distance_between_points(self.get_centre(), camera_s)
            # Iterate over each wall
            for x1, y1, x2, y2 in self.walls:
                start, end = (x1, y1), (x2, y2)
                # Compute the distance to the wall
                rt = self.raytrace(start, end, camera_s, camera_e)
                if rt:
                    # Compute the distance as a percentage of the maximum distance
                    d = self.distance_between_points(camera_s, rt) / max_distance
                    # Append the distance to the output list
                    output.append(min(round(d, 2), 1))
                    flag = True
                    break
            if not flag:
                # Compute the distance to the end point of the camera
                d = self.distance_between_points(camera_s, camera_e) / max_distance
                # Append the distance to the output list
                output.append(min(round(d, 2), 1))
        # Store the distances in the Car object
        self.camera_distances = output
        # Return the distances
        return output

    def percentage_to_color(self, distance):
        """
        Compute color based on percentage.

        This function takes a distance and returns a tuple of RGB values. The
        color is computed based on the cosine and sine of distance multiplied
        by pi/200. The result is a color that oscillates between red and blue
        as distance increases.

        :param distance: The distance to compute the color for.
        :type distance: int
        :return: A tuple of RGB values.
        :rtype: tuple
        """
        # Compute blue and green values
        distance = max(1, 100 - distance)
        green = int(255 * math.sqrt(math.cos(distance * math.pi / 200)))
        blue = 0

        # Compute red value
        red = int(255 * math.sqrt(math.sin(distance * math.pi / 200)))

        # Return the RGB values
        return (red, green, blue)

    def draw_cameras(self):
        """
        Draws the cameras on the screen.

        This function iterates over each camera and computes the distances to the walls.
        It then draws the lines between the cameras and the walls on the screen.
        """
        for camera_s, camera_e in self.get_cameras():
            flag = False
            # Compute the maximum distance to the camera
            max_distance = self.MAX_CAMERA_DISTANCE - self.distance_between_points(self.get_centre(), camera_s)
            # Iterate over each wall
            for x1, y1, x2, y2 in self.walls:
                start, end = (x1, y1), (x2, y2)
                # Compute the distance to the wall
                rt = self.raytrace(start, end, camera_s, camera_e)
                if rt:
                    # Compute the distance as a percentage of the maximum distance
                    d = int((self.distance_between_points(camera_s, rt) / max_distance) * 100)
                    # Draw the line between the camera and the wall
                    pygame.draw.line(self.screen, self.percentage_to_color(d), camera_s, rt, 1)
                    flag = True
                    break
            if not flag:
                # Compute the distance to the end point of the camera
                d = int((self.distance_between_points(camera_s, camera_e) / max_distance) * 100)
                # Draw the line between the camera and the end point
                pygame.draw.line(self.screen, self.percentage_to_color(d), camera_s, camera_e, 1)

    def draw_LiDAR(self):
        """
        Draws the LiDAR detection points on the screen.

        This function iterates over each camera and computes the LiDAR detection points.
        It then draws the lines between the detection points on the screen.
        """
        # List to store the detection points for each camera
        camera_points = []
        # List to store the distances of the cameras
        distances = []
        # Number of LiDAR levels
        n = 7

        def getPoints(camera_s, camera_e):
            """
            Computes the LiDAR detection points between two camera points.

            Args:
                camera_s (tuple): Coordinates of the starting point.
                camera_e (tuple): Coordinates of the ending point.

            Returns:
                list: List of detection points.
            """
            line = LineString(([camera_s, camera_e]))
            # Compute the distances between the starting and ending points
            distances = np.linspace(0, line.length, n)
            # Interpolate the points between the starting and ending points
            points = [line.interpolate(distance) for distance in distances]
            # Convert the points to their coordinates
            points = [(p.x, p.y) for p in points]
            return points

        # Iterate over each camera
        for i in range(1, n):
            j = 0
            for camera_s, camera_e in self.get_cameras():
                flag = False
                max_distance = self.MAX_CAMERA_DISTANCE - self.distance_between_points(self.get_centre(), camera_s)
                # Iterate over each wall
                for x1, y1, x2, y2 in self.walls:
                    start, end = (x1, y1), (x2, y2)
                    rt = self.raytrace(start, end, camera_s, camera_e)
                    if rt:
                        # Compute the detection points and distances
                        camera_points.append(getPoints(camera_s, rt))
                        distances.append(self.distance_between_points(camera_s, rt) / max_distance)
                        flag = True
                        break
                if not flag:
                    # Compute the distance and detection points for the camera points
                    distances.append(self.distance_between_points(camera_s, camera_e) / max_distance)
                    camera_points.append(getPoints(camera_s, camera_e))

                if j >= 1:
                    avg_distance = (distances[j] + distances[j - 1]) / 2
                    # Compute the average color based on the distance
                    avg_distance = int(avg_distance * 100)
                    avg_color = self.percentage_to_color(avg_distance)
                    # Draw the line between the detection points
                    pygame.draw.line(
                        self.screen, avg_color, camera_points[j][i], camera_points[j - 1][i], 1)

                j += 1
