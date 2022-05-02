"""Pathfinder d'un point A à un point B en OpenGL."""
import sys
import threading
from enum import Enum
from itertools import chain, product
from math import cos, inf, pi, pow, sin, sqrt
from random import randrange
from time import sleep

from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST,
                       GL_MODELVIEW, GL_PROJECTION, GL_QUADS, GL_TRIANGLES,
                       glBegin, glClear, glClearColor, glColor3f, glDisable,
                       glEnable, glEnd, glLoadIdentity, glMatrixMode, glOrtho,
                       glPopMatrix, glPushMatrix, glRotatef, glTranslatef,
                       glVertex2f, glVertex3f, glViewport)
from OpenGL.GLU import (GLU_SMOOTH, gluLookAt, gluNewQuadric, gluPerspective,
                        gluQuadricDrawStyle, gluSphere)
from OpenGL.GLUT import (GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGBA,
                         GLUT_WINDOW_HEIGHT, GLUT_WINDOW_WIDTH,
                         glutCreateWindow, glutDestroyWindow, glutDisplayFunc,
                         glutGet, glutGetWindow, glutIdleFunc, glutInit,
                         glutInitDisplayMode, glutKeyboardFunc, glutMainLoop,
                         glutMouseFunc, glutPostRedisplay, glutReshapeFunc,
                         glutReshapeWindow, glutSwapBuffers)


class Status(Enum):
    """Le statut possible de chaque case."""

    VISITED = 0
    UNVISITED = 1
    NONTRAVERSABLE = 2


class Worm:
    """A little worm to travel the earth."""

    def __init__(self, x, y, z, size):
        """Initialize the worm."""
        self.x = x
        self.y = y
        self.z = z
        self.size = size
        self.quadric = gluNewQuadric()
        gluQuadricDrawStyle(self.quadric, GLU_SMOOTH)

    def draw(self):
        """Draws the worm."""
        glColor3f(1, 1, 0)
        glTranslatef(-self.x, -self.y, -self.z)
        gluSphere(self.quadric, 1, 20, 16)
        glTranslatef(self.x, self.y, self.z)


