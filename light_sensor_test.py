#!/usr/bin/env python

import smbus
import time

bus = smbus.SMBus(1)

addr = 0x48

#Write registers
als_conf_0 = 0x00
#als_WH = 0x01
#als_WL = 0x02
pow_sav = 0x03

#Read registers
als = 0x04
#white = 0x05
#interrupt = 0x06


# These settings will provide the range for the sensor: (0 - 15099 lx)
#
# LSB MSB
confValues = [0x00, 0x18] # 1/4 gain, 100ms IT (Integration Time)


#Reference data sheet Table 1 for configuration settings
#MSB = 00011000 = 18 in hexadecimal ( als gain = 1/4, bits 12:11 = 11 )
#LSB = 00000000 = 00 ( integration time = 100ms, bits 9:6 = 0000 )

#interrupt_high = [0x00, 0x00] # Clear values
#Reference data sheet Table 2 for High Threshold

#interrupt_low = [0x00, 0x00] # Clear values
#Reference data sheet Table 3 for Low Threshold

power_save_mode = [0x00, 0x00] # Clear values
#Reference data sheet Table 4 for Power Saving Modes

bus.write_i2c_block_data(addr, als_conf_0, confValues)
#bus.write_i2c_block_data(addr, als_WH, interrupt_high)
#bus.write_i2c_block_data(addr, als_WL, interrupt_low)
bus.write_i2c_block_data(addr, pow_sav, power_save_mode)


max = 0

while True:
	#The frequency to read the sensor should be set greater than
	# the integration time (and the power saving delay if set).
	# Reading at a faster frequency will not cause an error, but
	# will result in reading the previous data
	time.sleep(.04) # 40ms

	word = bus.read_word_data(addr,als)
	# wordIR = bus.read_word_data(addr,white)

	gain = 0.2304 # gain=1/4 and int time=100ms, max lux=15099 lux


	#Reference www.vishay.com/docs/84367/designingveml6030.pdf
	# 'Calculating the LUX Level'

	val = word * gain
	#valIR = wordIR * gain
	#val = round(val,1)
	#valIR = round(valIR,1)

	#Reference www.vishay.com/docs/84367/designingveml6030.pdf
	# 'Calculating the LUX Level'

	valcorr = (6.0135E-13*val**4)-(9.392E-9*val**3)+(8.1488E-5*val**2)+(1.0023E0*val)
	valcorr = round(valcorr,1) #Round corrected value for presentation
	val = round(val,1) #Round value for presentation
	
	if val > max: 
		max = val
		print("New Record! -", max)

	print ("Measures: " + str(val) + " Lux" , str(valcorr) + "lux corrected")
