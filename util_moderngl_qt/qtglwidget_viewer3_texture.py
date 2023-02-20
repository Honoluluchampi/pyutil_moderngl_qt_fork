import math
import pyrr
import moderngl
import numpy
from PyQt5 import QtOpenGL, QtWidgets, QtCore, QtGui

import util_moderngl_qt.qtglwidget_viewer3

class QtGLWidget_Viewer3_Texture(QtOpenGL.QGLWidget):

    def __init__(self, drawer, img: numpy.ndarray, parent=None):
        self.parent = parent
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super(QtGLWidget_Viewer3_Texture, self).__init__(fmt, None)
        #
        self.nav = util_moderngl_qt.view_navigation3.ViewNavigation3()
        self.resize(640, 480)
        self.setWindowTitle('Mesh Viewer')
        self.drawer = drawer
        self.img = img
        self.mousePressCallBack = []
        self.mouseMoveCallBack = []

    def initializeGL(self):
        self.ctx = moderngl.create_context()
        self.drawer.init_gl(self.ctx)
        img2 = numpy.flip(self.img, axis=0)  # flip upside down
        self.texture = self.ctx.texture((img2.shape[0], img2.shape[1]), img2.shape[2], img2.tobytes())
        del self.img

    def paintGL(self):
        self.ctx.clear(0.9, 0.8, 1.0)
        self.ctx.enable(moderngl.DEPTH_TEST)
        proj = self.nav.projection_matrix()
        modelview = self.nav.modelview_matrix()
        zinv = pyrr.Matrix44(value=(1,0,0,0, 0,1,0,0, 0,0,-1,0, 0,0,0,1),dtype=numpy.float32)
        mvp = zinv * proj * modelview
        self.texture.use(location=0)
        self.drawer.paint_gl(mvp,0)

    def resizeGL(self, width, height):
        width = max(2, width)
        height = max(2, height)
        self.ctx.viewport = (0, 0, width, height)

    def mousePressEvent(self, event):
        self.nav.update_cursor_position(event.pos().x(), event.pos().y())
        if event.buttons() & QtCore.Qt.LeftButton:
            self.nav.btn_left = True
        for cb in self.mousePressCallBack:
            cb(event)

    def mouseReleaseEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.nav.btn_left = False

    def mouseMoveEvent(self, event):
        self.nav.update_cursor_position(event.pos().x(), event.pos().y())
        if event.buttons() & QtCore.Qt.LeftButton:
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
                self.nav.camera_translation()
                self.update()
            if event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier:
                self.nav.camera_rotation()
                self.update()
        for cb in self.mouseMoveCallBack:
            cb(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        dy = event.pixelDelta().y()
        self.nav.scale *= math.pow(1.01, dy)
        self.update()