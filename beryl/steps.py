from behave import *
from beryl import activate_window, click, notify

try: import scandir
except: from os import scandir

from os import sep

from subprocess import check_output

@when('click "{text}"')
def click_text(context, text):
    notify("starting click_text with: " + text)
    driver = context.driver if hasattr(context, "driver") else None
    click(text, webdriver=driver, debug=True)

@when('click "{text}" in the "{window_name}" window')
def click_text_in_window(context, text, window_name):
    notify("starting click_text_in_window with: " + text + " and " + window_name)
    activate_window(window_name=window_name)
    driver = context.driver if hasattr(context, "driver") else None
    click(text, webdriver=driver, window_name=window_name)
