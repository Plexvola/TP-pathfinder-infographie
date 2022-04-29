"""Pathfinder d'un point A à un point B en OpenGL."""
# ----- Importation des Modules ----- #
from itertools import product, chain
from math import inf, pow, sqrt
from random import randrange
import sys
from enum import Enum
from time import sleep

from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_COLOR_MATERIAL,
                       GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_FLAT, GL_LESS,
                       GL_LIGHTING, GL_MODELVIEW, GL_POLYGON, GL_PROJECTION,
                       GL_QUADS, glBegin, glClear, glClearColor, glColor3f,
                       glColor4f, glDepthFunc, glEnable, glEnd, glLoadIdentity,
                       glMatrixMode, glOrtho, glFrustum, glVertex3f,
                       glViewport, glPushMatrix, glPopMatrix)
from OpenGL.GLU import gluPerspective, gluLookAt
from OpenGL.GLUT import (GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGBA, glutCreateWindow,
                         glutDisplayFunc, glutIdleFunc, glutInit,
                         glutInitDisplayMode, glutKeyboardFunc, glutMainLoop,
                         glutMouseFunc, glutPostRedisplay, glutReshapeFunc,
                         glutReshapeWindow, glutSwapBuffers)

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
        glColor3f(*self.couleur)
        glBegin(GL_QUADS)
        glVertex3f(self.x * width,         self.y * height, 0)
        glVertex3f(self.x * width + width, self.y * height, 0)
        glVertex3f(self.x * width + width, self.y * height + height, 0)
        glVertex3f(self.x * width,         self.y * height + height, 0)
        glEnd()

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

        Chaque case mesure taille, et la grille possède dimension cases par
        côté.
        """
        self.taille = taille
        self.i = i
        self.j = j
        self.cases = [[] for _ in range(i+2)]
        self.total = 0
        self.dep = None
        self.arr = None

        self.cases[0] = [Case(0, x, inf) for x in range(j+2)]
        self.cases[i+1] = [Case(i+1, x, inf) for x in range(j+2)]

        for ligne in range(1, self.i+1):
            self.cases[ligne].append(Case(ligne, 0, inf))
            for colonne in range(1, self.j+1):
                case = Case(ligne, colonne, randrange(1, 17))
                self.cases[ligne].append(case)
            self.cases[ligne].append(Case(ligne, self.j+1, inf))

    def smallest(self):
        return min(filter(lambda c: c.status == Status.UNVISITED, chain(*self.cases)))

    def dijkstra(self):
        case = grille.smallest()

        adjacents = filter(lambda c: c != (case.x, case.y), product(
            [case.x - 1, case.x, case.x + 1], [case.y - 1, case.y, case.y + 1]
        ))

        cases_adj = [self.cases[x][y] for x, y in adjacents if
                     self.cases[x][y].status == Status.UNVISITED]

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
        while case.prev != None:
            case = case.prev
            cases_path.append(case)

        for c in reversed(cases_path):
            c.traverser()
            self.draw()
            glutPostRedisplay()
            sleep(0.1)


    def draw(self):
        for ligne in range(self.i+2):
            for colonne in range(self.j+2):
                self.cases[ligne][colonne].draw(self.taille, self.taille)

    def clic_case(self, x, y):
        """Cliquer sur une case."""
        print(self.cases[x // self.taille][y // self.taille])
        if not self.dep:
            self.dep = self.cases[x // self.taille][y // self.taille]
            self.dep.depart()
        elif not self.arr:
            self.arr = self.cases[x // self.taille][y // self.taille]
            self.arr.arrivee()

            self.path()


grille = Grille(120, 5, 5)

def init():
    global grille
    """Initialise la fenêtre OpenGL."""
    # glEnable(GL_DEPTH_TEST)
    # glDepthFunc(GL_LESS)
    glClearColor(0, 0, 0, 0)
    for g in grille.cases:
        print(list(filter(lambda x: x.poids != inf, g)))



def display():
    """Affiche la fenêtre OpenGL."""
    global grille
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # glLoadIdentity()
    # gluLookAt(0, 0, 1,
    #           0, 0, 0,
    #           0, 1, 0)
    # glPushMatrix()
    grille.draw()
    # glPopMatrix()

    glutSwapBuffers()


def reshape(width, height):
    """Reforme la fenêtre et bouge les formes dedans."""
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, height, 0, 1, 0)
    # gluPerspective(20, width / height, 3, 200)
    glMatrixMode(GL_MODELVIEW)


def keyboard(key, x, y):
    """Réagit aux entrées clavier."""
    print(key)
    glutPostRedisplay()


def mouse(button, state, x, y):
    """Réagit au clic de souris."""
    global grille
    if state:
        grille.clic_case(x, y)


if __name__ == '__main__':
    if 'g' in sys.argv:
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


# couleur : 15 couleurs (255 : 17 = 15)
# https://openclassrooms.com/forum/sujet/tkinter-lier-des-labels-avec-un-dictionnaire
