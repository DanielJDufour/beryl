from behave import *
import cv2
from beryl.contrib.geo import find_squares
from beryl.screenshooter import take_a_screenshot
from subprocess import call
from time import sleep

@when("raster appears")
@then("raster appears")
def raster_appears(context):
    path_to_screenshot = take_a_screenshot()
    print("path_to_screenshot:", path_to_screenshot)
    sleep(3)
    img = cv2.imread(path_to_screenshot)
    squares = find_squares(img)
    number_of_squares = len(squares)
    try:
        assert number_of_squares > 50
    except Exception as e:
        raise Exception(e.message + " with " + str(number_of_squares) + " squares")
