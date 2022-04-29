"""Pathfinder d'un poi0.65A à un point B en OpenGL."""
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
                       glShadeModel, glVertex3f, glViewport, glget,
                       GL_VIEWPORT, glVertex2f, glRotatef, glTranslatef,
                       glMultMatrixf)
from OpenGL.GLU import gluLookAt, gluPerspective
from OpenGL.GLUT import (GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGBA, glutCreateWindow,
                         glutDisplayFunc, glutIdleFunc, glutInit,
                         glutInitDisplayMode, glutKeyboardFunc, glutMainLoop,
                         glutMouseFunc, glutPostRedisplay, glutReshapeFunc,
                         glutReshapeWindow, glutSolidCube, glutSwapBuffers,
                         glutDestroyWindow, glutGetWindow, GLUT_WINDOW_HEIGHT,
                         GLUT_WINDOW_WIDTH, glutGet, glutFullScreen)


class Status(Enum):
    UNVISITED = True
    VISITED = False


class Case:
    """Case unique, avec un poids et une position."""

    def __init__(self, x, y, poids):
        """Initialise la case."""
        self.x = x
        self.y = y
        self.couleur = (0.058*poids, 0.8, 1)
        if poids == inf:
            self.couleur = (0.2, 0.2, 0.2)
        self.poids = poids
        self.distance = inf
        self.status = Status.UNVISITED
        self.prev = None

    def draw(self, width, height):
        """Affiche la case à l'écran."""
        w = self.x * width * 2
        h = self.y * height * 2
        glPushMatrix()
        glBegin(GL_QUADS)
        glColor3f(*self.couleur)

        # face du bas
        glVertex3f(w, 0, h)
        glVertex3f(w + width, 0, h)
        glVertex3f(w + width, 0, h + height)
        glVertex3f(w, 0, h + height)

        # face du haut
        glVertex3f(w, self.poids*10, h)
        glVertex3f(w + width, self.poids*10, h)
        glVertex3f(w + width, self.poids*10, h + height)
        glVertex3f(w, self.poids*10, h + height)

        # face de derrière
        glVertex3f(w, 0, h)
        glVertex3f(w + width, 0, h)
        glVertex3f(w + width, self.poids*10, h)
        glVertex3f(w, self.poids*10, h)

        # face de devant
        glVertex3f(w, 0, h + height)
        glVertex3f(w + width, 0, h + height)
        glVertex3f(w + width, self.poids*10, h + height)
        glVertex3f(w, self.poids*10, h + height)

        # face de gauche
        glVertex3f(w, 0, h)
        glVertex3f(w, self.poids*10, h)
        glVertex3f(w, self.poids*10, h + height)
        glVertex3f(w, 0, h + height)

        # face de gauche
        glVertex3f(w + width, 0, h)
        glVertex3f(w + width, self.poids*10, h)
        glVertex3f(w + width, self.poids*10, h + height)
        glVertex3f(w + width, 0, h + height)

        glEnd()
        glPopMatrix()

    def draw_s(self, width, height):
        """Affiche la case durant la sélection non-perspective."""
        glPushMatrix()
        glBegin(GL_QUADS)
        glColor3f(*self.couleur)
        glVertex2f(self.x * width,         self.y * height)
        glVertex2f(self.x * width + width, self.y * height)
        glVertex2f(self.x * width + width, self.y * height + height)
        glVertex2f(self.x * width,         self.y * height + height)
        glEnd()
        glPopMatrix()

    def depart(self):
        """Définit la case comme la case de départ."""
        self.couleur = (0, 1, 0)
        self.distance = 0

    def arrivee(self):
        """Définit la case comme la case d'arrivée."""
        self.couleur = (1, 0, 0)

    def traverser(self):
        """Traverse la case."""
        self.couleur = (1, 0.01 * self.distance, 0)

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
        self.cases = [[] for _ in range(i + 2)]
        self.total = 0
        self.dep = None
        self.arr = None

        self.zoom = 3200
        self.theta = 0
        self.phi = 0

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
        current = grille.smallest()

        adjacents = filter(
            lambda c: c != (current.x, current.y),
            product([current.x - 1, current.x, current.x + 1],
                    [current.y - 1, current.y, current.y + 1]),
        )

        cases_adj = [
            self.cases[x][y]
            for x, y in adjacents
            if self.cases[x][y].status == Status.UNVISITED
        ]

        for case in cases_adj:
            dis = current.distance + current.longueur(case)
            if dis < case.distance:
                case.distance = dis
                case.prev = current

        current.status = Status.VISITED


    def path(self):
        while self.smallest().distance != inf and self.arr.status != Status.VISITED:
            self.dijkstra()

        case = self.arr
        cases_path = []
        while case is not None:
            cases_path.append(case)
            case = case.prev

        for c in reversed(cases_path):
            c.traverser()
            self.draw()

    def draw(self):
        if self.perspective:
            x_offset = grille.taille * (grille.i+2)
            z_offset = grille.taille * (grille.j+2)
            gluLookAt(
                x_offset, grille.zoom * sin(grille.phi), grille.zoom * cos(grille.phi) + z_offset,
                x_offset,                             0,                                 z_offset,
                0,                                    cos(grille.phi),           -sin(grille.phi),
            )
            glTranslatef(x_offset, 0, z_offset)
            glRotatef(self.theta, 0, 1, 0)
            glTranslatef(-x_offset, 0, -z_offset)
        for ligne in range(1, self.i+1):
            for colonne in range(1, self.j+1):
                if self.perspective:
                    self.cases[ligne][colonne].draw(self.taille, self.taille)
                else:
                    self.cases[ligne][colonne].draw_s(self.taille, self.taille)

    def clic_case(self, x, y):
        """Cliquer sur une case."""
        x //= self.taille
        y //= self.taille
        if not self.perspective \
                and x < self.i and y < self.j \
                and self.cases[x][y].poids != inf:
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
    print(width, height)
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
    print(key, grille.theta, grille.phi, grille.zoom)

    if key == b" ":
        grille.perspective = not grille.perspective
        init()
        reshape(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
        if grille.perspective:
            grille.path()

    if grille.perspective:
        if key == b"z":
            grille.zoom -= 10
        elif key == b"x":
            grille.zoom += 10
        elif key == b"w":
            grille.phi = (grille.phi + 0.05 * pi) % (pi * 2)
        elif key == b"s":
            grille.phi = (grille.phi - 0.05 * pi) % (pi * 2)
        elif key == b"a":
            grille.theta = (grille.theta - 2) % 360
        elif key == b"d":
            grille.theta = (grille.theta + 2) % 360

    if key == b'q':
        glutDestroyWindow(glutGetWindow())

    if key != b'q':
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
