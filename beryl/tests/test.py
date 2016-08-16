import unittest
from datetime import datetime
from beryl import *
from os.path import abspath, dirname
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from settings import *
from time import sleep

path_to_this_directory = dirname(abspath(__file__))

def setUpModule():
    global driver

    print "starting setUpModule"
    call( [ "killall", "-9", "chrome" ] )
    options = Options()
    options.add_extension(path_to_chrome_extension)
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(executable_path=path_to_chrome_driver, chrome_options=options)
    print "finished setUpModule"

def tearDownModule():
    #global driver
    driver.quit() 

class TestNotify(unittest.TestCase):

    @record("/tmp/test_method.gif")
    @notify
    def test_method(self):
        sleep(3)

class TestButtonClickingMethods(unittest.TestCase):

    def test_click_untitled_document(self):
        click("Untitled Document")

    #@record("/tmp/clickbutton.gif")
    def test_click_button(self):
        path_to_example = path_to_this_directory + "/examples/click_me_test.html"
        driver.get("file://" + path_to_example)
        sleep(2)
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


class TestWindow(unittest.TestCase):

    @record("/tmp/window.gif", delay=5)
    def test_click_script_timeout_firefox(self):
        driver = webdriver.Firefox()
        sleep(1)
        driver.maximize_window()
        sleep(1)
        notify("executing runaway script")
        driver.execute_script("while(true){console.log('running');}")
        sleep(1)
        click("Stop script", webdriver=driver)
        assert is_text_on_screen("Stop Script") == False
        notify("stopped script")
        sleep(1)
