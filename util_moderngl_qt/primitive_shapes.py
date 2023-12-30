"""
generate triangle meshes for primitive shapes to draw thick lines and fat points
"""

import math
#
import numpy

def sphere(
        radius: float = 1.,
        n_longtitude: int = 16,
        n_latitude: int = 32):
    if n_longtitude <= 1 or n_latitude <= 2:
        return
    vtx2xyz = numpy.ndarray(((n_latitude * (n_longtitude - 1) + 2), 3), dtype=numpy.float32)
    pi = math.pi
    dl = pi / n_longtitude
    dr = 2. * pi / n_latitude
    i_cnt = 0
    for ila in range(n_longtitude + 1):
        y0 = math.cos(dl * ila)
        r0 = math.sin(dl * ila)
        for ilo in range(n_latitude):
            x0 = r0 * math.sin(dr * ilo)
            z0 = r0 * math.cos(dr * ilo)
            vtx2xyz[i_cnt] = numpy.array([radius * x0, radius * y0, radius * z0])
            i_cnt += 1
            if ila == 0 or ila == n_longtitude:
                break
    #
    tri2vtx = numpy.ndarray([n_latitude * (n_longtitude - 2) * 2 + n_latitude * 2, 3], dtype=numpy.uint64)
    i_cnt = 0
    for ilo in range(n_latitude):
        tri2vtx[i_cnt] = numpy.array([0, (ilo + 0) % n_latitude + 1, (ilo + 1) % n_latitude + 1])
        i_cnt += 1
    for ila in range(n_longtitude - 2):
        for ilo in range(n_latitude):
            i1 = (ila + 0) * n_latitude + 1 + (ilo + 0) % n_latitude
            i2 = (ila + 0) * n_latitude + 1 + (ilo + 1) % n_latitude
            i3 = (ila + 1) * n_latitude + 1 + (ilo + 1) % n_latitude
            i4 = (ila + 1) * n_latitude + 1 + (ilo + 0) % n_latitude
            tri2vtx[i_cnt] = numpy.array([i3, i2, i1])
            i_cnt += 1
            tri2vtx[i_cnt] = numpy.array([i4, i3, i1])
            i_cnt += 1
    for ilo in range(n_latitude):
        tri2vtx[i_cnt] = numpy.array([
            n_latitude * (n_longtitude - 1) + 1,
            (n_longtitude - 2) * n_latitude + 1 + (ilo + 1) % n_latitude,
            (n_longtitude - 2) * n_latitude + 1 + (ilo + 0) % n_latitude])
        i_cnt += 1
    return tri2vtx, vtx2xyz


def cylinder(
        radius: float = 1.,
        n_theta: int = 16):
    vtx2xyz = numpy.ndarray((n_theta * 2, 3), dtype=numpy.float32)
    dt = math.pi * 2 / n_theta
    i_cnt = 0
    for il in range(2):
        for it in range(n_theta):
            vtx2xyz[i_cnt] = numpy.array([
                math.cos(dt * it),
                math.sin(dt * it),
                il])
            i_cnt += 1
    tri2vtx = numpy.ndarray((n_theta * 2, 3), dtype=numpy.uint64)
    i_cnt = 0
    for il in range(1):
        for it in range(n_theta):
            ip0 = it
            ip1 = (it + 1) % n_theta
            jp0 = ip0 + n_theta
            jp1 = ip1 + n_theta
            tri2vtx[i_cnt] = numpy.array([ip0, ip1, jp1])
            i_cnt += 1
            tri2vtx[i_cnt] = numpy.array([ip0, jp1, jp0])
            i_cnt += 1
    return tri2vtx, vtx2xyz


def cube_wireframe():
    vtx2xyz = [
        [-1, -1, -1],
        [-1, -1, +1],
        [-1, +1, -1],
        [-1, +1, +1],
        [+1, -1, -1],
        [+1, -1, +1],
        [+1, +1, -1],
        [+1, +1, +1]]
    vtx2xyz = numpy.array(vtx2xyz, dtype=numpy.float32)
    edge2vtx = [
        [0, 1],
        [2, 3],
        [1, 3],
        [0, 2],
        [4, 5],
        [6, 7],
        [5, 7],
        [4, 6],
        [0, 4],
        [1, 5],
        [2, 6],
        [3, 7]]
    edge2vtx = numpy.array(edge2vtx, dtype=numpy.uint64)
    return edge2vtx, vtx2xyz