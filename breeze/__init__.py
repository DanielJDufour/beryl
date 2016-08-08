import cv2, editdistance, numpy
from datetime import datetime
from math import sqrt
from numpy import mean, median
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from pytesseract import image_to_string
from subprocess import call, Popen
from time import sleep

# notes
# probably need some sort of caching mechanism
# so don't have to rerun everything if doing repeated
# actions like clicking on a certain button
# maybe look at old location first and if don't find
# there, then run again??


# maybe need to train on an image before search for it

def is_text_on_screen(target, notify=True):

    if notify:
        _notify("starting is_text_on_screen")

    if isinstance(target, str):
        target = target.decode('utf-8')

    #GET SCREENSHOT
    call(["gnome-screenshot", "--file=/tmp/breeze.png"])
    sleep(1)

    #FIND TEXTS
    im = cv2.imread('/tmp/breeze.png')
    im = cv2.resize(im, (0,0), fx=2, fy=2)
    imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    #ret,thresh = cv2.threshold(imgray,127,255,0)
    ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for index, contour in enumerate(contours):
        location = cv2.boundingRect(contour)
        x,y,w,h = location
        if w > 10 and h > 6:
            cropped = im[y:y+h, x:x+w]
            text = image_to_string(Image.fromarray(cropped))
            print("text:", text)
            if target in text.decode("utf-8"):
                return True

def click_text(name, notify=True):

    if notify:
        _notify("starting to click " + name) 

    sleep(2)

    #GET SCREENSHOT
    call(["gnome-screenshot", "--file=/tmp/breeze.png"])
    sleep(1)

    #FIND LOCATION OF NAME
    im = cv2.imread('/tmp/breeze.png')
    imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    found_location = None
    d = {}
    for index, contour in enumerate(contours):
        location = cv2.boundingRect(contour)
        x,y,w,h = location
        if w > 10 and h > 6:
            cropped = im[y:y+h, x:x+w]
            text = image_to_string(Image.fromarray(cropped))
            if text:
                if text == name:
                    found_location = location
                    break
                else:
                    d[text] = {"location": location, "text": text}

    #print "FOUND", name, "at", found_location
    if not found_location:
        for text in d:
            d[text]['distance'] = editdistance.eval(text, name)

        #print "d:", d
        found_location = (sorted(d.iteritems(), key=lambda tup:tup[1]['distance'] ) or [None])[0][1]['location']

    #print "FOUND_LOCATION:", found_location
 

    #CLICK THAT LOCATION
    if found_location:
        x = found_location[0] + (float(found_location[2]) / 2)
        y = found_location[1] + (float(found_location[3]) / 2)
        click_location((x,y))

    if notify:
        _notify("finished clicking " + text)

def click_image(image, notify=True):

    if notify:
        _notify("starting to click " + image) 

    if isinstance(image, str) or isinstance(image, unicode):
        template = cv2.imread(image, 0)
    elif isinstance(image, PngImageFile):
        pass # need to convert to cv2 image type

    sleep(2)

    #GET SCREENSHOT
    call(["gnome-screenshot", "--file=/tmp/breeze.png"])
    sleep(1)

    #FIND LOCATION OF NAME
    source = cv2.imread('/tmp/breeze.png', 0)

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

def distance(p0, p1):
    return sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

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
