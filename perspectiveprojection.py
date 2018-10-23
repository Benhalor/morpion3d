#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np

class Point:
    
    def __init__(self, space, x, y, z):
        self._space = space
        self._xyzTrue = np.array((x,y,z))
        self._xyzVirtual = np.array((x,y,z))
        self._xyzProjected = np.array((0,0,0))
        self.update()
        self._space.points.append(self)
        
    def __str__(self):
        return 'True: ' + str((self._x, self._y, self._z)) + ' Virtual: ' + str((self._virtualx, self._virtualy, self._virtualz)) + ' Projected: ' + str((self._projectedx, self._projectedy))
    
    def __repr__(self):
        return str((self._x, self._y, self._z))
    
    def _get_xyz_true(self):
        return self._xyzTrue
    def _set_xyz_true(self, c):
        self._xyzTrue = c
        self.update()
    xyzTrue = property(_get_xyz_true, _set_xyz_true)
    
    def _get_xyz_virtual(self):
        return self._xyzVirtual
    xyzVirtual = property(_get_xyz_virtual)
    
    def _get_xy_projected(self):
        return self._xyzprojected[:2]
    xyProjected = property(_get_xy_projected)
    
    def _get_depth(self):
        #depth. Higher values are "behind" lower values
        return self._xyzprojected[2]
    depth = property(_get_depth)
    
    def update(self):
        #the three rotation matrices multiplication
        Mx = np.array([[1,0,0],[0, self._space.c[0],self._space.s[0]],[0,-self._space.s[0],self._space.c[0]]])
        My = np.array([[self._space.c[1],0,-self._space.s[1]],[0,1,0],[self._space.s[1],0, self._space.c[1]]])
        Mz = np.array([[self._space.c[2],self._space.s[2],0],[-self._space.s[2], self._space.c[2],0],[0,0,1]])
        self._xyzVirtual = Mx @ My @ Mz @ self._xyzTrue
        
        #projection in the 2D plane
        self._xyzProjected = self._space.axes @ self._xyzVirtual
        self._xyzProjected[:2] += self._space.origin


class Space:
    
    index = 0
    
    def __init__(self):
        self._axes = np.array([[1,0,0],[0,-1,0],[0,0,-1]])
        self._origin = np.array((320,240))
        self._angles = np.array((0,0,0))
        self._c = np.array((1,1,1))
        self._s = np.array((0,0,0))
        self._xyBounds = [0,0,0,0] #minx, miny, maxx, maxy
        self._points = []
        self._polygons = []
        self._index = Space.index
        Space.index += 1
        
        #default values: isometric projection centered in a 640x480 plane
        self.angles = np.array((np.arctan(1/np.sqrt(2)), np.pi/4, 0))
        
    def __str__(self):
        return "Space instance " + str(self._index)
        
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
        return self._origin
    def _set_origin(self, c):
        self._origin = c
        self.update()
    origin = property(_get_origin, _set_origin)
    
    #rotations between the true 3D space and the virtual 3D space
    #see Euler angles
    def _get_rotation_angles(self):
        return self._angles
    def _set_rotation_angles(self, t):
        self._angles = t
        self.update()
    angles = property(_get_rotation_angles, _set_rotation_angles)
    
    def _get_axes(self):
        return self._axes
    def _set_axes(self, a):
        self._axes = a
        self.update()
    axes = property(_get_axes, _set_axes)
    
    def _get_c(self):
        return self._c
    c = property(_get_c)
    def _get_s(self):
        return self._s
    s = property(_get_s)
    
    def _get_xyBounds(self):
        for p in self._points:
            xp, yp = p.xyProjected
            self._xyBounds[0] = min(self._xyBounds[0], xp)
            self._xyBounds[1] = min(self._xyBounds[1], yp)
            self._xyBounds[2] = max(self._xyBounds[2], xp)
            self._xyBounds[3] = max(self._xyBounds[3], yp)
        xmin, ymin, xmax, ymax = self._xyBounds
        return ((xmin, ymin), (xmax, ymax))
    xyBounds = property(_get_xyBounds)

    def update(self):
        self._c = np.cos(self._angles)
        self._s = np.sin(self._angles)
        for p in self._points:
            p.update()
        for poly in self._polygons:
            poly.update()
        #polygons are always sorted by increasing depth
        self._polygons.sort(key = lambda poly: poly.depth)
        
    def _test_left(self, a, b, c):
        #test if c is left of the ab line
        v = (b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1])
        if v > 0:
            return 1 #c is left of the line
        elif v <0:
            return -1 #c is right of the line
        else:
            return 0 #c is on the line
        
    def locate_polygon(self, x, y):
        #using the winding number algorithm
        for poly in self._polygons:
            if not poly.locate:
                continue
            windingNumber = 0
            V = poly.xyProjected + [poly.xyProjected[0]]
            n = len(poly.xyProjected)
            for i in range(n):
                if V[i][1] <= y:
                    if V[i+1][1] > y:
                        if self._test_left(V[i], V[i+1], (x,y)) > 0:
                            windingNumber += 1
                else:
                    if V[i+1][1] <= y:
                        if self._test_left(V[i], V[i+1], (x,y)) < 0:
                            windingNumber -= 1
            if windingNumber != 0:
                return poly
        return None


class Polygon:
    
    def __init__(self, space, pointsList, name = '', locate = True):
        self._space = space
        self._points = pointsList
        #self._normalVector = (0,0,0)
        self._locate = locate
        self._name = name
        self.update()
        self._space.polygons.append(self)
        
    def __str__(self):
        return "Polygon " + self._name
    
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
    
    """
    def _get_normal_vector(self):
        return self._normalVector
    normalVector = property(_get_normal_vector)"""

    def _get_locate(self):
        return self._locate
    locate = property(_get_locate)
    
    def _get_name(self):
        return self._name
    name = property(_get_name)

    def translate(self, t):
        for p in self._points:
            p.xyzTrue += t
        self.update()
    
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
        """
        if len(self._points) >= 3:
            (xa,ya,za) = self._points[0].xyzVirtual
            (xb,yb,zb) = self._points[1].xyzVirtual
            (xc,yc,zc) = self._points[2].xyzVirtual
            self._normalVector = ((yb-ya)*(zc-zb) - (zb-za)*(yc-yb), \
                                  (zb-za)*(xc-xb) - (xb-xa)*(zc-zb), \
                                  (xb-xa)*(yc-yb) - (yb-ya)*(xc-xb))
        """








        
        