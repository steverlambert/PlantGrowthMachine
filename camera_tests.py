#!/usr/bin/env python

import time
from picamera import PiCamera


camera = PiCamera();
camera.resolution = (1296, 977)
camera.start_preview()
time.sleep(3)
camera.capture('records/image.jpg')
camera.stop_preview()
