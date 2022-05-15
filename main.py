"""Pathfinder d'un point A à un point B en OpenGL."""
import argparse
import pickle
import sys
import threading
from enum import Enum
from itertools import chain, product
from math import comb, cos, inf, pi, pow, sin, sqrt
from random import randrange
from time import sleep

from OpenGL.GL import (GL_AMBIENT, GL_AMBIENT_AND_DIFFUSE, GL_BACK,
                       GL_COLOR_BUFFER_BIT, GL_COLOR_MATERIAL,
                       GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_DIFFUSE, GL_FLAT,
                       GL_FRONT, GL_FRONT_AND_BACK, GL_LIGHT0, GL_LIGHTING,
                       GL_LINES, GL_MODELVIEW, GL_POSITION, GL_PROJECTION,
                       GL_QUADS, GL_SHININESS, GL_TRIANGLES, glBegin, glClear,
                       glClearColor, glColor, glDisable, glEnable, glEnd,
                       glLight, glLoadIdentity, glMaterial, glMatrixMode,
                       glNormal3f, glOrtho, glPopMatrix, glPushMatrix,
                       glRotatef, glShadeModel, glTranslatef,
                       glVertex3f, glViewport)
from OpenGL.GLU import (GLU_FLAT, GLU_SMOOTH, gluLookAt, gluNewQuadric,
                        gluPerspective, gluQuadricDrawStyle, gluSphere)
from OpenGL.GLUT import (GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGBA,
                         GLUT_WINDOW_HEIGHT, GLUT_WINDOW_WIDTH,
                         glutCreateWindow, glutDestroyWindow, glutDisplayFunc,
                         glutGet, glutGetWindow, glutIdleFunc, glutInit,
                         glutInitDisplayMode, glutKeyboardFunc, glutMainLoop,
                         glutMouseFunc, glutPostRedisplay, glutReshapeFunc,
                         glutReshapeWindow, glutSwapBuffers)

from misc import HEIGHT
from grid import Grid


def bezier(p, t):
    """Return the point at length t from the Bézier curve of control tiles p."""
    x = 0
    y = 0
    z = 0
    i = 0
    while i < len(p):
        x += p[i].x * pow(t, i) * pow(1 - t, len(p) - 1 - i) * comb(len(p) - 1, i)
        y += p[i].cost * pow(t, i) * pow(1 - t, len(p) - 1 - i) * comb(len(p) - 1, i)
        z += p[i].y * pow(t, i) * pow(1 - t, len(p) - 1 - i) * comb(len(p) - 1, i)
        i += 1
    return (x, y, z)



def draw_bezier(path, k=4):
    """Draw in OpenGL the Bézier curves with k control points from the points path."""
    glBegin(GL_LINES)
    glColor(1, 1, 1, 1)
    glVertex3f(
        path[0].x * main_grid.size * 2 + main_grid.size / 2,
        path[0].cost,
        path[0].y * main_grid.size * 2 + main_grid.size / 2,
    )
    i = 0
    while i < len(path):
        t = 0.002
        while t < 1:
            bezier_path = bezier(path[i : i + k], t)
            glVertex3f(
                bezier_path[0] * main_grid.size * 2 + main_grid.size / 2,
                bezier_path[1],
                bezier_path[2] * main_grid.size * 2 + main_grid.size / 2,
            )
            glVertex3f(
                bezier_path[0] * main_grid.size * 2 + main_grid.size / 2,
                bezier_path[1],
                bezier_path[2] * main_grid.size * 2 + main_grid.size / 2,
            )
            t += 0.002
        i += k
    glEnd()


class Worm:
    """A little worm to travel the earth."""

    def __init__(self, radius):
        """Initialize the worm."""
        self.x = 0
        self.y = 0
        self.z = 0
        self.radius = radius

    def draw(self, size, quadric):
        """Draws the worm."""
        glColor(1, 1, 0)
        glTranslatef(
            size * self.x + size / 4, self.y + self.radius, size * self.z + size / 4
        )
        gluSphere(quadric, self.radius, 20, 16)

    def follow_bezier(self, path, k=4):
        self.x = path[0].x
        self.y = path[0].cost
        self.z = path[0].y
        i = 0
        while i < len(path):
            t = 0.002
            while t < 1:
                bezier_path = bezier(path[i : i + k + 1], t)
                self.x = bezier_path[0]
                self.y = bezier_path[1]
                self.z = bezier_path[2]
                sleep(0.005)
                t += 0.002
            i += k

def init():
    """Initialize the OpenGL window."""
    global main_grid
    if main_grid.perspective:
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
    else:
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_FLAT)


