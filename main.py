"""Pathfinder d'un point A à un point B en OpenGL."""
import argparse
import pickle
import sys
import threading
from math import comb, pow

from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST,
                       GL_LINES, GL_MODELVIEW, GL_PROJECTION,
                       glBegin, glClear, glClearColor, glColor, glDisable,
                       glEnable, glEnd, glLoadIdentity, glMatrixMode, glOrtho,
                       glRotatef, glTranslatef,
                       glVertex3f, glViewport)
from OpenGL.GLU import gluLookAt, gluPerspective
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
        path[0].x * main_grid.size + main_grid.size / 2,
        path[0].cost,
        path[0].y * main_grid.size + main_grid.size / 2,
    )
    i = 0
    while i < len(path):
        t = 0.002
        while t < 1:
            bezier_path = bezier(path[i : i + k], t)
            glVertex3f(
                bezier_path[0] * main_grid.size + main_grid.size / 2,
                bezier_path[1],
                bezier_path[2] * main_grid.size + main_grid.size / 2,
            )
            glVertex3f(
                bezier_path[0] * main_grid.size + main_grid.size / 2,
                bezier_path[1],
                bezier_path[2] * main_grid.size + main_grid.size / 2,
            )
            t += 0.002
        i += k
    glEnd()


def init():
    """Initialize the OpenGL window."""
    global main_grid
    if main_grid.perspective:
        glEnable(GL_DEPTH_TEST)
    else:
        glDisable(GL_DEPTH_TEST)


def display():
    """Display the OpenGL window."""
    global main_grid
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    if main_grid.perspective:
        x_offset = main_grid.size * (main_grid.width + 2) / 2
        z_offset = main_grid.size * (main_grid.height + 2) / 2
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

        glRotatef(main_grid.phi, 1, 0, 0)
        glRotatef(main_grid.theta, 0, 1, 0)
        glTranslatef(-x_offset, 0, -z_offset)

        # p = maingrid.path()
        # if p:
        # draw_bezier(p)

    main_grid.draw()

    glutSwapBuffers()


def reshape(width, height):
    """Reshape the window and moves the objects inside."""
    global main_grid
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if main_grid.perspective:
        gluPerspective(16, width / height, 200, 10000)
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

if args.input:
    with open(args.input, "rb") as file:
        main_grid = pickle.load(file)
else:
    main_grid = Grid(args.size, args.width, args.height, args.threshold)
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
