#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

# Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

# Set pin 11 as an output, and set servo1 as pin 11 as PWM
GPIO.setup(11,GPIO.OUT)
servo1 = GPIO.PWM(11,50) # Note 11 is pin, 50 = 50Hz pulse

#start PWM running, but with value of 0 (pulse off)
servo1.start(0)
print ("Duty at 0 - Waiting for 2 seconds")
time.sleep(2)


# Define variable duty
duty = 2
#print("changing duty to ", duty)
#servo1.ChangeDutyCycle(duty)
#time.sleep(1)

# Loop for duty values from 2 to 12 (0 to 180 degrees)
while duty <= 12:
    servo1.ChangeDutyCycle(duty)
    #print("duty at: ", duty)
    time.sleep(.3)
    servo1.ChangeDutyCycle(0)
    time.sleep(.7)
    duty = duty + 2

#servo1.ChangeDutyCycle(0)
#time.sleep(5)

#while duty >= 2:
#    servo1.ChangeDutyCycle(duty)
#    time.sleep(.3)
#    duty = duty - 1

#turn back to 0 degrees
print ("Turning back to 0 degrees")
time.sleep(0.5)
servo1.ChangeDutyCycle(2)
time.sleep(0.5)
servo1.ChangeDutyCycle(0)


print ("finishing")
time.sleep(2)

#Clean things up at the end
servo1.stop()
GPIO.cleanup()
print ("Goodbye")


