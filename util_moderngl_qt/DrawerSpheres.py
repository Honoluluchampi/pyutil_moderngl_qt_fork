import typing
import numpy
import moderngl
from pyrr import Matrix44


class SphereInfo:
    def __init__(
            self,
            rad: float = 1.,
            pos=numpy.array([0., 0., 0.]),
            color=(1., 1., 1.)):
        self.rad = rad
        self.pos = pos
        self.color = color


class Drawer:
    def __init__(self):
        from .primitive_shapes import sphere
        tri2vtx, vtx2xyz = sphere()
        self.list_sphere: typing.List[SphereInfo] = []
        from .DrawerMesh import Drawer, ElementInfo
        self.drawer = Drawer(
            vtx2xyz=vtx2xyz,
            list_elem2vtx=[
                ElementInfo(index=tri2vtx, color=(1., 0., 0.), mode=moderngl.TRIANGLES)])

    def init_gl(self, ctx: moderngl.Context):
        self.drawer.init_gl(ctx)

    def paint_gl(self, mvp: Matrix44):
        for sphere in self.list_sphere:
            mt = Matrix44.from_translation(sphere.pos)
            ms = Matrix44.from_scale((sphere.rad, sphere.rad, sphere.rad))
            transform = mt * ms
            self.drawer.list_elem2vtx[0].color = sphere.color
            self.drawer.paint_gl(mvp * transform)
