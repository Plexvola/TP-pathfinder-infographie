"""Contains the Grid class and needed functions."""
from tile import Tile
from misc import Status, HEIGHT
from math import inf
from random import randrange
from itertools import chain, product
from time import sleep


class Grid:
    """Grid made of tiles."""

    def __init__(self, size, width, height, threshold, worm):
        """Create a grid composed of tiles.

        Each tile measures size, width and height are in number of tiles.
        """
        self.size = size
        self.width = width
        self.height = height
        self.worm = worm
        self.start = None
        self.finish = None

        self.zoom = 12 * size * max(width, height)
        self.theta = 0
        self.phi = 90

        self.perspective = False
        self.threshold = HEIGHT * (threshold / 100)

    def generate(self, smooth_level=2):
        """Generate each tile of the grid. Tiles can be smoothed."""
        self.tiles = [[[] for _ in range(self.height + 2)] for _ in range(self.width + 2)]
        self.tiles[0] = [Tile(0, x, inf) for x in range(self.height + 2)]
        self.tiles[self.width + 1] = [Tile(self.width + 1, x, inf) for x in range(self.height + 2)]

        for line in range(1, self.width + 1):
            self.tiles[line][0] = Tile(line, 0, inf)
            self.tiles[line][self.height + 1] = Tile(line, self.height + 1, inf)
            for column in range(1, self.height + 1):
                self.tiles[line][column] = Tile(line, column, randrange(HEIGHT + 1))

        weights = [[[] for _ in range(self.height + 2)] for _ in range(self.width + 2)]

        if smooth_level:
            for tile in chain(*self.tiles):
                if tile.status != Status.NONTRAVERSABLE:
                    weights[tile.x][tile.y] = self.smooth(tile, smooth_level)

            for tile in chain(*self.tiles):
                if tile.status != Status.NONTRAVERSABLE:
                    tile.cost = weights[tile.x][tile.y]

        for tile in chain(*self.tiles):
            if tile.cost < self.threshold:
                tile.status = Status.NONTRAVERSABLE

    def smooth(self, tile, smooth_level):
        """Flattens the tile to the level of its neighbors."""
        n = [
            c.cost
            for c in self.neighbors(tile, smooth_level)
            if c.status != Status.NONTRAVERSABLE
        ]
        return sorted(n)[len(n) // 2] if n else tile.cost

    def reset(self):
        """Reset each grid's tile, without changing its cost."""
        self.start = None
        self.finish = None

        self.perspective = False

        for col in self.tiles:
            for tile in col:
                tile.reset()

    def smallest(self):
        """Find the smallest unvisited tile."""
        return min(filter(lambda c: c.status == Status.UNVISITED, chain(*self.tiles)))

    def astar(self):
        """Find the smallest unvisited tile (A* variation)."""
        return min(
            filter(lambda c: c.status == Status.UNVISITED, chain(*self.tiles)),
            key=lambda c: c.distance + c.length(self.finish),
        )

    def neighbors(self, tile, radius=1):
        """Find all traversable neighbors."""
        adjacents = filter(
            lambda c: 0 < c[0] <= self.width
            and 0 < c[1] <= self.height
            and c != (tile.x, tile.y),
            product(
                range(tile.x - radius, tile.x + radius + 1),
                range(tile.y - radius, tile.y + radius + 1),
            ),
        )

        tiles_adj = [self.tiles[x][y] for x, y in adjacents]

        return tiles_adj

    def dijkstra(self, smallest, time=0.01):
        """Fills each tile's attributes according to Dijkstra's algorithm."""
        while smallest().distance != inf and self.finish.status != Status.VISITED:
            current = smallest()
            for tile in self.neighbors(current):
                if tile.status == Status.UNVISITED:
                    dis = current.distance + current.length(tile)
                    if dis < tile.distance:
                        tile.distance = dis
                        tile.prev = current

            current.status = Status.VISITED
            sleep(time)

    def breadth_first(self, tile, time=0.01):
        """Fills each tile's attributes according to a breadth-first algorithm."""
        queue = [tile]
        for current in queue:
            if current == self.finish:
                return
            elif current.status == Status.UNVISITED:
                for n in self.neighbors(current):
                    if n.status == Status.UNVISITED:
                        n.prev = current
                        n.distance = current.distance + current.length(n)
                        queue.append(n)
                current.status = Status.VISITED
            sleep(time)

    def path(self):
        """Return a list containing the path from the start tile to the end tile."""
        tile = self.finish
        tiles_path = []
        while tile is not None:
            tiles_path.append(tile)
            tile = tile.prev

        return list(reversed(tiles_path))

    def draw(self):
        """Draw the grid."""
        for line in range(1, self.width + 1):
            for column in range(1, self.height + 1):
                if self.perspective:
                    self.tiles[line][column].draw(self.size, self.threshold)
                    self.tiles[line][column].draw_bridge(
                        self.neighbors(self.tiles[line][column]), self.size
                    )
                else:
                    self.tiles[line][column].draw_sel(self.size)

    def drawpath(self, algorithm):
        """Draws the path on the grid, after initalization of the start and end tile."""
        if algorithm == "astar":
            self.dijkstra(self.astar, 0)
        elif algorithm == "dijkstra":
            self.dijkstra(self.smallest, 0)
        elif algorithm == "breadth":
            self.breadth_first(self.start, 0)
        path = self.path()

        self.worm.follow_bezier(path)

    def clic_tile(self, x, y):
        """Click on a tile."""
        x //= self.size
        y //= self.size
        if (
            not self.perspective
            and x <= self.width
            and y <= self.height
            and self.tiles[x][y].cost != inf
        ):
            if not self.start:
                if self.tiles[x][y].status != Status.NONTRAVERSABLE:
                    self.start = self.tiles[x][y]
                    self.start.starting()
            elif not self.finish:
                if self.tiles[x][y].status != Status.NONTRAVERSABLE:
                    self.finish = self.tiles[x][y]
                    self.finish.ending()
