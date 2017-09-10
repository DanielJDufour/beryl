import cv2, editdistance, numpy
from boxerator import merge_boxes, Box
from collections import defaultdict
from datetime import datetime
from numpy import amin, argmin, asarray, triu_indices
import numpy as np
from notifier import notify, _notify
from os.path import abspath, dirname
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngImageFile
from processor import does_command_exist, is_command_running, wait_until_command_is_not_running
from psutil import Process
from pytesseract import image_to_string
from scipy.spatial.distance import cdist, pdist
import shlex
from subprocess import call, check_output, Popen
from screenshooter import take_a_screenshot
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

def find_contours(a, b, c, debug=True):
    results = cv2.findContours(a, b, c)
    number_of_results = len(results)
    if debug: print("number_of_results:", number_of_results)
    if number_of_results == 2:
        return results
    elif number_of_results == 3:
        return results[1:3]

def is_there_more_than_one_color(data):
    color = data[0]
    for pixel in data:
        if pixel != color:
            return True
    return False

def is_text_on_screen(target, notify=True):

    if notify:
        _notify("starting is_text_on_screen")

    if isinstance(target, str):
        target = target.decode('utf-8')

    #GET SCREENSHOT
    path_to_screenshot = take_a_screenshot()
    sleep(1)

    #FIND TEXTS
    im = cv2.imread(path_to_screenshot)
    im = cv2.resize(im, (0,0), fx=2, fy=2)
    imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    #ret,thresh = cv2.threshold(imgray,127,255,0)
    ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)
    contours, hierarchy = find_contours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


    for index, contour in enumerate(contours):
        b = Box(cv2.boundingRect(contour))
        if b.width > 10 and b.height > 6:
            cropped = im[b.ymin:b.ymax, b.xmin:b.xmax]
            text = image_to_string(Image.fromarray(cropped))
            print("text:", text)
            if target in text.decode("utf-8"):
                return True
    return False

