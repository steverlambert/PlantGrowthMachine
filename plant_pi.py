#!/usr/bin/env python

import time
from datetime import datetime
from gpiozero import MCP3008
import smbus
import wiringpi
from picamera import PiCamera
import json
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import os
from shutil import copyfile

#### Setup Servo #####

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(18, wiringpi.GPIO.PWM_OUTPUT)
wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)

#### Pump Pin ####
wiringpi.pinMode(17, 1)

#### Setup ADC pins #####
ai0 = MCP3008(0) # moisture sensor

#### Setup I2C #####
bus = smbus.SMBus(1)
addr = 0x48
#write registers
als_conf_0 = 0x00
pow_sav = 0x03
#Read registers
als = 0x04
# These settings will provide the range for the sensor: (0 - 15099 lx)
confValues = [0x00, 0x18] # 1/4 gain, 100ms IT (Integration Time)
power_save_mode = [0x00, 0x00] # Clear values
bus.write_i2c_block_data(addr, als_conf_0, confValues)
bus.write_i2c_block_data(addr, pow_sav, power_save_mode)

class PlantController:
	def __init__(self):
		self.current_rot = 0 #position of servo
		self.current_dir = 'up' #servo rotation direction
		self.run_loop = False #auto-water loop
		self.graph_path = 'records/graph.jpg' #file name for data graph
		self.photo_path = 'records/plant.jpg' # file name for plant photo

	# Return light level in lux
	def read_lux(self):
		time.sleep(.04) # 40ms
		word = bus.read_word_data(addr,als)
		gain = 0.2304 # gain=1/4 and int time=100ms, max lux=15099 lux
		val = word * gain
		valcorr = (6.0135E-13*val**4)-(9.392E-9*val**3)+(8.1488E-5*val**2)+(1.0023E0*val)
		valcorr = round(valcorr,1) #round corrected value
		return valcorr

	# Return moisture level as a raw value (averaged over sec seconds)
	def read_moisture(self, sec):
		total = 0
		print("Finding ave. moisture over %i secs" %sec)
		for i in range(sec):
			time.sleep(1)
			total += ai0.value
			
		result = total/sec
		return result
		
	# Find brightest orientation and rotate to that position,
	# return light level and position
	def run_servo_scan(self):
		delay = .4
		
		# reset to starting position
		wiringpi.pwmWrite(18, 50)
		time.sleep(delay)
		wiringpi.pwmWrite(18,0)
		time.sleep(delay)
		
		max_lux = 0
		max_pulse = 0
		l = 0
		
		# loop through all positions
		for pulse in range(50, 250, 20):
			wiringpi.pwmWrite(18, pulse)
			time.sleep(delay)
			wiringpi.pwmWrite(18,0)
			l = self.read_lux()
			if l > max_lux:
				max_lux = l
				max_pulse = pulse
			time.sleep(delay)
		
		# set servo to max lighting location	
		wiringpi.pwmWrite(18, max_pulse)
		time.sleep(delay)
		wiringpi.pwmWrite(18,0)
		time.sleep(delay)
		self.current_rot = max_pulse
		return max_lux, (max_pulse - 50) / 20 
		
	# Rotate one position in the current direction, return position
	def rotate_plant(self):
		if self.current_dir == 'up':
			loc = self.current_rot + 20
		else:
			loc = self.current_rot - 20

		if loc > 250:
			loc = 230
			self.current_dir = 'down'
		elif loc < 50:
			loc = 70
			self.current_dir = 'up'
		
		wiringpi.pwmWrite(18, loc)
		time.sleep(.4)
		wiringpi.pwmWrite(18, 0)
		self.current_rot = loc
		return (loc-50) / 20
	
	# Run pump (via relay) for secs seconds
	def run_pump(self, secs):
		wiringpi.digitalWrite(17, 0)  
		time.sleep(1)  
		wiringpi.digitalWrite(17, 1)
		time.sleep(secs)  
		wiringpi.digitalWrite(17, 0) 
		
	# Take photo with RPi camera
	def take_photo(self):
		if self.photo_path != "records/plant.jpg":
			os.remove(self.photo_path)
		self.photo_path = 'records/photo_' + str(datetime.now()) + '.jpg'	
		
		with PiCamera() as camera:
			time.sleep(1) # camera warm-up
			camera.capture(self.photo_path, resize=(400, 320))

	# Automatic watering loop, read moisture and lux, record values,
	# run pump when moisture below threshold, loop once the given minutes
	def loop(self, minutes):
		sec = minutes * 60
		print("started loop")
		
		while(self.run_loop):
			m = self.read_moisture(1)
			l = self.read_lux()
			# moisture threshold
			if m > 0.70:
				self.run_pump(10)
			
			# record data as json
			d = {"lux" : l, "moisture" : m, "date" : format(datetime.now()) }
			f = open("records/data_record.json", "a")
			if os.stat("records/data_record.json").st_size == 0:
				f.write("[\n")
			else:
				f.write(",\n")
			f.writelines(json.dumps(d,indent=2))
			f.close()
			
			# delay
			time.sleep(sec)
		print("ended loop")
		
	# Read in json data and save to graph
	def save_data_to_graph(self):
		# copy to add the closing bracket
		copyfile('records/data_record.json', 'records/tmp.json')
		f = open('records/tmp.json', "a")
		f.write(']')
		f.close()
		
		# read and parse json file into arrays
		with open('records/tmp.json') as json_file:
			data = json.load(json_file)
			
		lux = []
		mois = []
		time = []

		for reading in data:
			lux.append(reading["lux"])
			mois.append(reading["moisture"])
			time.append(datetime.strptime(reading["date"].split('.')[0], '%Y-%m-%d %H:%M:%S'))
	
		start = time[0]
		end = time[-1]
		
		# create and format plots
		fig, ax = plt.subplots(2, figsize=(8,8), sharex=True)
		ax[0].plot(time, lux)
		ax[1].plot(time, mois)
		ax[0].set_ylabel("Light Level (Lux)")
		ax[1].set_ylabel("Dryness Level")
		ax[1].set_ybound(upper=0.9)
		plt.xlabel("Date (m-d h)")
		#plt.suptitle("Plant Data from " + str(start) + " to " +  str(end))
		plt.tight_layout()
		
		# save graphs to file
		if self.graph_path != "records/graph.jpg":
			os.remove(self.graph_path)
		self.graph_path = 'records/graph_' + str(datetime.now()) + '.jpg'
		plt.savefig(self.graph_path)
