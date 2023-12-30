
from pyrr import Matrix44
import moderngl

class Drawer:
    def __init__(
            self,
             mvp: Matrix44):
        self.mvp_inv = mvp.inverse.copy()
        from .primitive_shapes import cube_wireframe
        edge2vtx, vtx2xyz = cube_wireframe()
        from .DrawerMesh import Drawer, ElementInfo
        self.drawer = Drawer(
            vtx2xyz,
            list_elem2vtx=[ElementInfo(edge2vtx, moderngl.LINES, (0., 0., 0. ))])

    def init_gl(
            self,
            ctx: moderngl.Context):
        self.drawer.init_gl(ctx)

    def paint_gl(self, mvp: Matrix44):
        self.drawer.paint_gl(mvp*self.mvp_inv)