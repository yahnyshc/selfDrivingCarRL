
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DataLoader(metaclass=SingletonMeta):
    def __init__(self):
        self.walls = self.load_walls("maps/path1.txt")

    def get_walls(self):
        return self.walls

    @staticmethod
    def load_walls(filename):
        walls = []
        with open(filename) as f:
            next(f)
            for line in f:
                (x1, y1), (x2, y2) = map(lambda x: x.split(","), line.split(" "))
                walls.append((round(float(x1)), round(float(y1)), round(float(x2)), round(float(y2))))
        return walls
