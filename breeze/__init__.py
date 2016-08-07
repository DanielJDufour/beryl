import cv2, editdistance, numpy
from datetime import datetime
from numpy import mean
from PIL import Image
from pytesseract import image_to_string
from subprocess import call
from time import sleep

def click_text(name):

    start = datetime.now()

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
        #print "x,y", x,y
        call(["xdotool","mousemove",str(x),str(y),"click","1"])


click = click_text
