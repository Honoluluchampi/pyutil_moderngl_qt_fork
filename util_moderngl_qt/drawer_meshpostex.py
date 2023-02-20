import typing
from pyrr import Matrix44
import numpy
import moderngl

class ElementInfo:

    def __init__(self, index, mode, color):
        self.vao = None
        self.index = index
        self.mode = mode
        self.color = color

class DrawerMesPosTex:

    def __init__(self,
                 list_elem2vtx: typing.List[ElementInfo],
                 vtx2xyz: numpy.ndarray,
                 vtx2uv: numpy.ndarray):
        self.vtx2xyz = vtx2xyz
        self.vtx2uv = vtx2uv
        self.list_elem2vtx = list_elem2vtx
        self.vao_content = None

    def init_gl(self, ctx: moderngl.Context):
        self.prog = ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 Mvp;
                in vec2 in_uv;
                in vec3 in_xyz;
                out vec2 texPrj;
                void main() {
                    gl_Position = Mvp * vec4(in_xyz, 1.0);
                    texPrj = in_uv;
                }
            ''',
            fragment_shader='''
                #version 330
                uniform sampler2D myTextureSampler;
                uniform vec3 color;
                uniform bool is_texture;
                out vec4 f_color;
                in vec2 texPrj;
                void main() {
                    if( is_texture ) {                 
                        f_color = texture(myTextureSampler,texPrj);
                    }
                    else { 
                        f_color = vec4(color, 1.0);
                    }
                }
            '''
        )
        self.uniform_mvp = self.prog['Mvp']
        self.uniform_texture_location = self.prog['myTextureSampler']
        self.uniform_is_texture = self.prog['is_texture']
        self.uniform_color = self.prog['color']

        self.vao_content = [
            (ctx.buffer(self.vtx2xyz.tobytes()), '3f', 'in_xyz'),
            (ctx.buffer(self.vtx2uv.tobytes()), '2f', 'in_uv')
        ]
        del self.vtx2xyz
        del self.vtx2uv
        for el in self.list_elem2vtx:
            index_buffer = ctx.buffer(el.index.tobytes())
            el.vao = ctx.vertex_array(
                self.prog, self.vao_content, index_buffer, 4
            )
            del el.index

    def update_position(self, vtx2xyz: numpy.ndarray):
        if self.vao_content != None:
            vbo = self.vao_content[0][0]
            vbo.write(vtx2xyz.tobytes())

    def paint_gl(self, mvp: Matrix44, texture_location: int):
        self.uniform_mvp.value = tuple(mvp.flatten())
        self.uniform_texture_location.value = texture_location
        for el in self.list_elem2vtx:
            if el.color is None:
                self.uniform_is_texture.value = True
            else:
                self.uniform_is_texture.value = False
            el.vao.render(mode=el.mode)