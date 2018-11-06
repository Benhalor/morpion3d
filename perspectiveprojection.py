#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A basic 3D engine with rotations (Euler's angles) and projection in a 2D plane
Classes: Point, Space, Polygon and Mesh

Usage example:

s = Space()

A = Point(s, 0, 0, 0)
B = Point(s, 1, 0, 0)
C = Point(s, 1, 1, 0)
D = Point(s, 0, 1, 0)

square = Polygon(s, [A,B,C,D])

ax, ay, az = s.angles

for i in range(24):
    s.angles = (ax, ay, az + i*np.pi/12)
    coordinates_list = square.xyProjected
    # do something with the coordinates

"""

from math import cos, sin, pi, sqrt

class Space:
    """3D space

    Attributes:
        origin (2-tuple): coordinates of the (0,0,0) point in the screen (read/write)
        points (list): all points of the space (read only)
        polygons (list): all polygons of the space (read only)
        angles (3-tuple): rotation angles of the view (read/write)
        axes (3-tuple of 3_tuple): projection axes (read/write)
        cx, sx, cy, sy, cz, sz (floats): cos and sin of the rotation angles (read only)
        xyBounds (2-tuple): ((xmin, ymin), (xmax, ymax)) all points projected coordinates are between these bounds

    Note:
        Writing angles, origin or axes will automatically update the other attributes

    """

    index = 0

    def __init__(self):
        self.__xAxis = (20, 0, 0)
        self.__yAxis = (0, 20, 0)
        self.__zAxis = (0, 0, 20)
        self.__originx = 320
        self.__originy = 240
        self.__anglex = 0
        self.__angley = 0
        self.__anglez = 0
        self.__cx, self.__sx = 1, 0
        self.__cy, self.__sy = 1, 0
        self.__cz, self.__sz = 1, 0
        self.__xyBounds = [0, 0, 0, 0]  # minx, miny, maxx, maxy
        self.__points = []
        self.__polygons = []
        self.__index = Space.index
        self.__lightVector = Vector(self, 2, 3, 1)
        Space.index += 1

    def update(self, noTrigo=False, noSort=False):
        """Updates the trigonometric values, the points and the polygons"""
        if not noTrigo:
            self.__cx, self.__sx = cos(self.__anglex), sin(self.__anglex)
            self.__cy, self.__sy = cos(self.__angley), sin(self.__angley)
            self.__cz, self.__sz = cos(self.__anglez), sin(self.__anglez)
        for p in self.__points:
            p.update()
        for poly in self.__polygons:
            poly.update()
        if not noSort:
            # polygons are always sorted by increasing depth to draw them "corectly" (painter's algorithm)
            self.__polygons.sort(key=lambda poly: poly.depth)

    def locate_polygon(self, x, y):
        """Finds the polygon under point (x,y) on 2D plane of the screen.
        Solves the Point-in-polygon problem with the Winding Number algorithm"""
        for poly in self.__polygons:
            if not poly.locate:
                continue
            windingNumber = 0
            V = poly.xyProjected + [poly.xyProjected[0]]
            n = len(poly.xyProjected)
            for i in range(n):
                if V[i][1] <= y:
                    if V[i + 1][1] > y:
                        if self.__test_left(V[i], V[i + 1], (x, y)) > 0:
                            windingNumber += 1
                else:
                    if V[i + 1][1] <= y:
                        if self.__test_left(V[i], V[i + 1], (x, y)) < 0:
                            windingNumber -= 1
            if windingNumber != 0:
                return poly
        return None

    def __test_left(self, a, b, c):
        """tests if c is left of the ab line"""
        v = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
        if v > 0:
            return 1  # c is left of the line
        elif v < 0:
            return -1  # c is right of the line
        else:
            return 0  # c is on the line

    def __str__(self):
        return "Space instance " + str(self.__index)

    def __get_light_vector(self):
        return self.__lightVector

    lightVector = property(__get_light_vector)

    def __get_points(self):
        return self.__points

    points = property(__get_points)

    def __get_polygons(self):
        return self.__polygons

    polygons = property(__get_polygons)

    # (0,0,0) will always be projected at position (originx, originy) in the 2D plane
    def __get_origin(self):
        return (self.__originx, self.__originy)

    def __set_origin(self, c):
        if type(c) != tuple:
            raise TypeError("Argument 'c': expected 'tuple', got " + str(type(c)))
        if len(c) != 2:
            raise ValueError("Tuple c should have 2 elements, but has " + str(len(c)))
        self.__originx, self.__originy = c
        self.update(noTrigo=True)

    origin = property(__get_origin, __set_origin)

    # rotations between the true 3D space and the virtual 3D space
    # see Euler angles
    def __get_rotation_angles(self):
        return (self.__anglex, self.__angley, self.__anglez)

    def __set_rotation_angles(self, t):
        if type(t) != tuple:
            raise TypeError("Argument 't': expected 'tuple', got " + str(type(t)))
        if len(t) != 3:
            raise ValueError("Tuple t should have 3 elements, but has " + str(len(t)))
        tx, ty, tz = t
        tx %= (2 * pi)
        ty %= (2 * pi)
        tz %= (2 * pi)
        self.__anglex, self.__angley, self.__anglez = tx, ty, tz
        self.update()

    angles = property(__get_rotation_angles, __set_rotation_angles)

    def __get_axes(self):
        return (self.__xAxis, self.__yAxis, self.__zAxis)

    def __set_axes(self, a):
        if type(a) != tuple:
            raise TypeError("Argument 'a': expected 'tuple', got " + str(type(a)))
        if len(a) != 3:
            raise ValueError("Tuple a should have 3 elements, but has " + str(len(a)))
        self.__xAxis, self.__yAxis, self.__zAxis = a
        self.update()

    axes = property(__get_axes, __set_axes)

    def __get_cx(self):
        return self.__cx

    cx = property(__get_cx)

    def __get_sx(self):
        return self.__sx

    sx = property(__get_sx)

    def __get_cy(self):
        return self.__cy

    cy = property(__get_cy)

    def __get_sy(self):
        return self.__sy

    sy = property(__get_sy)

    def __get_cz(self):
        return self.__cz

    cz = property(__get_cz)

    def __get_sz(self):
        return self.__sz

    sz = property(__get_sz)

    def __get_xyBounds(self):
        self.__xyBounds[0] = self.__points[0].xyProjected[0]
        self.__xyBounds[1] = self.__points[0].xyProjected[1]
        self.__xyBounds[2] = self.__points[0].xyProjected[0]
        self.__xyBounds[3] = self.__points[0].xyProjected[1]
        for p in self.__points[1:]:
            xp, yp = p.xyProjected
            self.__xyBounds[0] = min(self.__xyBounds[0], xp)
            self.__xyBounds[1] = min(self.__xyBounds[1], yp)
            self.__xyBounds[2] = max(self.__xyBounds[2], xp)
            self.__xyBounds[3] = max(self.__xyBounds[3], yp)
        xmin, ymin, xmax, ymax = self.__xyBounds
        return ((xmin, ymin), (xmax, ymax))

    xyBounds = property(__get_xyBounds)


class Point:
    """3D point in a given space.

    Attributes:
        xyzTrue (3-tuple): True coordinates of the point in the 3D space (read/write)
        xyzVirtual (3-tuple): coordinates after the rotation of the view (read only)
        xyProjected (2-tuple): coordinates of the point as displayed on the screen (read only)
        depth: points with higher depth value are "behind" others in the screen (read only)

    Note:
        Writing xyzTrue will automatically update the other attributes

    """

    def __init__(self, space, x, y, z):
        """Args:
            space: an instance of class Space
            x:
            y:
            z: True coordinates of the point in the 3D space
        """
        if not isinstance(space, Space):
            raise TypeError("Argument 'space' is not an instance of class 'Space'")
        self.__space = space
        self.__x = x
        self.__y = y
        self.__z = z
        self.__virtualx = x
        self.__virtualy = y
        self.__virtualz = z
        self.__projectedx = 0
        self.__projectedy = 0
        self.__depth = 0
        self.update()
        self.__space.points.append(self)

    def update(self):
        """Updates the virtual and projected coordinates, and the depth"""
        # the three rotation matrices multiplication
        self.__virtualx = self.__space.cy * (
                self.__space.sz * self.__y + self.__space.cz * self.__x) - self.__space.sy * self.__z
        self.__virtualy = self.__space.sx * (self.__space.cy * self.__z + self.__space.sy * (
                self.__space.sz * self.__y + self.__space.cz * self.__x)) + self.__space.cx * (
                                  self.__space.cz * self.__y - self.__space.sz * self.__x)
        self.__virtualz = self.__space.cx * (self.__space.cy * self.__z + self.__space.sy * (
                self.__space.sz * self.__y + self.__space.cz * self.__x)) - self.__space.sx * (
                                  self.__space.cz * self.__y - self.__space.sz * self.__x)

        # projection in the 2D plane
        axes = self.__space.axes
        origin = self.__space.origin
        self.__projectedx = self.__virtualx * axes[0][0] + self.__virtualy * axes[1][0] + self.__virtualz * axes[2][0] + \
                            origin[0]
        self.__projectedy = self.__virtualx * axes[0][1] + self.__virtualy * axes[1][1] + self.__virtualz * axes[2][1] + \
                            origin[1]
        self.__projectedx = int(self.__projectedx)
        self.__projectedy = int(self.__projectedy)

        # depth. Higher values are "behind" lower values
        self.__depth = self.__virtualx * axes[0][2] + self.__virtualy * axes[1][2] + self.__virtualz * axes[2][2]

    def __str__(self):
        return 'True: ' + str((self.__x, self.__y, self.__z)) + ' Virtual: ' + str(
            (self.__virtualx, self.__virtualy, self.__virtualz)) + ' Projected: ' + str(
            (self.__projectedx, self.__projectedy))

    def __repr__(self):
        return str((self.__x, self.__y, self.__z))

    def __get_xyz_true(self):
        return (self.__x, self.__y, self.__z)

    def __set_xyz_true(self, c):
        if type(c) != tuple:
            raise TypeError("Argument 'c': expected 'tuple', got " + str(type(c)))
        if len(c) != 3:
            raise ValueError("Tuple c should have 3 elements, but has " + str(len(c)))
        self.__x, self.__y, self.__z = c
        self.update()

    xyzTrue = property(__get_xyz_true, __set_xyz_true)

    def __get_xyz_virtual(self):
        return (self.__virtualx, self.__virtualy, self.__virtualz)

    xyzVirtual = property(__get_xyz_virtual)

    def __get_xy_projected(self):
        return (self.__projectedx, self.__projectedy)

    xyProjected = property(__get_xy_projected)

    def __get_depth(self):
        return self.__depth

    depth = property(__get_depth)

class Vector(Point) :
    """A vector defined by its 3 coordinates (it acts like a Point but we can also do some other operations)"""
    def __init__(self, space, x, y, z):
        Point.__init__(self,space, x, y, z)

    def scalar_product_with_light(self, lightVector):
        """Scalar product divided by the norms of the vectors of this vector with a light vector"""
        if not isinstance(lightVector, Vector):
            raise TypeError("'lightVector' argument must be a Vector, got :"+str(type(lightVector)))
        norms = self.norm()*lightVector.norm()
        if norms != 0 :
            (x1,y1,z1) = self.xyzVirtual
            (x2,y2,z2) = lightVector.xyzTrue
            return (x1*x2+y1*y2+z1*z2)/norms
        else :
            return 0

    def color_coeff(self, lightVector):
        """Computes a color coefficient corresponding to the scalar product of the vector with a light vector"""
        return 0.5*(1-self.scalar_product_with_light(lightVector))

    def norm(self):
        (x,y,z) = self.xyzVirtual
        return sqrt(x**2+y**2+z**2)

class Polygon:
    """A polygon defined by a list of points

    Attributes:
        xyzTrue (list): xyzTrue of the polygon's points (read only)
        xyzVirtual (list): xyzVirtual of the polygon's points (read only)
        xyProjected (list): xyProjected of the polygon's points (read only)
        depth (3-tuple): (depth min, depth average, depth max) (read only)
        locate (bool): if false, thje polygon will be skipped in the polygon search (read only)
        points (list): points list (read only)
        phantomPoint (Point): a point not really belonging to the polygon. If set, it is used for depth computations instead of the other points (read/write)

    """

    def __init__(self, space, pointsList, locate=True, normal = None):
        """Args:
            space: an instance of class Space
            pointsList: a list of instance of class Point
            name: a string
            locate: a boolean. If false, the polygon will be skipped in the polygon search
        """
        if not isinstance(space, Space):
            raise TypeError("Argument 'space' is not an instance of class 'Space'")
        for p in pointsList:
            if not isinstance(p, Point):
                raise TypeError("Argument 'pointsList' should only contains 'Point', but has " + str(type(p)))
        if type(locate) != bool:
            raise TypeError("Argument 'locate': expected 'bool', got " + str(type(locate)))
        if normal is not None :
            if type(normal) != tuple :
                raise TypeError("Argument 'normal' expected 'tuple', got "+ str(type(normal)))
            elif len(normal) != 3 :
                raise TypeError("Argument 'normal' expected 'tuple' of 3 elements , got a tuple of " + str(len(normal))+" elements")

        self.__space = space
        self.__points = pointsList
        self.__phantomPoint = None
        self.__locate = locate
        self.__mesh = None
        self.update()
        self.__space.polygons.append(self)
        if normal is not None :
            self.__normalVector = Vector(self.__space,normal[0],normal[1],normal[2])
        else :
            self.__normalVector = None

    def update(self):
        """Updates the depth values of the polygon"""
        if self.__phantomPoint is None:
            self.__depth = 0
            for p in self.__points:
                d = p.depth
                self.__depth += d
            self.__depth /= len(self.__points)
        else:
            self.__depth = self.__phantomPoint.depth

    def translate(self, t):
        """Translate all points true coordinates with the given vector.
        Warning: no duplicate check"""
        if type(t) != tuple:
            raise TypeError("Argument 't': expected 'tuple', got " + str(type(t)))
        if len(t) != 3:
            raise ValueError("Tuple t should have 3 elements, but has " + str(len(t)))
        tx, ty, tz = t
        for p in self.__points:
            x, y, z = p.xyzTrue
            p.xyzTrue = (x + tx, y + ty, z + tz)
        self.update()

    def __get_xyz_true(self):
        return [p.xyzTrue for p in self.__points]

    xyzTrue = property(__get_xyz_true)

    def __get_xyz_virtual(self):
        return [p.xyzVirtual for p in self.__points]

    xyzVirtual = property(__get_xyz_virtual)

    def __get_xy_projected(self):
        return [p.xyProjected for p in self.__points]

    xyProjected = property(__get_xy_projected)

    def __get_depth(self):
        return self.__depth

    depth = property(__get_depth)

    def __get_locate(self):
        return self.__locate

    locate = property(__get_locate)

    def __get_points(self):
        return self.__points

    points = property(__get_points)

    def __get_mesh(self):
        return self.__mesh

    def __set_mesh(self, m):
        if not isinstance(m, Mesh):
            raise TypeError("Argument 'm': expected 'Mesh', got " + str(type(m)))
        if self.__mesh is not None:
            raise ValueError("This polygon already belongs to a mesh")
        self.__mesh = m

    mesh = property(__get_mesh,__set_mesh)

    def __get_normal_vector(self):
        return self.__normalVector
    normal_vector = property(__get_normal_vector)

    def __get_phantom_point(self):
        return self.__phantomPoint

    def __set_phantom_point(self, p):
        if not isinstance(p, Point):
            raise TypeError("Argument 'p': expected 'Point', got " + str(type(p)))
        self.__phantomPoint = p

    phantomPoint = property(__get_phantom_point, __set_phantom_point)


class Mesh:
    """A mesh defined by a list of polygons

    Attributes:
        polygons (list): list of all polygons in the mesh (read only)
        angles (3-tuple): (ax,ay,az) rotation angles of the mesh (read/write)
        center (3-tuple): (cx,cy,cz) coordinates of the center of the mesh (read/write)

    Note:
        Setting center or angles will update the xyzTrue value of all points in the mesh

    """

    def __init__(self, space, polygonList):
        if not isinstance(space, Space):
            raise TypeError("Argument 'space' is not an instance of class 'Space'")
        for poly in polygonList:
            if not isinstance(poly, Polygon):
                raise TypeError("Argument 'polygonList' should only contains 'Polygon', but has " + str(type(poly)))
        self.__polygonList = polygonList
        cx, cy, cz = 0, 0, 0
        self.__points = set()
        self.__dpoints = dict()
        for poly in self.__polygonList:
            poly.mesh = self
            for p in poly.points:
                if p not in self.__points:
                    self.__points.add(p)
                    xp, yp, zp = p.xyzTrue
                    cx += xp
                    cy += yp
                    cz += zp
        l = len(self.__points)
        self.__center = (cx / l, cy / l, cz / l)
        self.__angles = (0.0, 0.0, 0.0)
        for p in self.__points:
            xp, yp, zp = p.xyzTrue
            self.__dpoints[p] = (xp - self.__center[0], yp - self.__center[1], zp - self.__center[2])

    def __get_angles(self):
        return self.__angles

    def __set_angles(self, a):
        if type(a) != tuple:
            raise TypeError("Argument 'a': expected 'tuple', got " + str(type(a)))
        if len(a) != 3:
            raise ValueError("Tuple a should have 3 elements, but has " + str(len(a)))
        ax, ay, az = a
        ax %= (2 * pi)
        ay %= (2 * pi)
        az %= (2 * pi)
        cx, sx = cos(ax), sin(ax)
        cy, sy = cos(ay), sin(ay)
        cz, sz = cos(az), sin(az)
        for p in self.__points:
            dx, dy, dz = self.__dpoints[p]
            xn = cy * (sz * dy + cz * dx) - sy * dz
            yn = sx * (cy * dz + sy * (sz * dy + cz * dx)) + cx * (cz * dy - sz * dx)
            zn = cx * (cy * dz + sy * (sz * dy + cz * dx)) - sx * (cz * dy - sz * dx)
            p.xyzTrue = (self.__center[0] + xn, self.__center[1] + yn, self.__center[2] + zn)
        self.__angles = (ax, ay, az)

    angles = property(__get_angles, __set_angles)

    def __get_center(self):
        return self.__center

    def __set_center(self, c):
        if type(c) != tuple:
            raise TypeError("Argument 'c': expected 'tuple', got " + str(type(c)))
        if len(c) != 3:
            raise ValueError("Tuple c should have 3 elements, but has " + str(len(c)))
        for p in self.__points:
            dx, dy, dz = self.__dpoints[p]
            p.xyzTrue = (c[0] + dx, c[1] + dy, c[2] + dz)
        self.__center = c

    center = property(__get_center, __set_center)

    def __get_polygons(self):
        return self.__polygonList

    polygons = property(__get_polygons)



