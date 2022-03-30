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
case_depart = 0  # Variable qui detecte la presence d'une case depart
case_fin = 0  # Variable qui detecte la presence d'une case fin
total = 0  # total du chemin

# ----- Création de la fenêtre ----- #
fen = tk.Tk()
fen.title("Chemin")

# ----- Création des canvas ----- #
canvas_cases = tk.Canvas(fen, width=nombre_cases * taille_case,
                         height=nombre_cases * taille_case, bg="white")
canvas_cases.grid(row=0, column=0, columnspan=2, padx=3, pady=3)

# ----- Création des figures ----- #
for ligne in range(nombre_cases):
    bloc = []
    for colonne in range(nombre_cases):  # Conception des cases d'une ligne
        bloc.append(
            canvas_cases.create_rectangle(
                colonne * taille_case + 2,
                ligne * taille_case + 2,
                (colonne + 1) * taille_case + 2,
                (ligne + 1) * taille_case + 2,
            )
        )
    cases.append(bloc)  # Ajout de la ligne à la liste principale

# def click(event):
# x, y = event.x, event.y
# print('{},{}'.format(x,y))


def rgb_hack(rgb):
    """Transforme un nombre en sa représentation RGB."""
    return "#%02x%02x%02x" % rgb


# ----- Création des nombres dans les cases colonne par colonne ----- #

l = taille_case / 2
L = taille_case / 2
for lign in range(taille_case):
    numb = []
    for colonn in range(taille_case):
        num = randrange(1, 17)
        numb.append(num)
        canvas_cases.create_text(L, l, text=num)
        canvas_cases.itemconfigure(
            cases[colonn][lign],
            outline="black",
            fill=rgb_hack((255, 255 - 15 * num, 255)),
        )
        l += taille_case
    poids.append(numb)
    L += taille_case
    l = taille_case / 2


def depart(event):
    """Place la case de départ à l'endroit cliqué."""
    global total
    x = event.x
    y = event.y
    canvas_cases.itemconfigure(
        cases[y // taille_case][x // taille_case], outline="black",
        fill=rgb_hack((0, 255, 0))
    )
    print(poids[x // taille_case][y // taille_case])
    total += poids[x // taille_case][y // taille_case]


def fin(event):
    """Place la case de fin à l'endroit cliqué."""
    global total
    x = event.x
    y = event.y
    canvas_cases.itemconfigure(
        cases[y // taille_case][x // taille_case], outline="black",
        fill=rgb_hack((255, 0, 0))
    )
    total += poids[x // taille_case][y // taille_case]


def chemin(event):
    """Place une case de chemin à l'endroit cliqué."""
    global total
    x = event.x
    y = event.y
    if canvas_cases.itemcget(cases[y // taille_case][x // taille_case],
                             "fill") == rgb_hack((255, 0, 0)):
        print("vous etes arrivé, vous avez parcouru un total de", total)
    elif canvas_cases.itemcget(cases[y // taille_case][x // taille_case],
                               "fill") == rgb_hack((0, 255, 0)):
        messagebox.showwarning(
            title="case depart", message="ceci est la case de depart"
        )
    elif canvas_cases.itemcget(cases[y // taille_case][x // taille_case],
                               "fill") == rgb_hack((255, 128, 0)):
        messagebox.showwarning(
            title="case depart", message="vous êtes deja passer par là"
        )
    else:
        canvas_cases.itemconfigure(
            cases[y // taille_case][x // taille_case], outline="black", fill=rgb_hack((255, 128, 0))
        )
        total += poids[x // taille_case][y // taille_case]


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
fen.bind("<Control-KeyPress-d>", depart)
fen.bind("<Control-KeyPress-f>", fin)

# ----- Programme principal ----- #
fen.mainloop()  # Boucle d'attente des événements


# couleur : 15 couleurs (255 : 17 = 15)
# couleur : a = (0 -> 15) (RGB : 0,0, a * 17)

# https://openclassrooms.com/forum/sujet/tkinter-lier-des-labels-avec-un-dictionnaire
