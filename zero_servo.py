#!/usr/bin/env python

import wiringpi
from time import sleep

wiringpi.wiringPiSetupGpio()

wiringpi.pinMode(17, 1)

wiringpi.digitalWrite(17, 0) # sets port 24 to 0 (0V, off)  
sleep(5)                    # wait 10s  
wiringpi.digitalWrite(17, 1) # sets port 24 to 1 (3V3, on)  
sleep(5)                    # wait 10s  
wiringpi.digitalWrite(17, 0) # sets port 24 to 0 (0V, off)  
