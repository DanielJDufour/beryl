from subprocess import call
from processor import does_command_exist

def take_a_screenshot(window_id=None):

    if window_id:

        if isinstance(window_id, int):
            window_id = str(window_id)

        path_to_screenshot = "/tmp/beryl_screenshot_of_" + window_id + ".png"
        if does_command_exist("import"):
            call(["import", "-window", window_id, path_to_screenshot,"-quiet"])

    else:

        path_to_screenshot = "/tmp/beryl.png"
        if does_command_exist("gnome-screenshot"):
            call(["gnome-screenshot", "--file="+path_to_screenshot])

    return path_to_screenshot
