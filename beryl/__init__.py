import cv2, editdistance, numpy
from collections import defaultdict
from datetime import datetime
from math import sqrt
from numpy import amin, argmin, asarray, mean, median, sum, triu_indices
import numpy as np
from os.path import abspath, dirname
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngImageFile
from pytesseract import image_to_string
from scipy.spatial.distance import cdist, pdist
from subprocess import call, Popen
from time import sleep
from recorder import record

# notes
# probably need some sort of caching mechanism
# so don't have to rerun everything if doing repeated
# actions like clicking on a certain button
# maybe look at old location first and if don't find
# there, then run again??

path_to_this_directory = dirname(abspath(__file__))
path_to_cache_directory = path_to_this_directory + "/cache/"
path_to_cache_image = path_to_cache_directory + "image.txt"
path_to_cache_text = path_to_cache_directory + "text.txt"

# maybe need to train on an image before search for it
global cache
cache = {}

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

def getGoodImage(image):

    width, height = image.size

    #bg_colors = set()
    #bg_colors.add(image.getpixel((0,0)))
    #bg_colors.add(image.getpixel((width-1,0)))
    #bg_colors.add(image.getpixel((width-1,height-1)))
    #bg_colors.add(image.getpixel((0,height-1)))

    #print "bg_colors from corners:", bg_colors

    # find text color by looking at most popular color through the middle of the image
    midheight = float(height)/2
    middle_pixels = [image.getpixel((i,midheight)) for i in range(width) ]
    print "middle_pixels:", middle_pixels
    return image

def is_there_more_than_one_color(data):
    color = data[0]
    for pixel in data:
        if pixel != color:
            return True
    return False

def area_of_box(box):
    #print "area_of_box started with"
    #print "\t", box
    #print "\t", x
    #raw_input()
    w = box[1][0] - box[0][0]
    h = box[2][1] - box[1][1]
    return w * h

def is_text_on_screen(target, notify=True):

    if notify:
        _notify("starting is_text_on_screen")

    if isinstance(target, str):
        target = target.decode('utf-8')

    #GET SCREENSHOT
    call(["gnome-screenshot", "--file=/tmp/beryl.png"])
    sleep(1)

    #FIND TEXTS
    im = cv2.imread('/tmp/beryl.png')
    im = cv2.resize(im, (0,0), fx=2, fy=2)
    imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    #ret,thresh = cv2.threshold(imgray,127,255,0)
    ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for index, contour in enumerate(contours):
        b = Box(cv2.boundingRect(contour))
        if b.width > 10 and b.height > 6:
            cropped = im[b.ymin:b.ymax, b.xmin:b.xmax]
            text = image_to_string(Image.fromarray(cropped))
            print("text:", text)
            if target in text.decode("utf-8"):
                return True

