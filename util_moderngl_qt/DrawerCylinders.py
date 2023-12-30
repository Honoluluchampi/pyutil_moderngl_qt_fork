import typing
import numpy
import moderngl
import pyrr
from pyrr import Matrix44


def minimum_rotation(uz, u01):
    n = numpy.cross(uz, u01)
    st = numpy.sqrt(n.dot(n))
    ct = uz.dot(u01)
    theta = numpy.arctan2(st, ct)
    n = n / numpy.linalg.norm(n)
    # print(st, ct)
    q = pyrr.Quaternion.from_axis(n * theta)
    return q.matrix44

class CylinderInfo:
    def __init__(
            self,
            pos0=numpy.array([0., 0., 0.]),
            pos1=numpy.array([0., 0., 0.]),
            color=None):
        self.pos0 = pos0
        self.pos1 = pos1
        self.color = color


class Drawer:
    def __init__(self):
        from .primitive_shapes import cylinder
        tri2vtx, vtx2xyz = cylinder()
        self.list_cylinder: typing.List[CylinderInfo] = []
        self.rad = 1.0
        self.color = (1., 0., 0.)
        from .DrawerMesh import Drawer, ElementInfo
        self.drawer = Drawer(
            vtx2xyz=vtx2xyz,
            list_elem2vtx=[
                ElementInfo(index=tri2vtx, color=(1., 0., 0.), mode=moderngl.TRIANGLES)])

    def init_gl(self, ctx: moderngl.Context):
        self.drawer.init_gl(ctx)

    def paint_gl(self, mvp: Matrix44):
        for cylinder in self.list_cylinder:
            p0 = cylinder.pos0
            p1 = cylinder.pos1
            u01 = (p1 - p0) / numpy.linalg.norm(p1 - p0)
            uz = numpy.array([0., 0., 1.])
            mr = minimum_rotation(uz, u01)
            mt = Matrix44.from_translation(p0)
            ms = Matrix44.from_scale((self.rad, self.rad, numpy.linalg.norm(p0-p1)))
            transform = mt * mr.transpose() * ms
            if cylinder.color is None:
                self.drawer.list_elem2vtx[0].color = self.color
            else:
                self.drawer.list_elem2vtx[0].color = cylinder.color
            self.drawer.paint_gl(mvp * transform)