from picamera import PiCamera
from time import sleep

import warnings
warnings.filterwarnings('default', category=DeprecationWarning)

camera = PiCamera()
camera.rotation = 180

# Capturing image to stream: https://picamera.readthedocs.io/en/release-1.13/recipes1.html

# Photo
camera.resolution = (3280, 2464)

sleep(2)

camera.capture('./photo.jpg')