def click_text(name, notify=True, use_cache=True):
    global cache

    write_to_cache = False
    found = None

    print "starting click_text with", name
    time_started_method = datetime.now()

    loadCacheTextIfNecessary()

    if notify:
        _notify("starting to click " + name) 
        sleep(1)
        call(["killall","notify-osd"])
        sleep(1)

    #GET SCREENSHOT
    call(["gnome-screenshot", "--file=/tmp/beryl.png"])
    sleep(0.5)

    #FIND LOCATION OF NAME
    imgray = cv2.cvtColor(cv2.imread('/tmp/beryl.png'),cv2.COLOR_BGR2GRAY)
    #cv2.imwrite('/tmp/imgray.png',imgray)
    ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)
    #ret,thresh = cv2.threshold(imgray,127,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
    #ret, thresh = cv2.adaptiveThreshold(imgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
    #cv2.imwrite('/tmp/thresh.png',thresh)

    if name in cache['text']:
        print "NAME IN CACHE TEXT"
        xmin, ymin, xmax, ymax = [float(_) for _ in cache['text'][name]]
        text = image_to_string(Image.fromarray(imgray[ymin:ymax, xmin:xmax])) or image_to_string(Image.fromarray(thresh[ymin:ymax, xmin:xmax]))
        if not text:
            # pad coordinates by 2 pixels
            if xmax <= box.width - 2: xmax += 2
            if xmin >= 2: xmin -= 2
            if ymin >= 2: ymin -= 2
            if ymax <= box.height - 2: ymax += 2
            text = image_to_string(Image.fromarray(imgray[ymin:ymax, xmin:xmax])) or image_to_string(Image.fromarray(thresh[ymin:ymax, xmin:xmax])) 
        print "\ttext:", text

        if text == name:
            found = Box((xmin, ymin, xmax-xmin, ymax-ymin))
            found.text = text

    if found is None:
 
        contours, hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cv2.imwrite('/tmp/thresh.png',thresh)
        #contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        #cv2.drawContours(im, contours, -1, (255, 255, 0), 3)
        #cv2.imshow("Keypoints", im)
        #cv2.waitKey(0)
        hierarchy = hierarchy.tolist()[0] # converting from ndarry to list
        boxes = []
        parent_children = defaultdict(list)
        for index, contour in enumerate(contours):
            box = Box(cv2.boundingRect(contour))
            boxes.append(box)
            parent_children[hierarchy[index][3]].append(box)

        print "len after beginning;", len(boxes)

        for parent in parent_children:
            #print "parent:", parent
            children = parent_children[parent]
            number_of_children = len(children)
            print "number_of_children:", number_of_children
            while len(children) > 1:
                number_of_children = len(children)
                nodes = [child.node for child in children]

                # wow numpy to the rescue!
                a = argmin(pdist(nodes, 'euclidean'))
                #n = sqrt(2*number_of_children)
                ti = triu_indices(number_of_children, 1)
                box1 = children[ti[0][a]]
                box2 = children[ti[1][a]]
           
                new_box = merge_boxes(box1,box2)
                boxes.append(new_box)
                children.append(new_box)
                children.remove(box1)
                children.remove(box2)

        #print("len after mergin:", len(boxes))

        #print "boxes:", boxes
        #boxes.sort(area_of_box) # go from smallest to biggest
        boxes = sorted(boxes, key=lambda box: box.area)
        print "sorted boxes by area"
    
        found = None
        d = {}
        minimum_width = 5 * len(name)
        print "minimum width:", minimum_width
        print "number of boxes:", len(boxes)
        for index, box in enumerate(boxes):
            # ignore if data all one color

            if minimum_width < box.width < 500 and 10 < box.height < 500:
                print "\tBOX", index, "PASSED",
                impath = "/tmp/"+str(index)+".png"
                xmax = box.xmax 
                xmin = box.xmin 
                ymax = box.ymax
                ymin = box.ymin 
                text = image_to_string(Image.fromarray(imgray[ymin:ymax, xmin:xmax])) 
                if not text:
                    text = image_to_string(Image.fromarray(thresh[ymin:ymax, xmin:xmax])) 
                    if not text:

                        # pad coordinates by 2 pixels
                        if xmax <= box.width - 2: xmax += 2
                        if xmin >= 2: xmin -= 2
                        if ymin >= 2: ymin -= 2
                        if ymax <= box.height - 2: ymax += 2

                        text = image_to_string(Image.fromarray(imgray[ymin:ymax, xmin:xmax])) 
                        if not text:
                            text = image_to_string(Image.fromarray(thresh[ymin:ymax, xmin:xmax])) 
                            cv2.imwrite(impath,thresh[ymin:ymax, xmin:xmax])
                        else:
                            cv2.imwrite(impath,imgray[ymin:ymax, xmin:xmax]) 
                    else:
                        cv2.imwrite(impath,thresh[ymin:ymax, xmin:xmax]) 
                else:
                    cv2.imwrite(impath,imgray[ymin:ymax, xmin:xmax]) 
 
                #if is_there_more_than_one_color(image.getdata()):
                #or image_to_string(ImageOps.invert(image))
                print "text:", text
                if text:
                    box.text = text
                    if text == name:
                        found = box
                        write_to_cache = True
                        break
                    else:
                        d[text] = box
            else:
                print "\tBOX", index, "FAILED",

    if not found:
        if d:
            for text in d:
                d[text].distance = editdistance.eval(text, name)

            #print "d:", d
            found = (sorted(d.iteritems(), key=lambda tup:tup[1].distance ) or [None])[0][1]
        else:
            found = None
    else: print "FOUND", name

    _notify("FOUND " + found.text)
 

    #CLICK THAT LOCATION
    if found:
        click_location((found.xmid,found.ymid))

    if notify:
        _notify("finished clicking " + text)

    if write_to_cache:
        with open(path_to_cache_text, "a") as f:
            f.write("\n"+name+"\t"+str(found.xmin)+"\t"+str(found.ymin)+"\t"+str(found.xmax)+"\t"+str(found.ymax))

    print "click_text took", (datetime.now()-time_started_method).total_seconds(), "seconds"

