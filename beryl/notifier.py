from subprocess import call

def _notify(text):
    call(["killall","notify-osd"])
    call(["notify-send", text])

def notify(x):

    if isinstance(x, str) or isinstance(x, unicode):
        _notify(x)

    elif hasattr(x,"__call__"):
        def wrapper(*args, **kwargs):
            func_name = x.func_name
            _notify("starting " + func_name)
            result = x(*args, **kwargs)
            _notify("finishing " + func_name)
            return result
        return wrapper

