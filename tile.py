"""Import the tile class and needed functions."""
from misc import Status, HEIGHT
from math import inf, sqrt

from OpenGL.GL import glBegin, GL_QUADS, glColor, glVertex3f, glEnd, glVertex2f, GL_TRIANGLES


def average_colors(col1, col2):
    """Averages two colors in a sane way."""
    return (
        sqrt((pow(col1[0], 2) + pow(col2[0], 2)) / 2),
        sqrt((pow(col1[1], 2) + pow(col2[1], 2)) / 2),
        sqrt((pow(col1[2], 2) + pow(col2[2], 2)) / 2),
    )


class Tile:
    """A basic tile, with a (x, y) position and a cost."""

    def __init__(self, x, y, cost):
        """Initialize the tile."""
        self.x = x
        self.y = y
        if cost == inf:
            self.status = Status.NONTRAVERSABLE
        else:
            self.status = Status.UNVISITED
        self.cost = cost
        self.distance = inf
        self.prev = None
        self.start = False
        self.end = False
        self.prog = None

    def color(self):
        """Return the color of the tile."""
        if self.status == Status.NONTRAVERSABLE:
            return (self.cost / HEIGHT, 0.45, 1)
        elif self.end:
            return (0, 1, 0)
        elif self.start:
            return (1, 0, 0)
        elif self.prog:
            return (sqrt(1 - pow(self.prog, 2)), self.prog, 0)
        # elif self.status == Status.VISITED:
        # return (self.cost / HEIGHT, 1, 0.6)  # nice toxic waste effect
        else:
            return (1, self.cost / HEIGHT, 0.2)

    def reset(self):
        """Une fonction qui réinitialise la tile."""
        if self.status == Status.VISITED:
            self.status = Status.UNVISITED

        self.distance = inf
        self.prev = None
        self.start = False
        self.end = False
        self.prog = None

    def draw(self, size, threshold):
        """Draw the tile in OpenGL."""
        w = self.x * size * 2
        h = self.y * size * 2
        elevation = self.cost if self.cost != inf else threshold
        glBegin(GL_QUADS)
        glColor(*self.color())

        glVertex3f(w, elevation, h)
        glVertex3f(w + size, elevation, h)
        glVertex3f(w + size, elevation, h + size)
        glVertex3f(w, elevation, h + size)

        glEnd()

    def draw_sel(self, size):
        """Draw the tile in orthogonal mode, for selection."""
        glBegin(GL_QUADS)
        glColor(*self.color())
        glVertex2f(self.x * size, self.y * size)
        glVertex2f(self.x * size + size, self.y * size)
        glVertex2f(self.x * size + size, self.y * size + size)
        glVertex2f(self.x * size, self.y * size + size)
        glEnd()

    def bridge_color(self, case):
        """Color a bridge between two cases."""
        return average_colors(self.color(), case.color())

    def bridge_color_diagonal(self, case, opposite):
        """Color a diagonal bridge between two cases."""
        if self.status == Status.NONTRAVERSABLE and case.status == Status.NONTRAVERSABLE:
            return opposite[0].bridge_color(opposite[1])
        else:
            return average_colors(case.color(), self.color())

    def draw_bridge(self, cases, size):
        """Draw a bridge between a case and all its neighbors."""
        neighbors = dict(((case.x - self.x, case.y - self.y), case) for case in cases)
        w = self.x * size * 2
        h = self.y * size * 2
        for diff, case in neighbors.items():
            if diff == (1, 0):
                glBegin(GL_QUADS)
                glColor(*self.bridge_color(case))
                glVertex3f(w + size, self.cost, h)
                glVertex3f(w + size, self.cost, h + size)
                glVertex3f(w + size * 2, case.cost, h + size)
                glVertex3f(w + size * 2, case.cost, h)
                glEnd()
            elif diff == (0, 1):
                glBegin(GL_QUADS)
                glColor(*self.bridge_color(case))
                glVertex3f(w + size, self.cost, h + size)
                glVertex3f(w, self.cost, h + size)
                glVertex3f(w, case.cost, h + size * 2)
                glVertex3f(w + size, case.cost, h + size * 2)
                glEnd()
            elif diff == (-1, -1):
                # 0-1, -10
                glBegin(GL_TRIANGLES)
                glColor(
                    *self.bridge_color_diagonal(
                        case, (neighbors[(0, -1)], neighbors[(-1, 0)])
                    )
                )
                glVertex3f(w, self.cost, h)
                glVertex3f(w - size, neighbors[(-1, 0)].cost, h)
                glVertex3f(w, neighbors[(0, -1)].cost, h - size)
                glEnd()
            elif diff == (1, 1):
                # 01, 10
                glBegin(GL_TRIANGLES)
                glColor(
                    *self.bridge_color_diagonal(
                        case, (neighbors[(0, 1)], neighbors[(1, 0)])
                    )
                )
                glVertex3f(w + size, self.cost, h + size)
                glVertex3f(w + size * 2, neighbors[(1, 0)].cost, h + size)
                glVertex3f(w + size, neighbors[(0, 1)].cost, h + size * 2)
                glEnd()

    def starting(self):
        """Set the tile as the starting tile."""
        self.distance = 0
        self.start = True

    def ending(self):
        """Set the tile as the ending tile."""
        self.end = True

    def travel(self, max_dist):
        """Travel on the tile."""
        self.prog = self.distance / max_dist

    def length(self, tile):
        """Return the length of the straight line between two tiles."""
        distance_horiz = pow(self.x - tile.x, 2) + pow(self.y - tile.y, 2)
        distance_diag = sqrt(distance_horiz + pow(self.cost - tile.cost, 2))
        return distance_diag

    def __repr__(self):
        """Return the string representation of the tile."""
        return f"({self.x},{self.y}): {self.cost}"

    def __lt__(self, other):
        """Return lesser-than comparisons between two tiles."""
        return self.distance < other.distance

    def __gt__(self, other):
        """Returns greater-than comparisons between two tiles."""
        return self.distance > other.distance
