"""Pathfinder d'un point A à un point B en OpenGL."""
# ----- Importation des Modules ----- #
import tkinter as tk
from random import randrange
from tkinter import messagebox

from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_COLOR_MATERIAL,
                       GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_FLAT, GL_LESS,
                       GL_LIGHTING, GL_MODELVIEW, GL_PROJECTION, glClear,
                       glClearColor, glColor4f, glDepthFunc, glEnable,
                       glLoadIdentity, glMatrixMode, glShadeModel, glViewport)
from OpenGL.GLU import gluPerspective
from OpenGL.GLUT import (GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGBA, glutCreateWindow,
                         glutDisplayFunc, glutInit, glutInitDisplayMode,
                         glutKeyboardFunc, glutMainLoop, glutPostRedisplay,
                         glutReshapeFunc, glutReshapeWindow)

# ----- Variables globales ----- #
taille_case = 30


def rgb_hack(rgb):
    """Transforme un nombre en sa représentation RGB."""
    return "#%02x%02x%02x" % rgb


class Case:
    """Case unique, avec un poids et une position."""

    def __init__(self, x, y, poids):
        """Initialise la case."""
        self.x = x
        self.y = y
        self.couleur = rgb_hack((255, 255 - 15 * poids, 255))
        self.poids = poids
        self.etat = "VIDE"

    def render(self, taille_case, canvas):
        """Affiche la case à l'écran."""
        self.id = canvas.create_rectangle(
            self.x * taille_case + 2,
            self.y * taille_case + 2,
            (self.x + 1) * taille_case + 2,
            (self.y + 1) * taille_case + 2,
        )
        canvas.create_text(
            self.x * taille_case + taille_case / 2,
            self.y * taille_case + taille_case / 2,
            text=self.poids,
        )
        canvas.itemconfigure(
            self.id,
            outline="black",
            fill=self.couleur,
        )

    def depart(self, canvas):
        """Définit la case comme la case de départ."""
        canvas.itemconfigure(self.id, outline="black",
                             fill=rgb_hack((0, 255, 0)))
        self.etat = "DEPART"

    def arrivee(self, canvas):
        """Définit la case comme la case d'arrivée."""
        canvas.itemconfigure(self.id, outline="black",
                             fill=rgb_hack((255, 0, 0)))
        self.etat = "ARRIVEE"

    def traverser(self, canvas):
        """Traverse la case."""
        canvas.itemconfigure(self.id, outline="black",
                             fill=rgb_hack((255, 128, 0)))
        self.etat = "CHEMIN"


class Grille:
    """Grille composée de cases."""

    def __init__(self, taille, dimension, canvas):
        """Crée une grille contenant des cases.

        Chaque case mesure taille, et la grille possède dimension cases par
        côté.
        """
        self.taille = taille
        self.dim = dimension
        self.cases = [[] for _ in range(dimension)]
        self.total = 0
        self.canvas = canvas

        self.case_d = False
        self.case_a = False

        for ligne in range(dimension):
            for colonne in range(dimension):
                case = Case(ligne, colonne, randrange(1, 17))
                case.render(taille, canvas)
                self.cases[ligne].append(case)

    def depart(self, event):
        """Place la case de départ à l'endroit cliqué."""
        x = event.x // self.taille
        y = event.y // self.taille
        self.cases[x][y].depart(self.canvas)
        self.total += self.cases[x][y].poids

    def arrivee(self, event):
        """Place la case de fin à l'endroit cliqué."""
        x = event.x // self.taille
        y = event.y // self.taille
        self.cases[x][y].arrivee(self.canvas)
        self.total += self.cases[x][y].poids

    def chemin(self, event):
        """Place une case de chemin à l'endroit cliqué."""
        x = event.x // self.taille
        y = event.y // self.taille
        if self.cases[x][y].etat == "ARRIVEE":
            print("vous etes arrivé, vous avez parcouru un total de",
                  self.total)
        elif self.cases[x][y].etat == "DEPART":
            messagebox.showwarning(
                title="case depart", message="ceci est la case de depart"
            )
        elif self.cases[x][y].etat == "CHEMIN":
            messagebox.showwarning(
                title="case depart", message="vous êtes deja passer par là"
            )
        else:
            self.cases[x][y].traverser(self.canvas)
            self.total += self.cases[x][y].poids

    def clic_case(self, event):
        """Cliquer sur une case."""
        if self.case_d:
            if self.case_a:
                self.chemin(event)
            else:
                self.arrivee(event)
                self.case_a = True
        else:
            self.depart(event)
            self.case_d = True


# # ----- Programme principal ----- #

# # ----- Création de la fenêtre ----- #
# fen = tk.Tk()
# fen.title("Chemin")

# # ----- Création des canvas ----- #
# canvas_cases = tk.Canvas(fen, width=nombre_cases * taille_case,
#                          height=nombre_cases * taille_case, bg="white")
# canvas_cases.grid(row=0, column=0, columnspan=2, padx=3, pady=3)

# # ----- Création des figures ----- #
# g = Grille(30, 50, canvas_cases)

# fen.bind("<Button-1>", g.clic_case)

# fen.mainloop()  # Boucle d'attente des événements


def init():
    """Initialise la fenêtre OpenGL."""
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearColor(0, 0, 0, 0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_FLAT)


def display():
    """Affiche la fenêtre OpenGL."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor4f(1, 1, 1, 1)


def reshape(width, height):
    """Reforme la fenêtre et bouge les formes dedans."""
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(20, width / height, 5, 200)
    glMatrixMode(GL_MODELVIEW)


def keyboard(key, x, y):
    """Réagit aux entrées clavier."""
    print(key)
    glutPostRedisplay()


glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)

glutCreateWindow("planet")
glutReshapeWindow(512, 512)

glutReshapeFunc(reshape)
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)

init()

glutMainLoop()


# couleur : 15 couleurs (255 : 17 = 15)
# https://openclassrooms.com/forum/sujet/tkinter-lier-des-labels-avec-un-dictionnaire
