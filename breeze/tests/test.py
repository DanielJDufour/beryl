import unittest
from datetime import datetime
from breeze import *

class TestButtonClickingMethods(unittest.TestCase):

    def test_click_untitled_document(self):
        click_button("Untitled Document")

    def test_click_next(self):
        click_text("Next")
