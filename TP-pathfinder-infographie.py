"""Pathfinder d'un point A à un point B en OpenGL."""
# ----- Importation des Modules ----- #
import sys
from enum import Enum
from itertools import chain, product
from math import cos, inf, pi, pow, sin, sqrt
from random import randrange
from time import sleep

from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_COLOR_MATERIAL,
                       GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_FLAT, GL_LESS,
                       GL_LIGHT0, GL_LIGHTING, GL_MODELVIEW, GL_POLYGON,
                       GL_PROJECTION, GL_QUADS, GLsizei, glBegin, glClear,
                       glClearColor, glColor3f, glColor4f, glDepthFunc,
                       glDisable, glEnable, glEnd, glFrustum, glLoadIdentity,
                       glMatrixMode, glOrtho, glPopMatrix, glPushMatrix,
                       glShadeModel, glVertex3f, glViewport)
from OpenGL.GLU import gluLookAt, gluPerspective
from OpenGL.GLUT import (GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGBA, glutCreateWindow,
                         glutDisplayFunc, glutIdleFunc, glutInit,
                         glutInitDisplayMode, glutKeyboardFunc, glutMainLoop,
                         glutMouseFunc, glutPostRedisplay, glutReshapeFunc,
                         glutReshapeWindow, glutSolidCube, glutSwapBuffers)


class Status(Enum):
    UNVISITED = True
    VISITED = False


class Case:
    """Case unique, avec un poids et une position."""

    def __init__(self, x, y, poids):
        """Initialise la case."""
        self.x = x
        self.y = y
        self.couleur = (1, 0.058 * poids, 1)
        if poids == inf:
            self.couleur = (0.2, 0.2, 0.2)
        self.poids = poids
        self.cost = inf
        self.status = Status.UNVISITED
        self.prev = None

    def draw(self, width, height):
        """Affiche la case à l'écran."""
        glPushMatrix()
        glBegin(GL_QUADS)
        glColor3f(*self.couleur)
        glVertex3f(self.x * width, self.y * height, 0)
        glVertex3f(self.x * width + width, self.y * height, 0)
        glVertex3f(self.x * width + width, self.y * height + height, 0)
        glVertex3f(self.x * width, self.y * height + height, 0)
        glEnd()
        glPopMatrix()

    def depart(self):
        """Définit la case comme la case de départ."""
        self.couleur = (0, 1, 0)
        self.cost = 0

    def arrivee(self):
        """Définit la case comme la case d'arrivée."""
        self.couleur = (1, 0, 0)

    def traverser(self):
        """Traverse la case."""
        self.couleur = (1, 0.5, 0)

    def distance(self, case):
        """Renvoie la distance entre deux cases."""
        distance_horiz = pow(self.x - case.x, 2) + pow(self.y - case.y, 2)
        distance_diag = sqrt(distance_horiz + pow(self.poids - case.poids, 2))
        return distance_diag

    def __repr__(self):
        return f"({self.x},{self.y}): {self.poids}"

    def __lt__(self, other):
        return self.cost < other.cost

    def __gt__(self, other):
        return self.cost > other.cost


class Grille:
    """Grille composée de cases."""

    def __init__(self, taille, i, j):
        """Crée une grille contenant des cases.

        Chaque case mesure taille, et la grille possède i x j cases.
        """
        self.taille = taille
        self.i = i
        self.j = j
        self.cases = [[] for _ in range(i + 2)]
        self.total = 0
        self.dep = None
        self.arr = None
        self.zoom = 2000

        self.perspective = False

        self.cases[0] = [Case(0, x, inf) for x in range(j + 2)]
        self.cases[i + 1] = [Case(i + 1, x, inf) for x in range(j + 2)]

        for ligne in range(1, self.i + 1):
            self.cases[ligne].append(Case(ligne, 0, inf))
            for colonne in range(1, self.j + 1):
                case = Case(ligne, colonne, randrange(1, 17))
                self.cases[ligne].append(case)
            self.cases[ligne].append(Case(ligne, self.j + 1, inf))

    def smallest(self):
        return min(filter(lambda c: c.status == Status.UNVISITED, chain(*self.cases)))

    def dijkstra(self):
        case = grille.smallest()

        adjacents = filter(
            lambda c: c != (case.x, case.y),
            product([case.x - 1, case.x, case.x + 1], [case.y - 1, case.y, case.y + 1]),
        )

        cases_adj = [
            self.cases[x][y]
            for x, y in adjacents
            if self.cases[x][y].status == Status.UNVISITED
        ]

        for caseadj in cases_adj:
            d = case.distance(caseadj) + case.poids
            if d < caseadj.cost:
                caseadj.cost = d
                caseadj.prev = case

        case.status = Status.VISITED
        return case

    def path(self):
        while self.smallest().cost != inf and self.arr.status != Status.VISITED:
            self.dijkstra()

        case = self.arr
        cases_path = [case]
        while case.prev is not None:
            case = case.prev
            cases_path.append(case)

        for c in reversed(cases_path):
            c.traverser()
            self.draw()
            glutPostRedisplay()
            sleep(0.1)

    def draw(self):
        for ligne in range(self.i + 2):
            for colonne in range(self.j + 2):
                self.cases[ligne][colonne].draw(self.taille, self.taille)

    def clic_case(self, x, y):
        """Cliquer sur une case."""
        print(self.cases[x // self.taille][y // self.taille])
        if not self.perspective:
            if not self.dep:
                self.dep = self.cases[x // self.taille][y // self.taille]
                self.dep.depart()
            elif not self.arr:
                self.arr = self.cases[x // self.taille][y // self.taille]
                self.arr.arrivee()


grille = Grille(40, 10, 15)
theta, phi = 0, 180


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
        x_offset = grille.taille * (grille.i+2) / 2
        y_offset = grille.taille * (grille.j+2) / 2
        gluLookAt(
            x_offset, grille.zoom * sin(phi) + y_offset, grille.zoom * cos(phi),
            x_offset,                          y_offset,                      0,
            0,               cos(phi),              -sin(phi),
        )
    grille.draw()

    glutSwapBuffers()


def reshape(width, height):
    """Reforme la fenêtre et bouge les formes dedans."""
    global grille
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if grille.perspective:
        gluPerspective(20, width / height, 500, 5000)
    else:
        glOrtho(0, width, height, 0, 1, 0)
    glMatrixMode(GL_MODELVIEW)


def keyboard(key, x, y):
    """Réagit aux entrées clavier."""
    global grille, theta, phi
    print(key, theta, phi)
    if key == b"z":
        grille.zoom -= 5
    if key == b"x":
        grille.zoom += 5
    elif key == b"w":
        phi = (phi + 0.05 * pi) % (pi * 2)
    elif key == b"s":
        phi = (phi - 0.05 * pi) % (pi * 2)
    elif key == b"a":
        theta0 = (theta - 0.05 * pi) % (pi * 2)
    elif key == b"d":
        theta = (theta + 0.05 * pi) % (pi * 2)
    elif key == b" ":
        grille.perspective = not grille.perspective
        init()
        # grille.path()
    glutPostRedisplay()


def mouse(button, state, x, y):
    """Réagit au clic de souris."""
    global grille
    if state:
        grille.clic_case(x, y)
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