def click_text(name, notify=True, use_cache=True, pid=None, pids=None, window_id=None, log=False, window_name=None, debug=False):
    global cache


    found = None
    write_to_cache = False
    paths_to_screenshots = []
    screenshots = []
    window_ids = []

    print "[beryl] starting click_text with", name
    if debug: print("\t[beryl] pid: " + str(pid))
    if debug: print("\t[beryl] pids: " + str(pids))
    if debug: print("\t[beryl] window_name: " + str(window_name))
    time_started_method = datetime.now()

    loadCacheTextIfNecessary()

    if notify:
        _notify("starting to click " + name)
        sleep(1)
        call(["killall","notify-osd"])
        sleep(0.5)

    # adds the window_id to the list of window_ids
    # this gives priority to this window
    if window_id:
        window_ids.append(window_id)

    pids_as_strings = set()
    if pid:
        pids_as_strings.add(str(pid))

    if pids:
        for pid in pids:
            pids_as_strings.add(str(pid))


    windows = get_list_of_windows()

    if windows:
        for window_id, info in windows:
            test1 = any(p in info for p in pids_as_strings) if pids_as_strings else True
            test2 = window_name in info if window_name else True
            if test1 and test2:
                if window_id not in window_ids:
                    window_ids.append(window_id)

    print("wids:", window_ids)
    #raw_input("pausing")

    #GET SCREENSHOT
    if window_ids:
        for window_id in window_ids:
            paths_to_screenshots.append(take_a_screenshot(window_id=window_id))
    else:
        paths_to_screenshots.append(take_a_screenshot())
    sleep(0.5)


    for path_to_screenshot in paths_to_screenshots:
        imgray = cv2.cvtColor(cv2.imread(path_to_screenshot),cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)
        screenshots.append({"imgray":imgray, "thresh": thresh})

    """
    disabling cache until can figure out bugs
    should double check and see if cache is correct before skipping ocr
    # try to see if we can get lucky and we've seen this before, so we can use cache
    if name in cache['text']:
        print "NAME IN CACHE TEXT"
        for index, dict_of_screenshots in enumerate(screenshots):
            imgray = dict_of_screenshots['imgray']
            thresh = dict_of_screenshots['thresh']
            xmin, ymin, xmax, ymax = [int(_) for _ in cache['text'][name]]

            try:
                text = image_to_string(Image.fromarray(imgray[ymin:ymax, xmin:xmax])) or image_to_string(Image.fromarray(thresh[ymin:ymax, xmin:xmax]))
            except Exception as e:
                print(e.message + " with [ymin, ymax, xmin, xmax] = " + str([ymin, ymax, xmin, xmax]))
                text = None

            if not text:
                # pad coordinates by 2 pixels
                if xmax <= box.width - 2: xmax += 2
                if xmin >= 2: xmin -= 2
                if ymin >= 2: ymin -= 2
                if ymax <= box.height - 2: ymax += 2
                try:
                    text = image_to_string(Image.fromarray(imgray[ymin:ymax, xmin:xmax])) or image_to_string(Image.fromarray(thresh[ymin:ymax, xmin:xmax]))
                except Exception as e:
                    print(e.message + " with [ymin, ymax, xmin, xmax] = " + str([ymin, ymax, xmin, xmax]))
                    text = None

            #print "\ttext:", text

            if text == name:
                found = Box((xmin, ymin, xmax-xmin, ymax-ymin))
                found.index = index
                found.text = text
    """

    if found is None:
        for index_of_screenshot, dict_of_screenshots in enumerate(screenshots):
            imgray = dict_of_screenshots['imgray']
            thresh = dict_of_screenshots['thresh']
            contours, hierarchy = find_contours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            #cv2.imwrite('/tmp/thresh.png',thresh)
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

            # use nearest neighbor like algorithm to merge boxes
            for parent in parent_children:
                children = parent_children[parent]
                number_of_children = len(children)
                #print "number_of_children:", number_of_children
                while len(children) > 1:
                    number_of_children = len(children)
                    nodes = [child.node for child in children]

                    a = argmin(pdist(nodes, 'euclidean'))
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
            boxes = sorted(boxes, key=lambda box: box.area)
            print "sorted boxes by area"

            d = {}
            minimum_width = 5 * len(name)
            print "minimum width:", minimum_width
            print "number of boxes:", len(boxes)
            for index_of_box, box in enumerate(boxes):
                # ignore if data all one color

                if minimum_width < box.width < 500 and 10 < box.height < 500:
                    #print "\tBOX", index, "PASSED",
                    impath = "/tmp/"+str(index_of_box)+".png"
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
                    #print "text:", text
                    if text:
                        box.text = text
                        box.index = index_of_screenshot
                        if text == name:
                            found = box
                            write_to_cache = True
                            break
                        else:
                            d[text] = box
                #else:
                    #print "\tBOX", index, "FAILED",

    if not found:
        if d:
            for text in d:
                d[text].distance = editdistance.eval(text, name)

            #print "d:", d
            found = (sorted(d.iteritems(), key=lambda tup:tup[1].distance ) or [None])[0][1]
        else:
            found = None
    else:
        print "FOUND", name

    if notify:
        _notify("FOUND " + found.text + " for '" + name + "'")

    if debug:
        print("xmid", found.xmid)
        print("ymid", found.ymid)
        print("window_id:", window_id)

    #CLICK THAT LOCATION
    if found:
        if window_id:
            click_location((found.xmid,found.ymid), window_id=window_ids[found.index])
        else:
            click_location((found.xmid,found.ymid))

    if notify:
        _notify("finished clicking " + found.text + " for '" + name + "'")

    if write_to_cache:
        with open(path_to_cache_text, "a") as f:
            f.write("\n"+name+"\t"+str(found.xmin)+"\t"+str(found.ymin)+"\t"+str(found.xmax)+"\t"+str(found.ymax))

    if debug:
        print "\nclicked text", found.text, "for", name
        print "\nclick_text took", (datetime.now()-time_started_method).total_seconds(), "seconds"


