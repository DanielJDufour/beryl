import unittest
from datetime import datetime
from breeze import *
from time import sleep

class TestNotify(unittest.TestCase):

    @record("/tmp/test_method.gif")
    @notify
    def test_method(self):
        sleep(3)

class TestButtonClickingMethods(unittest.TestCase):

    def test_click_untitled_document(self):
        click("Untitled Document")

    @record("/tmp/clickbutton.gif")
    def test_click_button(self):
        click("Click Me!")
        sleep(5)

class TestRecording(unittest.TestCase):

    @record
    def test_record_without_path(self):
        sleep(3)

    @record("/tmp/ogvtest.ogv")
    def test_record_with_path_to_ogv(self):
        sleep(2)

    @record("/tmp/giftest.gif")
    def test_record_with_path_to_gif(self):
        sleep(2)


