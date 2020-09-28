#!/usr/bin/env python

import time
import wiringpi

wiringpi.wiringPiSetupGpio()

wiringpi.pinMode(18, wiringpi.GPIO.PWM_OUTPUT)

wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)

# divide down clock
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)

delay_period = 1
speed = 50 #50 to 250
steps = 10

print("Setting up")
time.sleep(.5)
for i in range(50, 260, 10):
	print("step: ", i)
	wiringpi.pwmWrite(18, i)
	time.sleep(.2)
	#print("stopping")
	wiringpi.pwmWrite(18,0)
	time.sleep(.2)

wiringpi.pwmWrite(18,50)

#for pulse in range(50, 250, 5):
#        print(pulse)
#	wiringpi.pwmWrite(18, pulse)
#        time.sleep(delay_period)
		
#        for pulse in range(250, 50, -1):
#                wiringpi.pwmWrite(18, pulse)
#                time.sleep(delay_period)