def find_text(name, notify=True, use_cache=True, pid=None, pids=None, window_id=None, log=False, window_name=None, debug=False):
    global cache

    found = None
    write_to_cache = False
    paths_to_screenshots = []
    screenshots = []
    window_ids = []

    print "[beryl] starting find_text with", name
    if debug: print("\t[beryl] pid: " + str(pid))
    if debug: print("\t[beryl] pids: " + str(pids))
    if debug: print("\t[beryl] window_name: " + str(window_name))
    time_started_method = datetime.now()

    loadCacheTextIfNecessary()

    if notify:
        _notify("starting to find " + name)
        sleep(1)
        call(["killall","notify-osd"])
        sleep(0.5)

    # adds the window_id to the list of window_ids
    # this gives priority to this window
    if window_id:
        window_ids.append(window_id)

    pids_as_strings = set()
    if pid:
        pids_as_strings.add(str(pid))

    if pids:
        for pid in pids:
            pids_as_strings.add(str(pid))


    windows = get_list_of_windows()

    if windows:
        for window_id, info in windows:
            test1 = any(p in info for p in pids_as_strings) if pids_as_strings else True
            test2 = window_name in info if window_name else True
            if test1 and test2:
                if window_id not in window_ids:
                    window_ids.append(window_id)

    print("wids:", window_ids)
    #raw_input("pausing")

    #GET SCREENSHOT
    if window_ids:
        for window_id in window_ids:
            paths_to_screenshots.append(take_a_screenshot(window_id=window_id))
    else:
        paths_to_screenshots.append(take_a_screenshot())
    sleep(0.5)

    if debug: print("path_to_screenshots:", path_to_screenshots)
    for path_to_screenshot in paths_to_screenshots:
        try:
            im = cv2.imread(path_to_screenshot)
            imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
            ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)
            screenshots.append({"imgray":imgray, "thresh": thresh})
        except Exception as e:
            print("e:", e)

    # try to see if we can get lucky and we've seen this before, so we can use cache
    if name in cache['text']:
        print "NAME IN CACHE TEXT"
        for index, dict_of_screenshots in enumerate(screenshots):
            imgray = dict_of_screenshots['imgray']
            thresh = dict_of_screenshots['thresh']
            xmin, ymin, xmax, ymax = [float(_) for _ in cache['text'][name]]
            text = image_to_string(Image.fromarray(imgray[ymin:ymax, xmin:xmax])) or image_to_string(Image.fromarray(thresh[ymin:ymax, xmin:xmax]))
            if not text:
                # pad coordinates by 2 pixels
                if xmax <= box.width - 2: xmax += 2
                if xmin >= 2: xmin -= 2
                if ymin >= 2: ymin -= 2
                if ymax <= box.height - 2: ymax += 2
                text = image_to_string(Image.fromarray(imgray[ymin:ymax, xmin:xmax])) or image_to_string(Image.fromarray(thresh[ymin:ymax, xmin:xmax]))
            #print "\ttext:", text

            if text == name:
                found = Box((xmin, ymin, xmax-xmin, ymax-ymin))
                found.index = index
                found.text = text

    if found is None:
        for index_of_screenshot, dict_of_screenshots in enumerate(screenshots):
            imgray = dict_of_screenshots['imgray']
            thresh = dict_of_screenshots['thresh']
            contours, hierarchy = find_contours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0 and len(hierarchy) > 0:
                #cv2.imwrite('/tmp/thresh.png',thresh)
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

                # use nearest neighbor like algorithm to merge boxes
                for parent in parent_children:
                    children = parent_children[parent]
                    number_of_children = len(children)
                    #print "number_of_children:", number_of_children
                    while len(children) > 1:
                        number_of_children = len(children)
                        nodes = [child.node for child in children]

                        a = argmin(pdist(nodes, 'euclidean'))
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
                boxes = sorted(boxes, key=lambda box: box.area)
                print "sorted boxes by area"

                d = {}
                minimum_width = 5 * len(name)
                print "minimum width:", minimum_width
                print "number of boxes:", len(boxes)
                for index_of_box, box in enumerate(boxes):
                    # ignore if data all one color

                    if minimum_width < box.width < 500 and 10 < box.height < 500:
                        #print "\tBOX", index, "PASSED",
                        impath = "/tmp/"+str(index_of_box)+".png"
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
                            box.index = index_of_screenshot
                            if text == name:
                                found = box
                                write_to_cache = True
                                break
                            else:
                                d[text] = box
                    #else:
                        #print "\tBOX", index, "FAILED",

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

    if notify:
        _notify("finished finding " + found.text)

    if write_to_cache:
        with open(path_to_cache_text, "a") as f:
            f.write("\n"+name+"\t"+str(found.xmin)+"\t"+str(found.ymin)+"\t"+str(found.xmax)+"\t"+str(found.ymax))
    #if log:
    if True:
        print "\nfound text", found.text
        print "\nfound_text took", (datetime.now()-time_started_method).total_seconds(), "seconds"

    return found

#         When  "https://geotiff.io/data/example_4326.tif" into box for "URL to Your GeoTIFF"

def type_text_into_box(text, box_name, debug=True, box_location="under"):
    print "starting click_box_under_text"
    found_text = find_text(text)
    print "[click_box_under_text] found ", found
    found_boxes = find_boxes()
    #XXXX
    # find box that is shortest distance from being under the text


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

