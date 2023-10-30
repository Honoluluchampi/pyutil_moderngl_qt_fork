import typing
from pyrr import Matrix44
import numpy
import moderngl


class ElementInfo:

    def __init__(self, index: numpy.ndarray, mode, color: typing.Optional[tuple]):
        self.vao = None
        # index should be numpy.uint32
        if index.dtype == numpy.uint32:
            self.index = index
        else:
            self.index = index.astype(numpy.uint32)
        self.mode = mode
        self.color = color


class Drawer:

    def __init__(self,
                 vtx2xyz: numpy.ndarray,
                 list_elem2vtx: typing.List[ElementInfo],
                 vtx2val: numpy.ndarray,
                 color_map: numpy.ndarray):
        assert len(vtx2xyz.shape) == 2
        assert len(vtx2val.shape) == 1
        if vtx2xyz.dtype == numpy.float32:
            self.vtx2xyz = vtx2xyz
        else:
            self.vtx2xyz = vtx2xyz.astype(numpy.float32)
        #
        if vtx2val.dtype == numpy.float32:
            self.vtx2val = vtx2val
        else:
            self.vtx2val = vtx2val.astype(numpy.float32)
        #
        self.list_elem2vtx = list_elem2vtx
        self.color_map = color_map
        self.vao_content = None

    def init_gl(self, ctx: moderngl.Context):
        vertex_shader = '''
            #version 330
            uniform mat4 Mvp;
            layout (location = 0) in vec3 in_position;
            layout (location = 1) in float in_value;
            out float val;
            void main() {
                gl_Position = Mvp * vec4(in_position, 1.0);
                val = in_value;
            }
        '''
        fragment_shader_head = '''
            #version 330     
        '''

        fragment_shader_colormap = f'''
            const int ncolor = {self.color_map.shape[0]};
            vec3[ncolor] colors = vec3[] (
        '''
        for ic in range(self.color_map.shape[0]):
            r = self.color_map[ic][0]
            g = self.color_map[ic][1]
            b = self.color_map[ic][2]
            fragment_shader_colormap \
                = str(fragment_shader_colormap) \
                  + str(f"vec3({r}, {g}, {b})")
            if ic != self.color_map.shape[0] - 1:
                fragment_shader_colormap += ',\n'
            else:
                fragment_shader_colormap += ');\n'

        fragment_shader_body = '''
            uniform float valmin;
            uniform float valmax;
            in float val;            
            out vec4 f_color;
            void main() {
                float scaled_value = (val-valmin)/(valmax-valmin) * (ncolor-1);
                int idx_color = int(scaled_value);
                float r01 = scaled_value - float(idx_color);
                if( idx_color < 0 ){ idx_color = 0; r01 = 0.;}
                if( idx_color > ncolor-2 ){ idx_color = ncolor-2; r01 = 1.; }
                vec3 clr01 = (1.f-r01)*colors[idx_color] + r01*colors[idx_color+1];            
                f_color = vec4(clr01, 1.0);
            }
        '''
        self.prog = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader_head
                            + fragment_shader_colormap
                            + fragment_shader_body
        )
        self.vao_content = [
            (ctx.buffer(self.vtx2xyz.tobytes()), f'{self.vtx2xyz.shape[1]}f', 'in_position'),
            (ctx.buffer(self.vtx2val.tobytes()), '1f', 'in_value'),
        ]
        del self.vtx2xyz
        del self.vtx2val
        for el in self.list_elem2vtx:
            index_buffer = ctx.buffer(el.index.tobytes())
            el.vao = ctx.vertex_array(
                self.prog, self.vao_content, index_buffer, 4
            )
            del el.index

    def update_position(self, V: numpy.ndarray):
        if self.vao_content != None:
            vbo = self.vao_content[0][0]
            vbo.write(V.tobytes())

    def update_value(self, V: numpy.ndarray):
        if self.vao_content != None:
            vbo = self.vao_content[1][0]
            vbo.write(V.tobytes())

    def paint_gl(self, mvp: Matrix44):
        self.prog['Mvp'].value = tuple(mvp.flatten())
        self.prog['valmin'].value = 0.
        self.prog['valmax'].value = 1.
        for el in self.list_elem2vtx:
            el.vao.render(mode=el.mode)