class Case:
    """Case unique, avec un poids et une position."""

    def __init__(self, x, y, poids):
        """Initialise la case."""
        self.x = x
        self.y = y
        if poids == inf:
            self.status = Status.NONTRAVERSABLE
        else:
            self.status = Status.UNVISITED
        self.poids = poids
        self.distance = inf
        self.prev = None
        self.start = False
        self.end = False
        self.trav = None

    def color(self):
        """Une fonction renvoyant la couleur de chaque case."""
        if self.status == Status.NONTRAVERSABLE:
            return (0.2, 0.2, 0.2)
        elif self.end:
            return (0, 1, 0)
        elif self.start:
            return (1, 0, 0)
        elif self.trav:
            return (1 - self.trav, self.trav, 0)
        else:
            return (1 / 128 * self.poids, 0.85, 1)

    def reset(self):
        """Une fonction qui réinitialise la case."""
        if self.poids == inf:
            self.status = Status.NONTRAVERSABLE
        else:
            self.status = Status.UNVISITED

        self.distance = inf
        self.prev = None
        self.start = False
        self.end = False
        self.trav = None

    def draw(self, size):
        """Affiche la case à l'écran."""
        w = self.x * size * 2
        h = self.y * size * 2
        elevation = self.poids
        glPushMatrix()
        glBegin(GL_QUADS)
        glColor3f(*self.color())

        # face du haut
        glVertex3f(w, elevation, h)
        glVertex3f(w + size, elevation, h)
        glVertex3f(w + size, elevation, h + size)
        glVertex3f(w, elevation, h + size)

        glEnd()
        glPopMatrix()

    def draw_sel(self, size):
        """Affiche la case durant la sélection non-perspective."""
        glPushMatrix()
        glBegin(GL_QUADS)
        glColor3f(*self.color())
        glVertex2f(self.x * size, self.y * size)
        glVertex2f(self.x * size + size, self.y * size)
        glVertex2f(self.x * size + size, self.y * size + size)
        glVertex2f(self.x * size, self.y * size + size)
        glEnd()
        glPopMatrix()

    def bridge_color(self, case):
        """Color a bridge between two cases."""
        if self.start or self.end or self.trav:
            if case.start or case.end or case.trav:
                return ((n + m) / 2 for n, m in zip(self.color(), case.color()))
            else:
                return case.color()

        else:
            if case.start or case.end or case.trav:
                return self.color()
            else:
                return ((n + m) / 2 for n, m in zip(self.color(), case.color()))

    def bridge_color_diagonal(self, case, opposite):
        """Color a diagonal bridge between two cases."""
        if self.start or self.end or self.trav:
            if case.start or case.end or case.trav:
                return ((n + m) / 2 for n, m in zip(self.color(), case.color()))
            else:
                return opposite[0].bridge_color(opposite[1])
        else:
            return opposite[0].bridge_color(opposite[1])

    def draw_bridge(self, cases, size):
        """Draw a bridge between a case and all its neighbors."""
        neighbors = dict(((case.x - self.x, case.y - self.y), case) for case in cases)
        w = self.x * size * 2
        h = self.y * size * 2
        for diff, case in neighbors.items():
            if diff == (1, 0):
                glBegin(GL_QUADS)
                glColor3f(*self.bridge_color(case))
                glVertex3f(w + size, self.poids, h)
                glVertex3f(w + size, self.poids, h + size)
                glVertex3f(w + size * 2, case.poids, h + size)
                glVertex3f(w + size * 2, case.poids, h)
                glEnd()
            elif diff == (0, 1):
                glBegin(GL_QUADS)
                glColor3f(*self.bridge_color(case))
                glVertex3f(w + size, self.poids, h + size)
                glVertex3f(w, self.poids, h + size)
                glVertex3f(w, case.poids, h + size * 2)
                glVertex3f(w + size, case.poids, h + size * 2)
                glEnd()
            elif diff == (-1, -1):
                # 0-1, -10
                glBegin(GL_TRIANGLES)
                glColor3f(
                    *self.bridge_color_diagonal(
                        case, (neighbors[(0, -1)], neighbors[(-1, 0)])
                    )
                )
                glVertex3f(w, self.poids, h)
                glVertex3f(w - size, neighbors[(-1, 0)].poids, h)
                glVertex3f(w, neighbors[(0, -1)].poids, h - size)
                glEnd()
            elif diff == (1, 1):
                # 01, 10
                glBegin(GL_TRIANGLES)
                glColor3f(
                    *self.bridge_color_diagonal(
                        case, (neighbors[(0, 1)], neighbors[(1, 0)])
                    )
                )
                glVertex3f(w + size, self.poids, h + size)
                glVertex3f(w + size * 2, neighbors[(1, 0)].poids, h + size)
                glVertex3f(w + size, neighbors[(0, 1)].poids, h + size * 2)
                glEnd()

    def depart(self):
        """Définit la case comme la case de départ."""
        self.distance = 0
        self.start = True

    def arrivee(self):
        """Définit la case comme la case d'arrivée."""
        self.end = True

    def traverser(self, max_dist):
        """Traverse la case."""
        self.trav = self.distance / max_dist

    def longueur(self, case):
        """Renvoie la longueur du chemin entre deux cases."""
        distance_horiz = pow(self.x - case.x, 2) + pow(self.y - case.y, 2)
        distance_diag = sqrt(distance_horiz + pow(self.poids - case.poids, 2))
        return distance_diag

    def __repr__(self):
        """Returns the case under string representation."""
        return f"({self.x},{self.y}): {self.poids}"

    def __lt__(self, other):
        """Returns lesser-than comparisons between two cases."""
        return self.distance < other.distance

    def __gt__(self, other):
        """Returns greater-than comparisons between two cases."""
        return self.distance > other.distance


