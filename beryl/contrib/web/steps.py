from behave import *
from beryl import activate_window, click

try: import scandir
except: from os import scandir

from os import sep

from subprocess import check_output

@given('loaded webpage "{url}"')
def loaded_website(context, url):
    context.driver.get(url)

@given('opened file "{filename}" in browser')
@when('open file "{filename}" in browser')
def open_file_in_browser(context, filename):

    print("starting open_file_in_browser with " + filename)

    driver = context.driver if hasattr(context, "driver") else None
    window_name = "Open File"

    # we use -print and -quit, so that we get the first match only
    command = 'find / -name "' + filename + '" -print -quit 2>&1 | grep -v "Permission denied"'

    path_to_file = check_output(command, shell=True).strip().split(sep)

    # filter out any blanks
    path_to_file = [part for part in path_to_file if part.strip()]
    print("path_to_file:", path_to_file)


    for index, part in enumerate(path_to_file):
        activate_window(window_name=window_name)
        print "trying to click part " + part
        if index == 0:
            if part == "home":
                part = part.title()
        click(part, webdriver=driver, debug=True, window_name=window_name)

    click("Open", webdriver=driver, debug=True, window_name=window_name)
