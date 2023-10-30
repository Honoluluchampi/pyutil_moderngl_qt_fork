import typing
from pyrr import Matrix44
import numpy
import moderngl


class ElementInfo:

    def __init__(self, index: numpy.ndarray, mode, color):
        self.vao = None
        # index should be numpy.uint32
        if index.dtype == numpy.uint32:
            self.index = index
        else:
            self.index = index.astype(numpy.uint32)
        self.mode = mode
        self.color = color


class DrawerMeshNormal:

    def __init__(self,
                 list_elem2vtx: typing.List[ElementInfo],
                 vtx2xyz: numpy.ndarray,
                 vtx2nrm: numpy.ndarray):
        # coordinate
        assert len(vtx2xyz.shape) == 2
        assert vtx2xyz.shape[1] == 3
        if vtx2xyz.dtype == numpy.float32:
            self.vtx2xyz = vtx2xyz
        else:
            self.vtx2xyz = vtx2xyz.astype(numpy.float32)
        # uv coordinate
        assert len(vtx2nrm.shape) == 2
        assert vtx2nrm.shape[0] == vtx2xyz.shape[0]
        assert vtx2nrm.shape[1] == 3
        if vtx2nrm.dtype == numpy.float32:
            self.vtx2nrm = vtx2nrm
        else:
            self.vtx2nrm = vtx2nrm.astype(numpy.float32)
        self.list_elem2vtx = list_elem2vtx
        self.vao_content = None

    def init_gl(self, ctx: moderngl.Context):
        self.prog = ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 Mvp;
                in vec3 in_nrm;
                in vec3 in_xyz;
                out vec3 out_nrm;
                void main() {
                    out_nrm = normalize((Mvp * vec4(in_nrm, 0.0)).xyz);
                    gl_Position = Mvp * vec4(in_xyz, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform vec3 color;
                in vec3 out_nrm;
                out vec4 f_color;                
                void main() { 
                    float ratio = abs(out_nrm.z); 
                    ratio = 1-(1-ratio)*(1-ratio)*(1-ratio)*(1-ratio);
                    f_color = vec4(color*ratio, 1.0);
                }
            '''
        )

        self.vao_content = [
            (ctx.buffer(self.vtx2xyz.tobytes()), '3f', 'in_xyz'),
            (ctx.buffer(self.vtx2nrm.tobytes()), '3f', 'in_nrm')
        ]
        del self.vtx2xyz
        del self.vtx2nrm
        for el in self.list_elem2vtx:
            index_buffer = ctx.buffer(el.index.tobytes())
            el.vao = ctx.vertex_array(
                self.prog, self.vao_content, index_buffer, 4
            )
            del el.index

    def update_position(self, vtx2xyz: numpy.ndarray):
        if vtx2xyz.dtype != numpy.float32:
            vtx2xyz = vtx2xyz.astype(numpy.float32)
        if self.vao_content != None:
            vbo = self.vao_content[0][0]
            vbo.write(vtx2xyz.tobytes())

    def paint_gl(self, mvp: Matrix44):
        self.prog['Mvp'].value = tuple(mvp.flatten())
        for el in self.list_elem2vtx:
            self.prog['color'] = el.color
            el.vao.render(mode=el.mode)