class Grille:
    """Grille composée de cases."""

    def __init__(self, taille, i, j):
        """Crée une grille contenant des cases.

        Chaque case mesure taille, et la grille possède i x j cases.
        """
        self.taille = taille
        self.i = i
        self.j = j
        self.dep = None
        self.arr = None

        self.zoom = 6 * taille * max(i, j)
        self.theta = 0
        self.phi = pi / 2 - pi / 10

        self.perspective = False

        self.generate(True)

    def generate(self, smooth):
        """Remplit la grille de cases initialisées. Peut être adoucie."""
        self.cases = [[[] for _ in range(self.j + 2)] for _ in range(self.i + 2)]
        self.cases[0] = [Case(0, x, inf) for x in range(self.j + 2)]
        self.cases[self.i + 1] = [Case(self.i + 1, x, inf) for x in range(self.j + 2)]

        for ligne in range(1, self.i + 1):
            self.cases[ligne][0] = Case(ligne, 0, inf)
            self.cases[ligne][self.j + 1] = Case(ligne, self.j + 1, inf)
            for colonne in range(1, self.j + 1):
                self.cases[ligne][colonne] = Case(ligne, colonne, randrange(129))

        weights = [[[] for _ in range(self.j + 2)] for _ in range(self.i + 2)]

        if smooth:
            for case in chain(*self.cases):
                if case.status != Status.NONTRAVERSABLE:
                    weights[case.x][case.y] = self.smooth(case)

            for case in chain(*self.cases):
                if case.status != Status.NONTRAVERSABLE:
                    case.poids = weights[case.x][case.y]

    def smooth(self, case):
        """Flattens the case to the level of its neighbors."""
        n = [c.poids for c in self.neighbors(case)]
        return sum(n) // len(n)

    def reset(self):
        """Réinitialise la grille et ses cases, sans modifier leur poids."""
        self.dep = None
        self.arr = None

        self.perspective = False

        for col in self.cases:
            for case in col:
                case.reset()

    def smallest(self):
        """Find the smallest unvisited case."""
        return min(filter(lambda c: c.status == Status.UNVISITED, chain(*self.cases)))

    def astar(self):
        """Find the smallest unvisited case (A* variation)."""
        return min(
            filter(lambda c: c.status == Status.UNVISITED, chain(*self.cases)),
            key=lambda c: c.distance + c.longueur(self.arr),
        )

    def neighbors(self, case):
        """Find all traversable neighbors."""
        adjacents = filter(
            lambda c: c != (case.x, case.y),
            product([case.x - 1, case.x, case.x + 1], [case.y - 1, case.y, case.y + 1]),
        )

        cases_adj = [
            self.cases[x][y]
            for x, y in adjacents
            if self.cases[x][y].status != Status.NONTRAVERSABLE
        ]

        return cases_adj

    def dijkstra(self, smallest, time=0.01):
        """Fills each case's attributes according to Dijkstra's algorithm."""
        while smallest().distance != inf and self.arr.status != Status.VISITED:
            current = smallest()
            for case in self.neighbors(current):
                if case.status == Status.UNVISITED:
                    dis = current.distance + current.longueur(case)
                    if dis < case.distance:
                        case.distance = dis
                        case.prev = current

            current.status = Status.VISITED
            sleep(time)

    def path(self, algorithm, *args):
        """Return a list containing the path from the start case to the end case."""
        algorithm(*args, 0)

        case = self.arr
        cases_path = []
        while case is not None:
            cases_path.append(case)
            case = case.prev

        return list(reversed(cases_path))

    def draw(self):
        """Draw the grid."""
        if self.perspective:
            x_offset = grille.taille * (grille.i + 2)
            z_offset = grille.taille * (grille.j + 2)
            gluLookAt(
                x_offset,
                grille.zoom * sin(grille.phi),
                grille.zoom * cos(grille.phi) + z_offset,
                x_offset,
                0,
                z_offset,
                0,
                cos(grille.phi),
                -sin(grille.phi),
            )
            glTranslatef(x_offset, 0, z_offset)
            glRotatef(self.theta, 0, 1, 0)
            glTranslatef(-x_offset, 0, -z_offset)
        for ligne in range(1, self.i + 1):
            for colonne in range(1, self.j + 1):
                if self.perspective:
                    self.cases[ligne][colonne].draw(self.taille)
                    self.cases[ligne][colonne].draw_bridge(
                        self.neighbors(self.cases[ligne][colonne]), self.taille
                    )
                else:
                    self.cases[ligne][colonne].draw_sel(self.taille)

    def drawpath(self):
        """Draws the path on the grid, after initalization of the start and end case."""
        path = grille.path(grille.dijkstra, grille.astar)
        for case in path:
            case.traverser(path[-1].distance)
            sleep(0.05)
        print(self.arr.distance)

    def clic_case(self, x, y):
        """Cliquer sur une case."""
        x //= self.taille
        y //= self.taille
        if (
            not self.perspective
            and x <= self.i
            and y <= self.j
            and self.cases[x][y].poids != inf
        ):
            if not self.dep:
                self.dep = self.cases[x][y]
                self.dep.depart()
            elif not self.arr:
                self.arr = self.cases[x][y]
                self.arr.arrivee()


