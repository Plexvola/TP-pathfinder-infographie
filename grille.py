from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from random import randrange

window = 0                                             # glut window number
width, height = 1100, 750                               # window size

def rgb_hack(rgb):
    """Transforme un nombre en sa représentation RGB."""
    return "#%02x%02x%02x" % rgb

def draw():
    x1 = 10
    x2 = 10                                    # ondraw is called all the time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the screen
    refresh2d(width, height)                           # set mode to 2d
    for i in range(7):
        for j in range(7):
            a = randrange(1, 17)
            glColor3f(1,0.058*a,1)
            draw_rect(x1, x2, 50, 50)                        # rect at (10, 10) with width 200, height 100
            x1 += 60
        x1 = 10
        x2 += 60

    glutSwapBuffers()                                # important for double buffering


def draw_rect(x, y, width, height):
    glBegin(GL_QUADS)                                  # start drawing a rectangle
    glVertex2f(x, y)                                   # bottom left point
    glVertex2f(x + width, y)                           # bottom right point
    glVertex2f(x + width, y + height)                  # top right point
    glVertex2f(x, y + height)                          # top left point
    glEnd()                                            # done drawing a rectangle

def refresh2d(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, width, 0.0, height, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

# initialization
glutInit()                                             # initialize glut
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
glutInitWindowSize(width, height)                      # set window size
glutInitWindowPosition(0, 0)                           # set window position
window = glutCreateWindow("terrain")              # create window with title
glutDisplayFunc(draw)                                  # set draw function callback
glutIdleFunc(draw)                                     # draw all the time
glutMainLoop()                                         # start everything
