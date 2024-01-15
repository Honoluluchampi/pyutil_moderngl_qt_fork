import numpy
import moderngl
from pyrr import Matrix44


class Drawer:
    def __init__(
            self,
            depth: numpy.ndarray,
            mvp: Matrix44, color=(1., 0., 0.)):
        self.prog = None
        self.vao = None
        self.vao_content = None
        self.uniform_mvp = None
        self.uniform_color = None
        self.mvpinv = mvp.inverse
        self.depth = None
        self.update_depth(depth)
        self.color = color

    def update_depth(self, depth_image):
        nx = depth_image.shape[1]
        ny = depth_image.shape[0]
        self.depth = numpy.ndarray((ny, nx, 3), numpy.float32)
        for ih in range(0, ny):
            self.depth[ih, :, 0] = 2.0 * (numpy.linspace(0, nx - 1, nx) + 0.5) / float(nx) - 1.
            self.depth[ih, :, 1] = 2.0 * (float(ih) + 0.5) / ny - 1.
        self.depth[:, :, 2] = depth_image[:, :] * 2. - 1.
        self.depth = self.depth.reshape((-1, 3))
        if self.vao_content is not None:
            vbo = self.vao_content[0][0]
            vbo.write(self.depth.tobytes())

    def init_gl(self, ctx: moderngl.Context):
        self.prog = ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 Mvp;
                layout (location=0) in vec3 in_position;
                out vec3 color;
                void main() {
                    gl_Position = Mvp * vec4(in_position, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform vec3 color;
                out vec4 f_color;
                void main() {
                    f_color = vec4(color, 1.0);
                }
            '''
        )
        self.uniform_mvp = self.prog['Mvp']
        self.uniform_color = self.prog['color']

        self.vao_content = [
            (ctx.buffer(self.depth.tobytes()), f'{self.depth.shape[1]}f', 'in_position'),
        ]
        # del self.elem2node2xyz
        # del self.elem2node2color
        self.vao = ctx.vertex_array(self.prog, self.vao_content)

    def paint_gl(self, mvp: Matrix44):
        self.uniform_mvp.value = tuple((mvp * self.mvpinv).flatten())
        self.uniform_color.value = self.color
        self.vao.render(mode=moderngl.POINTS, vertices=self.depth.shape[0])