grille = Grille(32, 38, 29)

def init():
    """Initialise la fenêtre OpenGL."""
    global grille
    if grille.perspective:
        glEnable(GL_DEPTH_TEST)
    else:
        glDisable(GL_DEPTH_TEST)
    glClearColor(0, 0, 0, 0)


def display():
    """Affiche la fenêtre OpenGL."""
    global grille
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    # grille.draw()
    worm = Worm(0, 0, 0, 10)
    worm.draw()

    glutSwapBuffers()


def reshape(width, height):
    """Reforme la fenêtre et bouge les formes dedans."""
    global grille
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if grille.perspective:
        gluPerspective(16, width / height, 200, 10000)
    else:
        glOrtho(0, width, height, 0, 20, 0)
    glMatrixMode(GL_MODELVIEW)


def keyboard(key, x, y):
    """Réagit aux entrées clavier."""
    global grille

    if key == b"\r":
        grille.perspective = not grille.perspective
        init()
        reshape(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
        if grille.perspective:
            # draw = threading.Thread(target=grille.drawpath, daemon=True)
            # draw.start()
            pass
        else:
            grille.reset()

    if grille.perspective:
        if key == b"z":
            grille.zoom -= 10
        elif key == b"x":
            grille.zoom += 10
        elif key == b"w":
            grille.phi = (grille.phi + 0.02 * pi) % (pi * 2)
        elif key == b"s":
            grille.phi = (grille.phi - 0.02 * pi) % (pi * 2)
        elif key == b"a":
            grille.theta = (grille.theta - 2) % 360
        elif key == b"d":
            grille.theta = (grille.theta + 2) % 360

    if key == b"q":
        glutDestroyWindow(glutGetWindow())

    if key != b"q":
        glutPostRedisplay()

    print(key, grille.theta, grille.phi, grille.zoom)


def mouse(button, state, x, y):
    """Réagit au clic de souris."""
    global grille
    if state:
        grille.clic_case(x, y)
    if button == 3:
        grille.zoom -= 10
    if button == 4:
        grille.zoom -= 10
    glutPostRedisplay()


if __name__ == "__main__":
    if "d" not in sys.argv:
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)

        glutCreateWindow("pathfinder")
        glutReshapeWindow(512, 512)

        glutReshapeFunc(reshape)
        glutDisplayFunc(display)
        glutIdleFunc(display)
        glutKeyboardFunc(keyboard)
        glutMouseFunc(mouse)

        init()

        glutMainLoop()
