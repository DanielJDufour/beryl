from numpy import asarray

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
        self.node = asarray([xmid, ymid])

def merge_boxes(box1, box2):
    xmin = min(box1.xmin, box2.xmin)
    xmax = max(box1.xmax, box2.xmax)
    ymin = min(box1.ymin, box2.ymin)
    ymax = max(box1.ymax, box2.ymax)
    width = xmax - xmin
    height = ymax - ymin
    return Box((xmin, ymin, width, height))
