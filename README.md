# breeze
Makes Writing Tests A Breeze

# explanation
This package works by taking a screenshot of your screen, using opencv to extract contours, getting text for different areas with pytesseract, using editdistance to find text that is within 1 letter, and xdotool to click that location with the passed-in text


# requirements
gnome-screenshot
python-opencv
tesseract-ocr
xdotool

# example
```
from breeze import click

# clicks button named 'Click Me!'
click("Click Me!")
```
