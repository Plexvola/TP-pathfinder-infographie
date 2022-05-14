"""Pathfinder d'un point A à un point B en OpenGL."""
import sys
import pickle
import argparse
import threading
from enum import Enum
from itertools import chain, product
from math import cos, inf, pi, pow, sin, sqrt, comb
from random import randrange
from time import sleep

from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST,
                       GL_MODELVIEW, GL_PROJECTION, GL_QUADS, glBegin, glClear,
                       glClearColor, glColor, glDisable, glEnable, glEnd,
                       glLoadIdentity, glMatrixMode, glOrtho, glPopMatrix,
                       glPushMatrix, glRotatef, glTranslatef, glVertex2f,
                       glVertex3f, glViewport)
from OpenGL.GLU import gluLookAt, gluPerspective
from OpenGL.GLUT import (GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGBA,
                         GLUT_WINDOW_HEIGHT, GLUT_WINDOW_WIDTH,
                         glutCreateWindow, glutDestroyWindow, glutDisplayFunc,
                         glutGet, glutGetWindow, glutIdleFunc, glutInit,
                         glutInitDisplayMode, glutKeyboardFunc, glutMainLoop,
                         glutMouseFunc, glutPostRedisplay, glutReshapeFunc,
                         glutReshapeWindow, glutSwapBuffers)

HEIGHT = 256


def bezier(p, t):
    x = 0
    y = 0
    z = 0
    i = 0
    while i < len(p):
        x += p[i].x * pow(1-t, i) * pow(t, len(p)-1 - i) * comb(len(p)-1, i)
        y += p[i].poids * pow(1-t, i) * pow(t, len(p)-1 - i) * comb(len(p)-1, i)
        z += p[i].y * pow(1-t, i) * pow(t, len(p)-1 - i) * comb(len(p)-1, i)
        i += 1
    return (x, y, z)


