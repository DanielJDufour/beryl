# beryl
beryl makes writing tests better, super easy and quick

# explanation
This package works by using machine vision, optical character recognition, levenshtein distance and some custom code.

# install
```
pip install beryl
```

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
![gif showing click in action](https://raw.githubusercontent.com/DanielJDufour/beryl/master/gifs/clickbutton.gif)
```
from beryl import click

# clicks any button on screen named 'Click Me!'
click("Click Me!")
```
## notify
![gif showing notify in action](https://raw.githubusercontent.com/DanielJDufour/beryl/master/gifs/notify.gif)
```
from beryl import notify
from time import sleep

# notifies you when a method is starting and finishing
@notify
def test_method():
    sleep(3)
```

##record
```
from beryl import record
from time import sleep

# records the screen when your method is running
@record
def test_method():
    sleep(3)
```

## selenium
Selenium is a great tool but sometimes it's helpful to send a system-level mouse click event to a window.  Here's an example of what to do when a window pops up in Firefox saying that your script is taking too long.
```
from beryl import click
from selenium import webdriver

driver = webdriver.Firefox()
.
.
.

click("Stop script", webdriver=driver)

```

## window_name
If you know the name of the window, like "Open File", you can pass in the window name to the click method.
```
from beryl import click

click("Search", window_name="Open File")
```

# used by
- [First Draft GIS](https://firstdraftgis.com)
- [GeoTIFF.io](https://geotiff.io)