def display():
    """Display the OpenGL window."""
    global main_grid
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    if main_grid.perspective:
        gluLookAt(
            0,
            0,
            main_grid.zoom,
            0,
            0,
            0,
            0,
            1,
            0,
        )
        glNormal3f(
            cos(main_grid.theta / 360 * pi * 2), 1, sin(main_grid.theta / 360 * pi * 2)
        )
        glTranslatef(0, 0, main_grid.size * main_grid.worm.z * 2)
        glRotatef(main_grid.phi, 1, 0, 0)
        glRotatef(main_grid.theta, 0, 1, 0)
        glTranslatef(
            -main_grid.size * main_grid.worm.x * 2 - main_grid.size / 2,
            -main_grid.worm.y - main_grid.worm.radius,
            -main_grid.size * main_grid.worm.z * 2 - main_grid.size / 2,
        )

    # glPushMatrix()
    main_grid.draw()
    # glPopMatrix()
    if main_grid.perspective and main_grid.start:
        # glPushMatrix()
        # grid.worm.x = grid.dep.x
        # grid.worm.y = grid.dep.cost
        # grid.worm.z = grid.dep.y
        main_grid.worm.draw(main_grid.size * 2, quadric)
        # glPopMatrix()

    glTranslatef(
        -main_grid.size * main_grid.worm.x * 2 - main_grid.size / 2,
        -main_grid.worm.y - main_grid.worm.radius,
        # -grid.worm.radius,
        -main_grid.size * main_grid.worm.z * 2 - main_grid.size / 2,
    )
    glutSwapBuffers()


def reshape(width, height):
    """Reshape the window and moves the objects inside."""
    global main_grid
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if main_grid.perspective:
        gluPerspective(16, width / height, 200, 20000)
    else:
        glOrtho(0, width, height, 0, 20, 0)
    glMatrixMode(GL_MODELVIEW)


def keyboard(key, x, y):
    """React upon keyboard input."""
    global main_grid

    if key == b"\r":
        main_grid.perspective = not main_grid.perspective
        init()
        reshape(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
        if main_grid.perspective:
            draw = threading.Thread(target=main_grid.drawpath, daemon=True,
                                    args=(args.algorithm,))
            draw.start()
            pass
        else:
            main_grid.reset()

    if main_grid.perspective:
        if key == b"z":
            main_grid.zoom -= 10
        elif key == b"x":
            main_grid.zoom += 10
        elif key == b"w":
            main_grid.phi = (main_grid.phi + 2) % 360
        elif key == b"s":
            main_grid.phi = (main_grid.phi - 2) % 360
        elif key == b"a":
            main_grid.theta = (main_grid.theta - 2) % 360
        elif key == b"d":
            main_grid.theta = (main_grid.theta + 2) % 360

    else:
        if key == b"1":
            main_grid.threshold -= HEIGHT * 0.01
            main_grid.generate(args.smoothing)
        elif key == b"2":
            main_grid.threshold += HEIGHT * 0.01
            main_grid.generate(args.smoothing)
        elif key == b"r":
            main_grid.generate(args.smoothing)
        elif key == b"S":
            with open(args.output, "wb") as file:
                pickle.dump(main_grid, file)

    if key == b"q":
        glutDestroyWindow(glutGetWindow())

    if key != b"q":
        glutPostRedisplay()

    print(key, main_grid.theta, main_grid.phi, main_grid.zoom)


def mouse(button, state, x, y):
    """React upon mouse clicks."""
    global main_grid
    if state:
        main_grid.clic_tile(x, y)
    if button == 3:
        main_grid.zoom -= 30
    if button == 4:
        main_grid.zoom += 30
    glutPostRedisplay()


parser = argparse.ArgumentParser(description="Pathfinder codé entièrement en OpenGL.")
parser.add_argument("--algorithm", "-a", type=str, default="astar")
parser.add_argument("--output", "-o", type=str, default="terrain.pickle")
parser.add_argument("--input", "-i", type=str)
parser.add_argument("--threshold", "-t", type=int, default=50)
parser.add_argument("--size", "-s", type=int, default=32)
parser.add_argument("--width", "-W", type=int, default=38)
parser.add_argument("--height", "-H", type=int, default=29)
parser.add_argument("--smoothing", "-S", type=int, default=2)
args = parser.parse_args()

quadric = gluNewQuadric()
gluQuadricDrawStyle(quadric, GLU_FLAT)

if args.input:
    with open(args.input, "rb") as file:
        main_grid = pickle.load(file)
else:
    worm = Worm(20)
    main_grid = Grid(args.size, args.width, args.height, args.threshold, worm)
    main_grid.generate(args.smoothing)

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
