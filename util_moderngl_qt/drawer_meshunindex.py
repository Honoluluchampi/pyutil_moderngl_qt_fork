import typing
from pyrr import Matrix44
import numpy
import moderngl


class DrawerMeshUnindex:

    def __init__(self, tri2vtx2xyz: numpy.ndarray):
        if tri2vtx2xyz.dtype == numpy.float32:
            self.tri2vtx2xyz = tri2vtx2xyz
        else:
            self.tri2vtx2xyz = tri2vtx2xyz.astype(numpy.float32)
        self.tri2color = numpy.ones([tri2vtx2xyz.shape[0]*9], dtype=numpy.float32)
        self.vao_content = None
        self.num_point = tri2vtx2xyz.size // 3

    def init_gl(self, ctx: moderngl.Context):
        self.prog = ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 Mvp;
                layout (location=0) in vec3 in_position;
                layout (location=1) in vec3 in_color;
                out vec3 color;
                void main() {
                    color = in_color; 
                    gl_Position = Mvp * vec4(in_position, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                in vec3 color;
                out vec4 f_color;
                void main() {
                    f_color = vec4(color, 1.0);
                }
            '''
        )
        self.uniform_mvp = self.prog['Mvp']

        self.vao_content = [
            (ctx.buffer(self.tri2vtx2xyz.tobytes()), '3f', 'in_position'),
            (ctx.buffer(self.tri2color.tobytes()), '3f', 'in_color')
        ]
        del self.tri2vtx2xyz
        self.vao = ctx.vertex_array(self.prog, self.vao_content)

    def update_color(self, V: numpy.ndarray):
        if self.vao_content is not None:
            vbo = self.vao_content[1][0]
            vbo.write(V.tobytes())

    def paint_gl(self, mvp: Matrix44):
        self.uniform_mvp.value = tuple(mvp.flatten())
        self.vao.render(mode=moderngl.TRIANGLES, vertices=self.num_point)