def click_image(image, notify=True):

    if notify:
        _notify("starting to click " + image) 

    if isinstance(image, str) or isinstance(image, unicode):
        template = cv2.imread(image, 0)
    elif isinstance(image, PngImageFile):
        pass # need to convert to cv2 image type

    sleep(2)

    #GET SCREENSHOT
    call(["gnome-screenshot", "--file=/tmp/beryl.png"])
    sleep(1)

    #FIND LOCATION OF NAME
    source = cv2.imread('/tmp/beryl.png', 0)

    points = []
    w, h = template.shape[::-1] 
    methods = [cv2.TM_CCOEFF,cv2.TM_CCOEFF_NORMED,cv2.TM_CCORR,cv2.TM_CCORR_NORMED,cv2.TM_SQDIFF,cv2.TM_SQDIFF_NORMED]
    for method in methods:
        # Apply Template Matching
        result = cv2.matchTemplate(source.copy(), template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        #If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        #bottom_right = (top_left[0] + w, top_left[1] + h)
        # (x,y)
        point = (  top_left[0] + (float(w)/2), top_left[1] + (float(h)/2)  )
        points.append(point)

    best_point = sorted([(point, avg_distance(point, points)) for point in points], key=lambda tup: tup[1])[0][0] 
   
    click_location(best_point) 

    if notify:
        _notify("finished clicking image")

def click_location((x,y), notify=False):

    if notify:
        _notify("clicking at " + str(x) + " " + str(y))

    call(["xdotool","mousemove",str(x),str(y),"click","1"])

    if notify:
        _notify("finishing clicking at " + str(x) + " " + str(y))



def click(x, notify=False):
    type_as_string = str(type(x))
    if isinstance(x, str) or isinstance(x, unicode):
        if x.endswith(".png") or x.endswith(".jpg"):
            click_image(x,notify=notify)
        else:
            click_text(x,notify=notify)
    elif isinstance(x, PngImageFile):
        click_image(x,notify=notify)
    elif isinstance(x, tuple):
        click_location(x,notify=notify)

def contour_to_rectangle_points(contour1, contour2):
    x,y,w,h = cv2.boundingRect(contour)
    return [[x,y],[x+w,y],[x,y+h],[x+w,y+h]]


# doesn't return the true distance
# to get that you would take the sqrt of whatever is returned
# this shortcut saves us 13 seconds when running merge on 600 boxes
def distance(p0, p1):
    #return (p0[0] - p1[0])**2 + (p0[1] - p1[1])**2
    return sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

# as a shortcut, basically calculate distance between midpoints
# this saves us 30 seconds when merging 600 boxes
def distance_between_boxes(box1, box2):
    """
    min_distance = None
    for point1 in box1.points:
        for point2 in box2.points:
            d = distance(point1, point2)
            if min_distance:
                if d < min_distance:
                    min_distance = d
            else:
                min_distance = d
    return min_distance
    """ 
    return distance([box1.xmid, box1.ymid],[box2.xmid, box2.ymid])
    # numpy method is actually slower at takes 102 seconds
    #np.linalg.norm(box1.node-box2.node)
    #return np.sum((box1.node-box2.node)**2,axis=0)
    # this takes 60 seconds
    

def merge_boxes(box1, box2):
    xmin = min(box1.xmin, box2.xmin)
    xmax = max(box1.xmax, box2.xmax)
    ymin = min(box1.ymin, box2.ymin)
    ymax = max(box1.ymax, box2.ymax)
    width = xmax - xmin
    height = ymax - ymin
    return Box((xmin, ymin, width, height))

def avg_distance(point, points):
    return median([distance(point, other_point) for other_point in points])

def _notify(text):
    call(["killall","notify-osd"])
    call(["notify-send", text])

def notify(x):

    if isinstance(x, str) or isinstance(x, unicode):
        _notify(x)

    elif hasattr(x,"__call__"):
        def wrapper(*args, **kwargs):
            func_name = x.func_name
            _notify("starting " + func_name)
            result = x(*args, **kwargs)
            _notify("finishing " + func_name)
            return result
        return wrapper

def loadCacheTextIfNecessary():
    global cache
    print "starting loadCacheTextIfNecessary"

    if "text" not in cache:
        cache_text = {}
        with open(path_to_cache_text) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    text, xmin, ymin, xmax, ymax = line.split("\t")
                    cache_text[text] = [xmin, ymin, xmax, ymax]
        cache['text'] = cache_text
