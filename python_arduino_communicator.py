import serial
import random

port_name = 'COM3' #arduino port name on your PC.
arduino = serial.Serial(port_name, 115200, timeout=.1)
while True:
	test_str = str(random.randint(0,100))
	print("sending to arduino:" + test_str)
	arduino.write((test_str+"\n").encode())
	#data = arduino.readline()
	data = arduino.readline()
	if(str(data) =="b\'\'"):
		while(True):
			data = arduino.readline()
			if(str(data)!="b\'\'"):
				break
	
	print("received from arduino:", end=' ')
	print(str(data))
	input()
	