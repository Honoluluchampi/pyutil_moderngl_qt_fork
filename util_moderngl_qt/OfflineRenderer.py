import typing
#
import moderngl
import numpy


class OfflineRenderer:

    def __init__(
            self,
            width_height: typing.Tuple[int, int]):
        self.ctx = moderngl.create_context(standalone=True)
        self.ctx.polygon_offset = 1.1, 4.0
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.fbo = self.ctx.simple_framebuffer(width_height)

    def start(self):
        self.fbo.use()
        self.fbo.clear(0.0, 0.0, 1.0, 1.0)

    def get_rgb(self):
        rgb = numpy.frombuffer(self.fbo.read(), dtype=numpy.uint8)
        rgb = rgb.reshape((self.fbo.size[1], self.fbo.size[0], 3)).copy()
        return rgb

    def get_depth(self):
        depth = self.fbo.read(attachment=-1, dtype='f4')
        depth = numpy.frombuffer(depth, dtype=numpy.float32)
        depth = depth.reshape((3, self.fbo.size[1], self.fbo.size[0]))
        depth = depth.transpose(1, 2, 0)[:, :, 0].copy()
        return depth
