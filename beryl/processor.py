from subprocess import call, check_output

def does_command_exist(command):
    return call(["which",command]) != 1

def is_command_running(command):
    return command in check_output(["ps","aux"])

def wait_until_command_is_not_running(command):
    while True:
        if not is_command_running(command):
            break
