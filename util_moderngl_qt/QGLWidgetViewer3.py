import math
import typing
#
import moderngl
import pyrr
import numpy
from PyQt5 import QtOpenGL, QtGui, QtCore
#
import util_moderngl_qt.view_navigation3


class QtGLWidget_Viewer3(QtOpenGL.QGLWidget):

    def __init__(
            self,
            list_drawer:typing.Optional[typing.List] = None,
            parent=None):
        self.ctx = None
        if list_drawer is None:
            list_drawer = []
        self.parent = parent
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super(QtGLWidget_Viewer3, self).__init__(fmt, None)
        #
        self.nav = util_moderngl_qt.view_navigation3.ViewNavigation3()
        self.resize(640, 480)
        self.setWindowTitle('Mesh Viewer')
        self.list_drawer = list_drawer
        self.mousePressCallBack = []
        self.mouseReleaseCallBack = []
        self.mouseMoveCallBack = []
        self.mouseDoubleClickCallBack = []
        self.viewTransformationChangeCallCack = []

    def initializeGL(self):
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        for drawer in self.list_drawer:
            drawer.init_gl(self.ctx)

    def view_transformation_matrix_for_gl(self):
        proj = self.nav.projection_matrix()
        modelview = self.nav.modelview_matrix()
        zinv = pyrr.Matrix44(value=(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1), dtype=numpy.float32)
        return zinv * proj * modelview

    def paintGL(self):
        self.ctx.fbo.use()
        self.ctx.clear(1.0, 0.8, 1.0)
        self.ctx.polygon_offset = 1.1, 4.0
        mvp = self.view_transformation_matrix_for_gl()
        for drawer in self.list_drawer:
            drawer.paint_gl(mvp)

    def resizeGL(self, width, height):
        width = max(2, width)
        height = max(2, height)
        self.ctx.viewport = (0, 0, width, height)
        self.nav.win_height = self.height()
        self.nav.win_width = self.width()

    def mousePressEvent(self, event):
        self.nav.update_cursor_position(event.pos().x(), event.pos().y())
        if event.buttons() & QtCore.Qt.LeftButton:
            self.nav.btn_left = True
        for cb in self.mousePressCallBack:
            cb(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        self.nav.update_cursor_position(event.pos().x(), event.pos().y())
        if event.buttons() & QtCore.Qt.LeftButton:
            self.nav.btn_left = True
        for cb in self.mouseDoubleClickCallBack:
            cb(event)

    def mouseReleaseEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.nav.btn_left = False
        for cb in self.mouseReleaseCallBack:
            cb(event)

    def mouseMoveEvent(self, event):
        self.nav.update_cursor_position(event.pos().x(), event.pos().y())
        if event.buttons() & QtCore.Qt.LeftButton:
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
                self.nav.camera_translation()
                self.update()
                for cb in self.viewTransformationChangeCallCack:
                    cb(event)
            if event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier:
                self.nav.camera_rotation()
                self.update()
                for cb in self.viewTransformationChangeCallCack:
                    cb(event)
        for cb in self.mouseMoveCallBack:
            cb(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        dy = event.pixelDelta().y()
        self.nav.scale *= math.pow(1.01, dy)
        self.update()
        for cb in self.viewTransformationChangeCallCack:
            cb(event)