class Status(Enum):
    """Le statut possible de chaque case."""

    VISITED = 0
    UNVISITED = 1
    NONTRAVERSABLE = 2


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
            return (self.poids / HEIGHT, 0.45, 1)
        elif self.end:
            return (0, 1, 0)
        elif self.start:
            return (1, 0, 0)
        elif self.trav:
            return (sqrt(1 - pow(self.trav, 2)), self.trav, 0)
        elif self.status == Status.VISITED:
            return (self.poids / HEIGHT, 1, 0.6)  # nice toxic waste effect
        else:
            # return (self.poids / HEIGHT, self.poids / HEIGHT, self.poids / HEIGHT)
            return (1, self.poids/HEIGHT, 0.2)

    def reset(self):
        """Une fonction qui réinitialise la case."""
        if self.status == Status.VISITED:
            self.status = Status.UNVISITED

        self.distance = inf
        self.prev = None
        self.start = False
        self.end = False
        self.trav = None

    def draw(self, size, threshold):
        """Affiche la case à l'écran."""
        w = self.x * size
        h = self.y * size
        elevation = self.poids if self.poids != inf else threshold
        glPushMatrix()
        glBegin(GL_QUADS)
        glColor(*self.color())

        # face du bas
        glVertex3f(w, 0, h)
        glVertex3f(w + size, 0, h)
        glVertex3f(w + size, 0, h + size)
        glVertex3f(w, 0, h + size)

        # face du haut
        glVertex3f(w, elevation, h)
        glVertex3f(w + size, elevation, h)
        glVertex3f(w + size, elevation, h + size)
        glVertex3f(w, elevation, h + size)

        # face de derrière
        glVertex3f(w, 0, h)
        glVertex3f(w + size, 0, h)
        glVertex3f(w + size, elevation, h)
        glVertex3f(w, elevation, h)

        # face de devant
        glVertex3f(w, 0, h + size)
        glVertex3f(w + size, 0, h + size)
        glVertex3f(w + size, elevation, h + size)
        glVertex3f(w, elevation, h + size)

        # face de gauche
        glVertex3f(w, 0, h)
        glVertex3f(w, elevation, h)
        glVertex3f(w, elevation, h + size)
        glVertex3f(w, 0, h + size)

        # face de gauche
        glVertex3f(w + size, 0, h)
        glVertex3f(w + size, elevation, h)
        glVertex3f(w + size, elevation, h + size)
        glVertex3f(w + size, 0, h + size)

        glEnd()
        glPopMatrix()

    def draw_sel(self, size):
        """Affiche la case durant la sélection non-perspective."""
        glPushMatrix()
        glBegin(GL_QUADS)
        glColor(*self.color())
        glVertex2f(self.x * size, self.y * size)
        glVertex2f(self.x * size + size, self.y * size)
        glVertex2f(self.x * size + size, self.y * size + size)
        glVertex2f(self.x * size, self.y * size + size)
        glEnd()
        glPopMatrix()

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

    def __init__(self, taille, i, j, threshold):
        """Crée une grille contenant des cases.

        Chaque case mesure taille, et la grille possède i x j cases.
        """
        self.taille = taille
        self.i = i
        self.j = j
        self.dep = None
        self.arr = None

        self.zoom = 4 * taille * max(i, j)
        self.theta = 0
        self.phi = pi / 2 - pi / 10

        self.perspective = False
        self.threshold = HEIGHT * (threshold/100)

        self.generate(args.smoothing)

    def generate(self, smooth):
        """Remplit la grille de cases initialisées. Peut être adoucie."""
        self.cases = [[[] for _ in range(self.j + 2)] for _ in range(self.i + 2)]
        self.cases[0] = [Case(0, x, inf) for x in range(self.j + 2)]
        self.cases[self.i + 1] = [Case(self.i + 1, x, inf) for x in range(self.j + 2)]

        for ligne in range(1, self.i + 1):
            self.cases[ligne][0] = Case(ligne, 0, inf)
            self.cases[ligne][self.j + 1] = Case(ligne, self.j + 1, inf)
            for colonne in range(1, self.j + 1):
                self.cases[ligne][colonne] = Case(ligne, colonne, randrange(HEIGHT+1))

        weights = [[[] for _ in range(self.j + 2)] for _ in range(self.i + 2)]

        if smooth:
            for case in chain(*self.cases):
                if case.status != Status.NONTRAVERSABLE:
                    weights[case.x][case.y] = self.smooth(case)

            for case in chain(*self.cases):
                if case.status != Status.NONTRAVERSABLE:
                    case.poids = weights[case.x][case.y]

        for case in chain(*self.cases):
            if case.poids < self.threshold:
                case.status = Status.NONTRAVERSABLE

    def smooth(self, case):
        """Flattens the case to the level of its neighbors."""
        n = [c.poids for c in self.neighbors(case, 2) if c.status != Status.NONTRAVERSABLE]
        return sorted(n)[len(n)//2] if n else case.poids

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

    def neighbors(self, case, radius=1):
        """Find all traversable neighbors."""
        adjacents = filter(
            lambda c: 0 < c[0] <= self.i and 0 < c[1] <= self.j and c != (case.x, case.y),
            product(
                range(case.x-radius, case.x+radius+1),
                range(case.y-radius, case.y+radius+1),
            )
        )

        cases_adj = [
            self.cases[x][y]
            for x, y in adjacents
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

    def breadth_first(self, case, time=0.01):
        """Fills each case's attributes according to a breadth-first algorithm."""
        queue = [case]
        for current in queue:
            if current == self.arr:
                return
            elif current.status == Status.UNVISITED:
                for n in self.neighbors(current):
                    if n.status == Status.UNVISITED:
                        n.prev = current
                        n.distance = current.distance + current.longueur(n)
                        queue.append(n)
                current.status = Status.VISITED
            sleep(time)

    def path(self):
        """Return a list containing the path from the start case to the end case."""
        case = self.arr
        cases_path = []
        while case is not None:
            cases_path.append(case)
            case = case.prev

        return list(reversed(cases_path))

    def draw(self):
        """Draw the grid."""
        for ligne in range(1, self.i + 1):
            for colonne in range(1, self.j + 1):
                if self.perspective:
                    self.cases[ligne][colonne].draw(self.taille, self.threshold)
                else:
                    self.cases[ligne][colonne].draw_sel(self.taille)

    def drawpath(self):
        """Draws the path on the grid, after initalization of the start and end case."""
        if args.algorithm == 'astar':
            grille.dijkstra(grille.astar)
        elif args.algorithm == 'dijkstra':
            grille.dijkstra(grille.smallest)
        elif args.algorithm == 'breadth':
            grille.breadth_first(grille.dep)
        path = self.path()
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
                if self.cases[x][y].status != Status.NONTRAVERSABLE:
                    self.dep = self.cases[x][y]
                    self.dep.depart()
            elif not self.arr:
                if self.cases[x][y].status != Status.NONTRAVERSABLE:
                    self.arr = self.cases[x][y]
                    self.arr.arrivee()


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
    if grille.perspective:
        x_offset = grille.taille * (grille.i + 2) / 2
        z_offset = grille.taille * (grille.j + 2) / 2
        gluLookAt(
            0, 0, grille.zoom,
            0, 0, 0,
            0, 1, 0,
        )

        glRotatef(grille.phi, 1, 0, 0)
        glRotatef(grille.theta, 0, 1, 0)
        glTranslatef(-x_offset, 0, -z_offset)

    grille.draw()

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
            draw = threading.Thread(target=grille.drawpath, daemon=True)
            draw.start()

        else:
            grille.reset()

    if grille.perspective:
        if key == b"z":
            grille.zoom -= 10
        elif key == b"x":
            grille.zoom += 10
        elif key == b"w":
            grille.phi = (grille.phi + 2) % 360
        elif key == b"s":
            grille.phi = (grille.phi - 2) % 360
        elif key == b"a":
            grille.theta = (grille.theta - 2) % 360
        elif key == b"d":
            grille.theta = (grille.theta + 2) % 360

    else:
        if key == b"1":
            grille.threshold -= HEIGHT*0.01
            grille.generate(True)
        elif key == b"2":
            grille.threshold += HEIGHT*0.01
            grille.generate(True)
        elif key == b"r":
            grille.generate(True)
        elif key == b"S":
            with open(args.output, 'wb') as file:
                pickle.dump(grille, file)

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
        grille.zoom -= 30
    if button == 4:
        grille.zoom += 30
    glutPostRedisplay()


parser = argparse.ArgumentParser(description='Pathfinder codé entièrement en OpenGL.')
parser.add_argument('--algorithm', '-a', type=str, default='astar')
parser.add_argument('--output', '-o', type=str, default='terrain.pickle')
parser.add_argument('--input', '-i', type=str)
parser.add_argument('--threshold', '-t', type=int, default=50)
parser.add_argument('--size', '-s', type=int, default=32)
parser.add_argument('--width', '-W', type=int, default=38)
parser.add_argument('--height', '-H', type=int, default=29)
parser.add_argument('--smoothing', action=argparse.BooleanOptionalAction, default=True)
args = parser.parse_args()

if args.input:
    with open(args.input, 'rb') as file:
        grille = pickle.load(file)
else:
    grille = Grille(args.size, args.width, args.height, args.threshold)


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
