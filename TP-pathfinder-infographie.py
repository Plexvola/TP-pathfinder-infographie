"""Pathfinder d'un point A à un point B en OpenGL."""
# ----- Importation des Modules ----- #
from itertools import product
from math import inf, pow, sqrt
from random import randrange

from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_COLOR_MATERIAL,
                       GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_FLAT, GL_LESS,
                       GL_LIGHTING, GL_MODELVIEW, GL_POLYGON, GL_PROJECTION,
                       GL_QUADS, glBegin, glClear, glClearColor, glColor3f,
                       glColor4f, glDepthFunc, glEnable, glEnd, glLoadIdentity,
                       glMatrixMode, glOrtho, glFrustum, glVertex3f, glViewport)
from OpenGL.GLU import gluPerspective
from OpenGL.GLUT import (GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGBA, glutCreateWindow,
                         glutDisplayFunc, glutIdleFunc, glutInit,
                         glutInitDisplayMode, glutKeyboardFunc, glutMainLoop,
                         glutMouseFunc, glutPostRedisplay, glutReshapeFunc,
                         glutReshapeWindow, glutSwapBuffers)


class Case:
    """Case unique, avec un poids et une position."""

    def __init__(self, x, y, poids):
        """Initialise la case."""
        self.x = x
        self.y = y
        self.couleur = (1, 0.058 * poids, 1)
        self.poids = poids
        self.cost = inf

    def draw(self, width, height):
        """Affiche la case à l'écran."""
        glColor3f(*self.couleur)
        glBegin(GL_QUADS)
        glVertex3f(self.x * width, self.y * height, 0)
        glVertex3f(self.x * width + width, self.y * height, 0)
        glVertex3f(self.x * width + width, self.y * height + height, 0)
        glVertex3f(self.x * width, self.y * height + height, 0)
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
        distance_diag = sqrt(distance_horiz + pow(self.poids - case.poids), 2)
        return distance_diag


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
        self.cases = [[] for _ in range(i)]
        self.total = 0
        self.dep = None
        self.arr = None

        for ligne in range(self.i):
            for colonne in range(self.j):
                case = Case(ligne, colonne, randrange(1, 17))
                self.cases[ligne].append(case)

    def dijkstra(self, case):
        if case.cost == inf:
            Exception("nope")

        adj = product(
            [case.x - 1, case.x, case.x + 1], [case.y - 1, case.y, case.y + 1]
        )

        print(adj)

    def draw(self):
        for ligne in range(self.i):
            for colonne in range(self.j):
                self.cases[ligne][colonne].draw(self.taille, self.taille)

    def clic_case(self, x, y):
        """Cliquer sur une case."""
        if not self.dep:
            self.cases[x // self.taille][y // self.taille].depart()
            self.dep = (x // self.taille, y // self.taille)
        elif not self.arr:
            self.cases[x // self.taille][y // self.taille].arrivee()
            self.arr = (x // self.taille, y // self.taille)


grille = Grille(40, 10, 10)


def init():
    """Initialise la fenêtre OpenGL."""
    glClearColor(0, 0, 0, 0)


def display():
    """Affiche la fenêtre OpenGL."""
    global grille
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    grille.draw()
    glutSwapBuffers()


def reshape(width, height):
    """Reforme la fenêtre et bouge les formes dedans."""
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, height, 0, 1, 0)
    # gluPerspective(20, width / height, 5, 200)
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
