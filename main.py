import numpy as np
import scipy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as pat
import svgwrite
import sys
import time
import copy
from dataclasses import dataclass
import math

@dataclass
class edge:
    a: list[float]
    b: list[float]
    len: float
    midpoint: list[float] = 'default_factory'

@dataclass
class circle:
    coords: list[float]
    radius: float
def vprint(v):  # given a list, print all elements in the list
    for x in range(0, len(v)):
        print(v[x])

def ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

def midpoint(n):
    return ([(n.a[0]+n.b[0])/2, (n.a[1]+n.b[1])/2])

def maxCircle(q, S):
    R = (-1*((S[0]-q[0])**2)-((S[1]-q[1])**2))/(2.0*(S[0] - q[0]))
    return R

# Return true if line segments AB and CD intersect
def intersect(e):
    for x in range(0, len(e)-1):
        for y in range(x+1,len(e)):
            a = e[x].a
            b = e[x].b
            c = e[y].a
            d = e[y].b
            if ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d):
                return True
    return False

'''
Determine if there are two set of circles that need to be bridged together, or just one (two circles are in the same
set if they are touching)
'''
def onegroup(r, border):
    cellsize=0
    for x in range(len(r)):
        if r[x].radius > cellsize:
            cellsize=r[x].radius
    hashgrid={}
    for x in range(math.ceil(1.0/cellsize)):
        for y in range(math.ceil(1.0/cellsize)):
            hashgrid[(x,y)] = []
    if border > len(r)/2:
        for x in range(border-1, len(r)):
            cell = (r[x].coords[0]//cellsize, r[x].coords[1]//cellsize)
            hashgrid[cell].append(r[x])
        for x in range(0,border-1):
            cell = (r[x].coords[0] // cellsize, r[x].coords[1] // cellsize)
            if len(hashgrid[cell]) > 0:
                for y in range(0, len(hashgrid[cell])):
                    if (dist(hashgrid[cell][y].coords, r[x].coords) - hashgrid[cell][y].radius + r[x].radius) < 0.0001:
                        return 1
        return 2
    else:
        for x in range(0, border-1):
            cell = (r[x].coords[0]//cellsize, r[x].coords[1]//cellsize)
            hashgrid[cell].append(r[x])
        for x in range(border-1, len(r)):
            cell = (r[x].coords[0] // cellsize, r[x].coords[1] // cellsize)
            if len(hashgrid[cell]) > 0:
                for y in range(0, len(hashgrid[cell])):
                    if (dist(hashgrid[cell][y].coords, r[x].coords) - hashgrid[cell][y].radius + r[x].radius) < 0.0001:
                        return 1
        return 2

'''
Bridge together the floating set of circles to the set of circles in on the border, so that all of the circles 
are in the same set
This is achieved by placing a maximum radius circle on the left of the floating set
'''
def bridge(r,border):
    leftmost=r[0]
    for x in range(1, border-1):
        if leftmost.coords[0] > r[x].coords[0]:
            leftmost=r[x]
    query=(leftmost.coords[0]-leftmost.radius, leftmost.coords[1])
    minR=1
    for x in range(border, len(r)):
        S=r[x].coords
        if S[0] < query[0]:
            R=maxCircle(query, S)
            print(R)
            print(r[x])
            if R < minR:
                minR= R
    r.insert(0, circle([query[0]-minR, query[1]], minR))
    ax = plt.subplot()
    c = pat.Circle(r[0].coords, radius=minR, color='red')
    ax.add_patch(c)



def draw(v):
    x = np.array([])
    y = np.array([])
    for n in range(0, len(v)):
        x = np.append(x, v[n][0])
        y = np.append(y, v[n][1])
    x=np.append(x, v[0][0])
    y=np.append(y,v[0][1])
    plt.plot(x,y)
def dist(v1, v2): #given two vertices, determine the distance between them
    x=abs(v1[0]-v2[0])
    y=abs(v1[1]-v2[1])
    return float(np.sqrt((x**2)+(y**2)))


def handle_input():
    #num = int(input("Enter the number of points in the polygon: "))
    num=3
    if num < 3 or num > 20:
        print("the number of vertices must be between 3 and 20 (inclusive)")
        sys.exit(1)
    print("Enter the points of the polygon in order in the form x,y (clockwise order):")
    v = []
    '''
    for x in range(0, num): #converting user input into a list of coordinates
        coords = input().split(",")
        coords[0] = float(coords[0])
        coords[1] = float(coords[1])
        if (coords[0] > 1 or coords[0] < 0) or (coords[1] > 1 or coords[1] < 0): #checks if the coords are in boundary
            print("invalid locations for vertices")
            exit(1)
        v.append(coords)
    '''
    v=[[0.3,0.3],[0.8,0.8],[0.8,0.3]]
    return v

'''
given a list of vertices (and an empty list e):
1. check if the lines defined by the vertices intersects and if so, exit
2. plot the polygon as well as the corners
3. extend the list of vertices to include the corners
4. construct a weighted adjacency matrix representing edges and their lengths
'''
def plot(v, e):
    corners = [[0, 0], [0, 1], [1, 1], [1, 0]]
    for x in range(1, len(v)):
        e.append(edge(v[x-1], v[x], dist(v[x-1], v[x])))
    e.append(edge(v[0], v[-1], dist(v[0], v[-1])))
    for x in range(1, len(corners)):
        e.append(edge(corners[x-1], corners[x], 1))
    e.append(edge(corners[0], corners[-1], 1))
    if intersect(e):
        print("Invalid input, lines intersect or vertices in counterclockwise order")
        exit(1)
    draw(v)
    draw(corners)
    v.extend(corners)

'''
given a list of ordered vertices and a list of edges, define the radius of a circle that is halfway between the
vertex and the nearest non-incident edge for every vertex in the list and modify the list r to include these radii
as well as the coordinates of the vertex that it is centered on
'''
def diskpack1(v,e,r):
    for x in range(0, len(v)):
        n=-1
        vert = np.array(v[x])
        vprint(v[x])
        for y in range(0, len(e)):
            if e[y].a == v[x] or e[y].b == v[x]:
                continue
                #skip all incident edges
            norm = np.array([e[y].a[1] - e[y].b[1], -(e[y].a[0] - e[y].b[0])])
            # normal to the vector between the two points stored in e[y]
            A = np.array(e[y].a)
            B = np.array(e[y].b)  # vectors of endpoints of the edge
            t = (np.dot((vert - A), (B - A))) / ((np.linalg.norm(B - A)) ** 2)
            # calculate the projection parameter
            if t < 0:
                rad = abs(np.linalg.norm(vert - A))
                # the closest point on the edge to the vertex is A
            elif t > 1:
                rad = abs(np.linalg.norm(vert - B))
                # the closest point on the edge to the vertex is B

            else:
                # otherwise, assume the edge to be an infinite line and use vector projection
                p = np.array([v[x][0] - e[y].a[0], v[x][1] - e[y].a[1]])
                # vector from one end of the edge to the vertex
                rad = abs(np.dot(p, norm) / np.linalg.norm(norm))
                # vector projection
            if rad < n or n == -1:
                # want the distance of the closest edge to the vertex
                n = rad

        r.append(circle(v[x], n / 2))

'''
given a list of ordered vertices, a list of edges, a list of circles, place vertices at the points where the edges 
meet the border of a circle and add the edges formed between these vertices to the list uc
'''
def diskpack2(v,e,r,uc):
    for x in range(0, len(e)):
        v1 = np.array([-e[x].a[0] + e[x].b[0], -e[x].a[1] + e[x].b[1]])
        # vector from one endpoint to another
        v1 = (v1 / np.linalg.norm(v1))
        for z in range(0, len(r)):
            if r[z].coords == e[x].a:
                v1 = v1 * r[z].radius
        v1 = v1 + np.array(e[x].a)

        v2 = np.array([-e[x].b[0] + e[x].a[0], -e[x].b[1] + e[x].a[1]])
        # vector from one endpoint to another
        v2 = (v2 / np.linalg.norm(v2))
        for z in range(0, len(r)):
            if r[z].coords == e[x].b:
                v2 = v2 * r[z].radius
        v2 = v2 + np.array(e[x].b)

        uc.append(edge([float(v1[0]),float(v1[1])], [float(v2[0]),float(v2[1])], np.linalg.norm(v1 - v2)))
        uc[-1].midpoint = midpoint(uc[-1])
    ax = plt.subplot()
    for x in range(0, len(uc)):
        c = pat.Circle(uc[x].a, radius=0.01, color='red')
        ax.add_patch(c)
        c = pat.Circle(uc[x].b, radius=0.01, color='red')
        ax.add_patch(c)


def diskpack3(r,uc):
    border=0
    crowded = []
    done = []
    skip=0
    while 1:
        for x in range(0, len(uc)):
            skip=0
            for y in range(x, len(uc)):
                if x == y:
                    continue

                dist = abs(np.linalg.norm(np.array(uc[x].midpoint) - np.array(uc[y].midpoint)))

                # calculate the distance between the two points
                if round(dist, 4) < round(uc[x].len/2 + uc[y].len/2, 4):
                    print(str(round(dist, 3)) + " " + str(round(uc[x].len/2 + uc[y].len/2, 3)))
                    crowded.append(edge(uc[x].a, uc[x].midpoint, uc[x].len/2))
                    crowded[-1].midpoint = midpoint(crowded[-1])
                    # if the diameter disks overlap, split the edge and put it in crowded [ucov[x][0], midp[x]]
                    crowded.append(edge(uc[x].b, uc[x].midpoint, uc[x].len/2))
                    crowded[-1].midpoint = midpoint(crowded[-1])
                    skip = 1
                    break
            if skip == 1:
                continue
            for y in range(0, len(r)):
                dist = abs(np.linalg.norm(np.array(uc[x].midpoint) - np.array(r[y].coords)))
                if round(dist, 4) < round(uc[x].len/2 + r[y].radius, 4):
                    crowded.append(edge(uc[x].a, uc[x].midpoint, uc[x].len / 2))
                    crowded[-1].midpoint = midpoint(crowded[-1])
                    # if the diameter disks overlap, split the edge and put it in crowded [ucov[x][0], midp[x]]
                    crowded.append(edge(uc[x].b, uc[x].midpoint, uc[x].len / 2))
                    crowded[-1].midpoint = midpoint(crowded[-1])
                    skip = 1
                    break
            if skip == 0:
                done.append(uc[x])

        print(len(done))
        if len(crowded) == 0:
            break
        uc.clear()
        uc = copy.deepcopy(crowded)
        crowded.clear()
    ax = plt.subplot()
    for x in range(0, len(done)):
        c = pat.Circle((done[x].midpoint[0], done[x].midpoint[1]),
                       radius=abs(done[x].len / 2), color='yellow')
        ax.add_patch(c)

    for x in range(0, len(done)):
        if (done[x].midpoint[0] in (0,1) or done[x].midpoint[1] in (0,1)):
            r.append(circle(done[x].midpoint, done[x].len/2))
            border+=1
        else:
            r.insert(0, circle(done[x].midpoint, done[x].len/2))
    return border
def diskpack4(r, border):
    if onegroup(r, border) == 2:
        bridge(r, border)

def diskpack(v, e, r):
    diskpack1(v,e,r)
    ax = plt.subplot()
    for x in range(0, len(r)):
        c = pat.Circle(r[x].coords, radius=r[x].radius, color='blue')
        ax.add_patch(c)
    uc=[]
    diskpack2(v,e,r,uc)
    border=diskpack3(r,uc)
    vprint(r)
    diskpack4(r, border)

V=handle_input()
vprint(V)
E=[]
plot(V, E)
R=[]
diskpack(V, E, R)
#map_folds(V,E,R)
plt.show()