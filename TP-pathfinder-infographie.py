"""Pathfinder d'un point A à un point B en OpenGL."""
# ----- Importation des Modules ----- #
import tkinter as tk
from random import randrange
from tkinter import messagebox

# ----- Variables globales ----- #
taille_case = 30
nombre_cases = 30  # Nombre de cases par ligne et par colonne
cases = []  # Liste contenant les objets cases
poids = []  # Liste contenant les nombres dans les cases
case_depart = False  # Variable qui detecte la presence d'une case depart
case_fin = False  # Variable qui detecte la presence d'une case fin
total = 0  # total du chemin


def rgb_hack(rgb):
    """Transforme un nombre en sa représentation RGB."""
    return "#%02x%02x%02x" % rgb

class Case:
    """Classe de la case."""

    def __init__(self, x, y, poids, C):
        """Initialise la case."""
        self.x = x
        self.y = y
        self.couleur = rgb_hack((255, 255 - 15 * poids, 255))
        self.poids = poids
        self.canvas = C

    def render(self, taille_case):
        """Affiche la case à l'écran."""
        self.id = self.canvas.create_rectangle(
            self.x * taille_case + 2,
            self.y * taille_case + 2,
            (self.x + 1) * taille_case + 2,
            (self.y + 1) * taille_case + 2
        )
        self.canvas.create_text(
            self.x * taille_case + taille_case/2,
            self.y * taille_case + taille_case/2,
            text=self.poids
        )
        self.canvas.itemconfigure(
            self.id, outline="black",
            fill=self.couleur,
        )


# ----- Création de la fenêtre ----- #
fen = tk.Tk()
fen.title("Chemin")

# ----- Création des canvas ----- #
canvas_cases = tk.Canvas(fen, width=nombre_cases * taille_case,
                         height=nombre_cases * taille_case, bg="white")
canvas_cases.grid(row=0, column=0, columnspan=2, padx=3, pady=3)

# ----- Création des figures ----- #
for ligne in range(nombre_cases):
    cases.append([])
    for colonne in range(nombre_cases):  # Conception des cases d'une ligne
        case = Case(ligne, colonne, randrange(1, 17), canvas_cases)
        case.render(taille_case)
        cases[ligne].append(case)


# ----- Création des nombres dans les cases colonne par colonne ----- #


def depart(event):
    """Place la case de départ à l'endroit cliqué."""
    global total
    x = event.x
    y = event.y
    canvas_cases.itemconfigure(
        cases[x // taille_case][y // taille_case].id, outline="black",
        fill=rgb_hack((0, 255, 0))
    )
    total += cases[x // taille_case][y // taille_case].poids


def fin(event):
    """Place la case de fin à l'endroit cliqué."""
    global total
    x = event.x
    y = event.y
    canvas_cases.itemconfigure(
        cases[x // taille_case][y // taille_case].id, outline="black",
        fill=rgb_hack((255, 0, 0))
    )
    total += cases[x // taille_case][y // taille_case].poids

def chemin(event):
    """Place une case de chemin à l'endroit cliqué."""
    global total
    x = event.x
    y = event.y
    if canvas_cases.itemcget(cases[x // taille_case][y // taille_case].id,
                             "fill") == rgb_hack((255, 0, 0)):
        print("vous etes arrivé, vous avez parcouru un total de", total)
    elif canvas_cases.itemcget(cases[x // taille_case][y // taille_case].id,
                               "fill") == rgb_hack((0, 255, 0)):
        messagebox.showwarning(
            title="case depart", message="ceci est la case de depart"
        )
    elif canvas_cases.itemcget(cases[x // taille_case][y // taille_case].id,
                               "fill") == rgb_hack((255, 128, 0)):
        messagebox.showwarning(
            title="case depart", message="vous êtes deja passer par là"
        )
    else:
        canvas_cases.itemconfigure(
            cases[x // taille_case][y // taille_case].id, outline="black",
            fill=rgb_hack((255, 128, 0))
        )
        total += cases[x // taille_case][y // taille_case].poids


def clic_case(event):
    """Cliquer sur une case."""
    global case_depart, case_fin
    if case_depart:
        if case_fin:
            chemin(event)
        else:
            fin(event)
            case_fin = True
    else:
        depart(event)
        case_depart = True


fen.bind("<Button-1>", clic_case)

# ----- Programme principal ----- #
fen.mainloop()  # Boucle d'attente des événements


# couleur : 15 couleurs (255 : 17 = 15)
# couleur : a = (0 -> 15) (RGB : 0,0, a * 17)

# https://openclassrooms.com/forum/sujet/tkinter-lier-des-labels-avec-un-dictionnaire
