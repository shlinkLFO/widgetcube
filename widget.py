import sys
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QMatrix4x4
from OpenGL.GL import *
import numpy as np

class SpinningCubeWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.timer.start(16)  # ~60 FPS

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)

        # Cube vertices
        self.vertices = np.array([
            # Front face
            [-0.5, -0.5,  0.5], [0.5, -0.5,  0.5], [0.5,  0.5,  0.5], [-0.5,  0.5,  0.5],
            # Back face
            [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5,  0.5, -0.5], [-0.5,  0.5, -0.5]
        ], dtype=np.float32)

        # Cube indices
        self.indices = np.array([
            0, 1, 2, 2, 3, 0,  # Front
            1, 5, 6, 6, 2, 1,  # Right
            5, 4, 7, 7, 6, 5,  # Back
            4, 0, 3, 3, 7, 4,  # Left
            3, 2, 6, 6, 7, 3,  # Top
            4, 5, 1, 1, 0, 4   # Bottom
        ], dtype=np.uint32)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        self.projection = QMatrix4x4()
        self.projection.perspective(45, width / height, 0.1, 100.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        modelview = QMatrix4x4()
        modelview.translate(0, 0, -5)
        modelview.rotate(self.angle, 1, 1, 0)

        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(self.projection.data())
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(modelview.data())

        glBegin(GL_TRIANGLES)
        for i in self.indices:
            glColor3f(self.vertices[i][0] + 0.5, 
                     self.vertices[i][1] + 0.5, 
                     self.vertices[i][2] + 0.5)
            glVertex3fv(self.vertices[i])
        glEnd()

    def rotate(self):
        self.angle += 2
        if self.angle >= 360:
            self.angle = 0
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = SpinningCubeWidget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec_())
