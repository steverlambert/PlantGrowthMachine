#!/usr/bin/env python

import time
from gpiozero import MCP3008

ai0 = MCP3008(0)
#ai1 = MCP3008(1)

while True:
	#print("Resistive Sensor: ",  ai1.value)
	print("Capacitive Sensor: ", ai0.value)
	print('\n')
	time.sleep(1)
