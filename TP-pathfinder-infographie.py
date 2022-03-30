##----- Importation des Modules -----##
from tkinter import *
from random import randrange
from tkinter import messagebox

##----- Variables globales -----##
c = 30                       # Longueur d'un côté d'une case
n = 30                       # Nombre de cases par ligne et par colonne
cases = []                      # Liste contenant les objets cases
nombres = []                    #Liste contenant les nombres dans les cases
casedeb = 0                     #Variable qui detecte la presence d'une case depart
casefin = 0                     #Variable qui detecte la presence d'une case fin
total = 0                       #total du chemin

##----- Création de la fenêtre -----##
fen = Tk()
fen.title('Chemin')

##----- Création des canevas -----##
bloc_chemin = Canvas(fen, width = n*c, height = n*c, bg = 'white')
bloc_chemin.grid(row = 0, column = 0, columnspan=2, padx=3, pady=3)

##----- Création des figures -----##
for ligne in range(n):          # Les cases de chaque ligne seront stockées dans "transit"
    bloc=[]
    for colonne in range(n):    # Conception des cases d'une ligne
        bloc.append(bloc_chemin.create_rectangle(colonne*c+2, ligne*c+2, (colonne+1)*c+2, (ligne+1)*c+2))
    cases.append(bloc)       # Ajout de la ligne à la liste principale

#def click(event):
    #x, y = event.x, event.y
    #print('{},{}'.format(x,y))


def rgb_hack(rgb):
    return "#%02x%02x%02x" % rgb



##----- Création des nombres dans les cases colonne par colonne -----##

l=c/2
L=c/2
for lign in range(c):
    numb=[]
    for colonn in range(c):
        num=randrange(1,17)
        numb.append(num)
        bloc_chemin.create_text(L, l, text=num)
        bloc_chemin.itemconfigure(cases[colonn][lign], outline='black', fill=rgb_hack((255, 255-15*num, 255)))
        l+=c
    nombres.append(numb)
    L+=c
    l=c/2


def depart(event):
    global total, casedeb
    x=event.x
    y=event.y
    if casedeb == 1 :
        messagebox.showwarning(title='case depart', message='case de depart deja initialisé')
    else:
        bloc_chemin.itemconfigure(cases[y//c][x//c], outline='black', fill=rgb_hack((0,255,0)))
        casedeb += 1
        print(nombres[x//c][y//c])
        total+=nombres[x//c][y//c]

def fin(event):
    global total,casedeb, casefin
    x=event.x
    y=event.y
    if casedeb == 0:
        messagebox.showwarning(title='case depart', message='Veuillez commencer par definir une case depart')
    elif casefin == 1:
        messagebox.showwarning(title='case fin', message='case fin deja initialisé')
    else:
        bloc_chemin.itemconfigure(cases[y//c][x//c], outline='black', fill=rgb_hack((255,0,0)))
        casefin += 1
        total+=nombres[x//c][y//c]

def chemin(event):
    global total,casedeb, casefin
    x=event.x
    y=event.y
    if bloc_chemin.itemcget(cases[y//c][x//c],'fill') == rgb_hack((255,0,0)):
        print('vous etes arrivé, vous avez parcouru un total de',total)
    elif bloc_chemin.itemcget(cases[y//c][x//c],'fill') == rgb_hack((0,255,0)):
        messagebox.showwarning(title='case depart', message='ceci est la case de depart')
    elif bloc_chemin.itemcget(cases[y//c][x//c],'fill') == rgb_hack((255,128,0)):
        messagebox.showwarning(title='case depart', message='vous êtes deja passer par là')
    else:
        bloc_chemin.itemconfigure(cases[y//c][x//c], outline='black', fill=rgb_hack((255,128,0)))
        total+=nombres[x//c][y//c]





fen.bind('<Button-1>', chemin)
fen.bind('<Control-KeyPress-d>',depart)
fen.bind('<Control-KeyPress-f>',fin)

##----- Programme principal -----##
fen.mainloop()                  # Boucle d'attente des événements


#couleur : 15 couleurs (255 : 17 = 15)
#couleur : a = (0 -> 15) (RGB : 0,0, a * 17)

#https://openclassrooms.com/forum/sujet/tkinter-lier-des-labels-avec-un-dictionnaire
