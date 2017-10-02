import numpy as np
from scipy.spatial.distance import euclidean

class Box:
    def __init__(self, (xmin, ymin, width, height)):
        self.xmin = xmin
        self.ymin = ymin
        self.width = width
        self.height = height
        self.xmax = xmax = xmin + width
        self.ymax = ymax = ymin + height
        self.area = width * height
        self.xmid = xmid = float(xmax + xmin) / 2
        self.ymid = ymid = float(ymax + ymin) / 2
        self.points = [[xmin,ymin],[xmax,ymin],[xmax,ymax],[xmin,ymax]]
        self.line_segments = [
            [ np.asarray([xmin,ymin]), np.asarray([xmax,ymin]) ],
            [ np.asarray([xmax,ymin]), np.asarray([xmax,ymax]) ],
            [ np.asarray([xmax,ymax]), np.asarray([xmin,ymax]) ],
            [ np.asarray([xmin,ymax]), np.asarray([xmin,ymin]) ]
        ]
        self.node = np.asarray([xmid, ymid])
        self.bbox = np.asarray([xmin, ymin, xmax, ymax])

def merge_boxes(box1, box2):
    xmin = min(box1.xmin, box2.xmin)
    xmax = max(box1.xmax, box2.xmax)
    ymin = min(box1.ymin, box2.ymin)
    ymax = max(box1.ymax, box2.ymax)
    width = xmax - xmin
    height = ymax - ymin
    return Box((xmin, ymin, width, height))

#https://stackoverflow.com/questions/2824478/shortest-distance-between-two-line-segments
def closestDistanceBetweenLines(a0,a1,b0,b1,clampAll=True,clampA0=False,clampA1=False,clampB0=False,clampB1=False):

    ''' Given two lines defined by numpy.array pairs (a0,a1,b0,b1)
        Return the closest points on each segment and their distance
    '''

    # If clampAll=True, set all clamps to True
    if clampAll:
        clampA0=True
        clampA1=True
        clampB0=True
        clampB1=True


    # Calculate denomitator
    A = a1 - a0
    B = b1 - b0
    magA = np.linalg.norm(A)
    magB = np.linalg.norm(B)

    _A = A / magA
    _B = B / magB

    cross = np.cross(_A, _B);
    denom = np.linalg.norm(cross)**2


    # If lines are parallel (denom=0) test if lines overlap.
    # If they don't overlap then there is a closest point solution.
    # If they do overlap, there are infinite closest positions, but there is a closest distance
    if not denom:
        d0 = np.dot(_A,(b0-a0))

        # Overlap only possible with clamping
        if clampA0 or clampA1 or clampB0 or clampB1:
            d1 = np.dot(_A,(b1-a0))

            # Is segment B before A?
            if d0 <= 0 >= d1:
                if clampA0 and clampB1:
                    if np.absolute(d0) < np.absolute(d1):
                        return a0,b0,np.linalg.norm(a0-b0)
                    return a0,b1,np.linalg.norm(a0-b1)


            # Is segment B after A?
            elif d0 >= magA <= d1:
                if clampA1 and clampB0:
                    if np.absolute(d0) < np.absolute(d1):
                        return a1,b0,np.linalg.norm(a1-b0)
                    return a1,b1,np.linalg.norm(a1-b1)


        # Segments overlap, return distance between parallel segments
        return None,None,np.linalg.norm(((d0*_A)+a0)-b0)



    # Lines criss-cross: Calculate the projected closest points
    t = (b0 - a0);
    detA = np.linalg.det([t, _B, cross])
    detB = np.linalg.det([t, _A, cross])

    t0 = detA/denom;
    t1 = detB/denom;

    pA = a0 + (_A * t0) # Projected closest point on segment A
    pB = b0 + (_B * t1) # Projected closest point on segment B


    # Clamp projections
    if clampA0 or clampA1 or clampB0 or clampB1:
        if clampA0 and t0 < 0:
            pA = a0
        elif clampA1 and t0 > magA:
            pA = a1

        if clampB0 and t1 < 0:
            pB = b0
        elif clampB1 and t1 > magB:
            pB = b1

        # Clamp projection A
        if (clampA0 and t0 < 0) or (clampA1 and t0 > magA):
            dot = np.dot(_B,(pA-b0))
            if clampB0 and dot < 0:
                dot = 0
            elif clampB1 and dot > magB:
                dot = magB
            pB = b0 + (_B * dot)

        # Clamp projection B
        if (clampB0 and t1 < 0) or (clampB1 and t1 > magB):
            dot = np.dot(_A,(pB-a0))
            if clampA0 and dot < 0:
                dot = 0
            elif clampA1 and dot > magA:
                dot = magA
            pA = a0 + (_A * dot)


    return pA,pB,np.linalg.norm(pA-pB)

rect_distance_cache = {}

#https://stackoverflow.com/questions/4978323/how-to-calculate-distance-between-two-rectangles-context-a-game-in-lua
def rect_distance(rect1, rect2):
    #print "starting rect_distance with x1,", x1, x2, y1b, y2b
    key = (rect1.tostring(), rect2.tostring())
    if key in rect_distance_cache:
        #print "F",
        return rect_distance_cache[key]
    #print "_",
    x1, y1, x1b, y1b = rect1
    x2, y2, x2b, y2b = rect2
    distance = None
    left = x2b < x1
    right = x1b < x2
    bottom = y2b < y1
    top = y1b < y2
    if top and left:
        distance = euclidean((x1, y1b), (x2b, y2))
    elif left and bottom:
        distance = euclidean((x1, y1), (x2b, y2b))
    elif bottom and right:
        distance = euclidean((x1b, y1), (x2, y2b))
    elif right and top:
        distance = euclidean((x1b, y1b), (x2, y2))
    elif left:
        distance = x1 - x2b
    elif right:
        distance = x2 - x1b
    elif bottom:
        distance = y1 - y2b
    elif top:
        distance = y2 - y1b
    else: # rectangles intersect
        distance = 0

    rect_distance_cache[key] = distance
    return distance
