# breeze
Makes Writing Tests A Breeze

# explanation
This package works by using machine vision, optical character recognition, levenshtein distance and some custom code.


# requirements
On Ubuntu or any system using Apt Package Manager, install the required system-level packages with the following:
```
sudo apt-get install ffmpeg gnome-screenshot recordmydesktop python-opencv tesseract-ocr xdotool
```
On any system with PIP installed, install the Python packages with the following:
```
sudo pip install editdistance Pillow pytesseract
```

# examples
## click
![gif showing click in action](https://raw.githubusercontent.com/DanielJDufour/breeze/master/gifs/clickbutton.gif)
```
from breeze import click

# clicks any button on screen named 'Click Me!'
click("Click Me!")
```
## notify
![gif showing notify in action](https://raw.githubusercontent.com/DanielJDufour/breeze/master/gifs/notify.gif)
```
from breeze import notify
from time import sleep

# notifies you when a method is starting and finishing
@notify
def test_method():
    sleep(3)
```

##record
```
from breeze import record
from time import sleep

# records the screen when your method is running
@record
def test_method():
    sleep(3)
    
# used by
[First Draft GIS](http://firstdraftgis.com)
