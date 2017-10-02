from subprocess import call, Popen
from processor import does_command_exist

def take_a_screenshot(window_id=None, debug=False):

    if window_id:

        if isinstance(window_id, int):
            window_id = str(window_id)

        path_to_screenshot = "/tmp/beryl_screenshot_of_" + window_id + ".png"
        if does_command_exist("import"):
            print("taking a screenshot with import")
            call(["import", "-window", window_id, path_to_screenshot,"-quiet"])
            if debug: Popen(["shotwell", path_to_screenshot])

    else:

        path_to_screenshot = "/tmp/beryl.png"
        if does_command_exist("gnome-screenshot"):
            print("taking a screenshot with gnome-screenshot")
            call(["gnome-screenshot", "--file="+path_to_screenshot])
            if debug: Popen(["shotwell", path_to_screenshot])

    return path_to_screenshot