def click_location((x,y), notify=False, window_id=None, debug=True):

    if notify:
        _notify("clicking at " + str(x) + " " + str(y))

    window_id = str(window_id)

    if does_command_exist("xdotool"):

        # want to make sure not moving mouse one way
        # while another process is moving it another way
        wait_until_command_is_not_running("xdotool")
        if window_id:
            call(shlex.split("xdotool windowfocus " + window_id))
            call(shlex.split("xdotool windowactivate " + window_id))
            # can't use window param for click because Chrome doesn't recognize click with it
            _args = ["xdotool","mousemove","--sync","--window", window_id, str(x),str(y),"click","--repeat", "2", "1"]
        else:
            _args = ["xdotool","mousemove","--sync",str(x),str(y),"click","1"]
        if debug:
            print("_args:", _args)
            print("command:", " ".join(_args))
        call(_args)
        #raw_input("PAUSED")
    else:
        raise Exception("UH OH! You don't have any software installed that can be used to click a location on your screen.  We recommend installing xdotool.")

    if notify:
        _notify("finishing clicking at " + str(x) + " " + str(y))



def click(x, notify=False, pid=None, pids=None, webdriver=None, window_name=None, debug=False):

    if debug:
        print("[beryl] starting click")
        print("\tpid: " + str(pid))
        print("\twebdriver: " + str(webdriver))
        print("\twindow_name: " + str(window_name))
        print("\tstr(type(webdriver)): " + str(type(webdriver)))

    type_as_string = str(type(x))

    webdriver_type_as_string = str(type(webdriver))
    if webdriver_type_as_string == "<class 'selenium.webdriver.firefox.webdriver.WebDriver'>":
        pids = [webdriver.binary.process.pid]
    elif webdriver_type_as_string == "<class 'selenium.webdriver.chrome.webdriver.WebDriver'>":
        process = Process(webdriver.service.process.pid)
        if hasattr(process, "children"):
            pids = [p.pid for p in process.children()]
        elif hasattr(process, "get_children"):
            pids = [p.pid for p in process.get_children()]


    if isinstance(x, str) or isinstance(x, unicode):
        if x.endswith(".png") or x.endswith(".jpg"):
            click_image(x, notify=notify)
        else:
            click_text(x, notify=notify, pids=pids, window_name=window_name, debug=debug)
    elif isinstance(x, PngImageFile):
        click_image(x,notify=notify)
    elif isinstance(x, tuple):
        click_location(x,notify=notify)

def activate_window(window_id=None, window_name=None):

    if not window_id:
        windows = get_list_of_windows()
        for wid, info in windows:
            info_ascii = [character for character in info if ord(character) < 128]
            if window_name in info_ascii:
                window_id = wid
                break

    if does_command_exist("wmctrl"):
        call(shlex.split("xdotool windowfocus --sync " + str(window_id)))

def get_list_of_windows(debug=True):
    if debug: print "starting get_list_of_windows"
    if does_command_exist("wmctrl"):
        windows = [ [line.split()[0], line] for line in check_output(["wmctrl","-lp"]).split("\n") if line ]
    else:
        raise Exception("no ability to get windows. install wmctrl")
    if debug: print "finishing get_list_of_windows"
    return windows


def press_key(key, window_id=None, window_name=None):

    if notify:
        _notify("pressing " + key)

    if window_name and not window_id:
        windows = get_list_of_windows()
        for wid, info in windows:
            if window_name in info:
                window_id = wid
                break

    if does_command_exist("xdotool"):

        # want to make sure not moving mouse one way
        # while another process is moving it another way
        wait_until_command_is_not_running("xdotool")
        if window_id:
            command = "xdotool key --window '" + str(window_id) + "' " + key
            print "running command:", command
            call(shlex.split(command))
        else:
            call(shlex.split("xdotool key " + key))
    else:
        raise Exception("UH OH! You don't have any software installed that can be used to press enter.  We recommend installing xdotool.")

    if notify:
        _notify("finishing pressing key " + key)

def press_enter(window_id=None, window_name=None):
    press_key(key="Return", window_id=window_id, window_name=window_name)

def press_backspace(window_id=None, window_name=None):
    press_key(key="BackSpace", window_id=window_id, window_name=window_name)


def type_text(text, notify=False, window_id=None, window_name=None):

    if notify:
        _notify("typing text '" + text + "'")

    if window_name and not window_id:
        windows = get_list_of_windows()
        for wid, info in windows:
            if window_name in info:
                window_id = wid
                break

    if does_command_exist("xdotool"):

        # want to make sure not moving mouse one way
        # while another process is moving it another way
        wait_until_command_is_not_running("xdotool")
        if window_id:
            command = "xdotool type --window '" + str(window_id) + "' '" + text + "'"
            print "running command:", command
            call(shlex.split(command))
        else:
            call(shlex.split("xdotool type '" + text + "'"))
    else:
        raise Exception("UH OH! You don't have any software installed that can be used to click a location on your screen.  We recommend installing xdotool.")

    if notify:
        _notify("finishing typing text")

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
