from math import sqrt
from numpy import median

def distance(p0, p1):
    return sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def avg_distance(point, points):
    return median([distance(point, other_point) for other_point in points])
