"""Pathfinder d'un point A à un point B en OpenGL."""
import sys
import threading
from enum import Enum
from itertools import chain, product
from math import cos, inf, pi, pow, sin, sqrt
from random import choice, randrange
from time import sleep

from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_COLOR_MATERIAL,
                       GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_FLAT, GL_LESS,
                       GL_LIGHT0, GL_LIGHTING, GL_MODELVIEW, GL_POLYGON,
                       GL_PROJECTION, GL_QUADS, GL_TRIANGLES, GL_VIEWPORT,
                       GLsizei, glBegin, glClear, glClearColor, glColor3f,
                       glColor4f, glDepthFunc, glDisable, glEnable, glEnd,
                       glFrustum, glget, glLoadIdentity, glMatrixMode,
                       glMultMatrixf, glOrtho, glPopMatrix, glPushMatrix,
                       glRotatef, glShadeModel, glTranslatef, glVertex2f,
                       glVertex3f, glViewport)
from OpenGL.GLU import gluLookAt, gluPerspective
from OpenGL.GLUT import (GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGBA,
                         GLUT_WINDOW_HEIGHT, GLUT_WINDOW_WIDTH,
                         glutCreateWindow, glutDestroyWindow, glutDisplayFunc,
                         glutFullScreen, glutGet, glutGetWindow, glutIdleFunc,
                         glutInit, glutInitDisplayMode, glutKeyboardFunc,
                         glutMainLoop, glutMouseFunc, glutPostRedisplay,
                         glutReshapeFunc, glutReshapeWindow, glutSolidCube,
                         glutSwapBuffers)


class Status(Enum):
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
        if self.status == Status.NONTRAVERSABLE:
            return (0.2, 0.2, 0.2)
        elif self.end:
            return (0, 1, 0)
        elif self.start:
            return (1, 0, 0)
        elif self.trav:
            return (1 - self.trav, self.trav, 0)
        elif self.status == Status.VISITED:
            return (1 / 32 * self.poids, 1 / 32 * self.poids, 1 / 32 * self.poids)
        else:
            return (1 / 32 * self.poids, 0.85, 1)

    def clean(self):
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
        w = self.x * size
        h = self.y * size
        glPushMatrix()
        glBegin(GL_QUADS)
        glColor3f(*self.color())

        # face du bas
        glVertex3f(w, 0, h)
        glVertex3f(w + size, 0, h)
        glVertex3f(w + size, 0, h + size)
        glVertex3f(w, 0, h + size)

        # face du haut
        glVertex3f(w, self.poids * 3, h)
        glVertex3f(w + size, self.poids * 3, h)
        glVertex3f(w + size, self.poids * 3, h + size)
        glVertex3f(w, self.poids * 3, h + size)

        # face de derrière
        glVertex3f(w, 0, h)
        glVertex3f(w + size, 0, h)
        glVertex3f(w + size, self.poids * 3, h)
        glVertex3f(w, self.poids * 3, h)

        # face de devant
        glVertex3f(w, 0, h + size)
        glVertex3f(w + size, 0, h + size)
        glVertex3f(w + size, self.poids * 3, h + size)
        glVertex3f(w, self.poids * 3, h + size)

        # face de gauche
        glVertex3f(w, 0, h)
        glVertex3f(w, self.poids * 3, h)
        glVertex3f(w, self.poids * 3, h + size)
        glVertex3f(w, 0, h + size)

        # face de gauche
        glVertex3f(w + size, 0, h)
        glVertex3f(w + size, self.poids * 3, h)
        glVertex3f(w + size, self.poids * 3, h + size)
        glVertex3f(w + size, 0, h + size)

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
        return f"({self.x},{self.y}): {self.poids}"

    def __lt__(self, other):
        return self.distance < other.distance

    def __gt__(self, other):
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

        self.zoom = 3 * taille * max(i, j)
        self.theta = 0
        self.phi = pi / 2

        self.perspective = False

        self.cases = [[] for _ in range(i + 2)]
        self.generate()

    def generate(self):

        self.cases[0] = [Case(0, x, inf) for x in range(self.j + 2)]
        self.cases[self.i + 1] = [Case(self.i + 1, x, inf) for x in range(self.j + 2)]

        for ligne in range(1, self.i + 1):
            self.cases[ligne].append(Case(ligne, 0, inf))
            for colonne in range(1, self.j + 1):
                case = Case(ligne, colonne, choice(list(range(1, 33))))
                self.cases[ligne].append(case)
            self.cases[ligne].append(Case(ligne, self.j + 1, inf))

        for column in self.cases[1:-1]:
            for case in column[1:-1]:
                case.poids = self.smooth(case)

    def smooth(self, case):
        """Flattens the case to the level of its neighbors."""
        print(case)
        n = [c.poids for c in self.neighbors(case)]
        return sum(n) // len(n)

    def clean(self):
        self.dep = None
        self.arr = None

        self.zoom = 3 * self.taille * max(self.i, self.j)
        self.theta = 0
        self.phi = pi / 2

        self.perspective = False

        for col in self.cases:
            for case in col:
                case.clean()

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

        cases_adj = [self.cases[x][y] for x, y in adjacents if
                     self.cases[x][y].status != Status.NONTRAVERSABLE]

        return cases_adj

    def dijkstra(self, smallest):
        """Visit a case according to the Dijkstra's algorithm."""
        current = smallest()
        for case in self.neighbors(current):
            if case.status == Status.UNVISITED:
                dis = current.distance + current.longueur(case)
                if dis < case.distance:
                    case.distance = dis
                    case.prev = current

        current.status = Status.VISITED

    def path(self):
        """Return a list containing the path from the start case to the end case."""
        while self.smallest().distance != inf and self.arr.status != Status.VISITED:
            self.dijkstra(self.astar)
            sleep(0.01)

        case = self.arr
        cases_path = []
        while case is not None:
            cases_path.append(case)
            case = case.prev

        return list(reversed(cases_path))

    def draw(self):
        """Draw the grid."""
        if self.perspective:
            x_offset = grille.taille * (grille.i + 2) / 2
            z_offset = grille.taille * (grille.j + 2) / 2
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
                else:
                    self.cases[ligne][colonne].draw_sel(self.taille)

    def drawpath(self):
        path = grille.path()
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


grille = Grille(25, 40, 37)


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
    grille.draw()

    glutSwapBuffers()


def reshape(width, height):
    """Reforme la fenêtre et bouge les formes dedans."""
    global grille
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if grille.perspective:
        gluPerspective(20, width / height, 200, 10000)
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
            grille.clean()

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
