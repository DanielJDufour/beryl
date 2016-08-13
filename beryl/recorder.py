from multiprocessing import Process
from random import choice
from subprocess import call, Popen
from time import sleep

def convert(input_path, output_path, async=False, silent=True):
    print "starting convert"
    _args = ["ffmpeg", "-y", "-i", input_path, output_path]

    if async:
        Popen(_args)
    else:
        call(_args)

def start(path_to_video="/tmp/beryl_recording.ogv", silent=True):
    _args = ["recordmydesktop","-o",path_to_video]
    return Popen(_args)

def record(i):
    print "starting record with", i

    if hasattr(i, "__call__"):
        def wrapper(*args, **kwargs):
            print "_wrapper"
            func_name = i.func_name
            path_to_ogv = "/tmp/" + func_name + ".ogv"
            p = start(path_to_ogv)
            result = i(*args, **kwargs)
            p.terminate()
            return result
        return wrapper
 
    elif isinstance(i, str) or isinstance(i, unicode):
        _format = i.split(".")[-1]
        if _format == "ogv":
            shouldConvert = False
            path_to_ogv = i
        else:
            shouldConvert = True
            path_to_ogv = "/tmp/" + "".join([choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for x in range(4)]) + ".ogv"
 
        def outer_wrapper(f):
            print "outer_wrapper with", f
            print "i:", i
            def inner_wrapper(*args, **kwargs):
                print "inner_wrapper"
                p = start(path_to_ogv)
                result = f(*args, **kwargs)
                p.terminate()
                if shouldConvert:
                    sleep(5)
                    convert(path_to_ogv, i)
                return result
            return inner_wrapper
        return outer_wrapper

