#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 20:43:14 2018

@author: armand
"""

import numpy as np

class Point:
    
    def __init__(self, space, x, y, z):
        self._space = space
        self._x = x
        self._y = y
        self._z = z
        self._virtualx = x
        self._virtualy = y
        self._virtualz = z
        self._projectedx = 0
        self._projectedy = 0
        self._depth = 0
        self.update()
        self._space.points.append(self)
        
    def __str__(self):
        return 'True: ' + str((self._x, self._y, self._z)) + ' Virtual: ' + str((self._virtualx, self._virtualy, self._virtualz)) + ' Projected: ' + str((self._projectedx, self._projectedy))
    
    def _get_xyz_true(self):
        return (self._x, self._y, self._z)
    def _set_xyz_true(self, c):
        self._x, self._y, self._z = c
        self.update()
    xyzTrue = property(_get_xyz_true, _set_xyz_true)
    
    def _get_xyz_virtual(self):
        return (self._virtualx, self._virtualy, self._virtualz)
    xyzVirtual = property(_get_xyz_virtual)
    
    def _get_xy_projected(self):
        return (self._projectedx, self._projectedy)
    xyProjected = property(_get_xy_projected)
    
    def _get_depth(self):
        return self._depth
    depth = property(_get_depth)
    
    def update(self):
        #the three rotation matrices multiplication
        self._virtualx = self._space.cy*(self._space.sz*self._y + self._space.cz*self._x) - self._space.sy*self._z
        self._virtualy = self._space.sx*(self._space.cy*self._z + self._space.sy*(self._space.sz*self._y + self._space.cz*self._x)) + self._space.cx*(self._space.cz*self._y - self._space.sz*self._x)
        self._virtualz = self._space.cx*(self._space.cy*self._z + self._space.sy*(self._space.sz*self._y + self._space.cz*self._x)) - self._space.sx*(self._space.cz*self._y - self._space.sz*self._x)
        
        #projection in the 2D plane
        axes = self._space.axes
        origin = self._space.origin
        self._projectedx = self._virtualx*axes[0][0] + self._virtualy*axes[1][0] + self._virtualz*axes[2][0] + origin[0]
        self._projectedy = self._virtualx*axes[0][1] + self._virtualy*axes[1][1] + self._virtualz*axes[2][1] + origin[1]
        self._projectedx = int(self._projectedx)
        self._projectedy = int(self._projectedy)
        
        #depth. Higher values are "behind" lower values
        self._depth = self._virtualx*axes[0][2] + self._virtualy*axes[1][2] + self._virtualz*axes[2][2]

class Space:
    
    def __init__(self):
        #default values: isometric projection centered in a 640x480 plane
        l = 20
        self._xAxis = (l*np.sqrt(1/2), l*np.sqrt(1/6), l*np.sqrt(1/3))
        self._yAxis = (0.0, l*np.sqrt(2/3), -l*np.sqrt(1/3))
        self._zAxis = (-l*np.sqrt(1/2), l*np.sqrt(1/6), l*np.sqrt(1/3))
        self._originx = 320
        self._originy = 240
        self._anglex = 0
        self._angley = 0
        self._anglez = 0
        self._cx, self._sx = 1,0
        self._cy, self._sy = 1,0
        self._cz, self._sz = 1,0
        self._points = []
        self._polygons = []
        
    def _get_points(self):
        return self._points
    def _set_points(self, p):
        self._points = p
    points = property(_get_points, _set_points)
    
    def _get_polygons(self):
        return self._polygons
    def _set_polygons(self, poly):
        self._polygons = poly
    polygons = property(_get_polygons, _set_polygons)
    
    #(0,0,0) will always be projected at position (originx, originy) in the 2D plane
    def _get_origin(self):
        return (self._originx, self._originy)
    def _set_origin(self, c):
        self._originx, self._originy = c
        self.update()
    origin = property(_get_origin, _set_origin)
    
    #rotations between the true 3D space and the virtual 3D space
    #see Euler angles
    def _get_rotation_angles(self):
        return (self._anglex, self._angley, self._anglez)
    def _set_rotation_angles(self, t):
        self._anglex, self._angley, self._anglez = t
        self.update()
    angles = property(_get_rotation_angles, _set_rotation_angles)
    
    def _get_axes(self):
        return (self._xAxis, self._yAxis, self._zAxis)
    def _set_axes(self, a):
        self._xAxis, self._yAxis, self._zAxis = a
        self.update()
    axes = property(_get_axes, _set_axes)
    
    def _get_cx(self):
        return self._cx
    cx = property(_get_cx)
    def _get_sx(self):
        return self._sx
    sx = property(_get_sx)
    def _get_cy(self):
        return self._cy
    cy = property(_get_cy)
    def _get_sy(self):
        return self._sy
    sy = property(_get_sy)
    def _get_cz(self):
        return self._cz
    cz = property(_get_cz)
    def _get_sz(self):
        return self._sz
    sz = property(_get_sz)

    def update(self):
        self._cx, self._sx = np.cos(self._anglex),np.sin(self._anglex)
        self._cy, self._sy = np.cos(self._angley),np.sin(self._angley)
        self._cz, self._sz = np.cos(self._anglez),np.sin(self._anglez)
        for p in self._points:
            p.update()
        for poly in self._polygons:
            poly.update()
        #polygons are always sorted by increasing depth
        self._polygons.sort(key = lambda poly: poly.depth)


class Polygon:
    
    def __init__(self, space, pointsList):
        self._space = space
        self._points = pointsList
        self.update()
        self._space.polygons.append(self)
    
    def _get_xyz_true(self):
        return [p.xyzTrue for p in self._points]
    xyzTrue = property(_get_xyz_true)
    
    def _get_xyz_virtual(self):
        return [p.xyzVirtual for p in self._points]
    xyzTrue = property(_get_xyz_virtual)
    
    def _get_xy_projected(self):
        return [p.xyProjected for p in self._points]
    xyProjected = property(_get_xy_projected)
    
    def _get_depth(self):
        return (self._depthMin, self._depthAvg, self._depthMax)
    depth = property(_get_depth)
    
    def update(self):
        self._depthMin = 0
        self._depthAvg = 0
        self._depthMax = 0
        for p in self._points:
            d = p.depth
            self._depthMin = min(d, self._depthMin)
            self._depthMax = max(d, self._depthMax)
            self._depthAvg += d
        self._depthAvg /= len(self._points)













        
        