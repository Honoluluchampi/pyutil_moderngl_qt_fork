from pyrr import Matrix44
import moderngl


class DrawerTransformMulti:

    def __init__(self, drawer):
        self.list_transform = []
        self.drawer = drawer

    def init_gl(self, ctx: moderngl.Context):
        self.drawer.init_gl(ctx)

    def paint_gl(self, mvp: Matrix44):
        for transform in self.list_transform:
            self.drawer.paint_gl(mvp * transform)
