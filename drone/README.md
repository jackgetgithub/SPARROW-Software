Before running the sendcv.py, please make sure you have the dependencies installed on the drone (Linux Ubuntu 22.04)

Assuming you have python installed first, follow these libraries installation as well
Open CV on python:
pip install opencv-python

Pymavlink on python:
pip install pymavlink

All in one line:
pip install opencv-python pymavlink

############

The code on the drone will incorporate the sending scripts which are sending its data to the udpout port of 14550 (udpout:127.0.0.1:14550)
Our MAVProxy on the drone will utilize the masters as the udp port for the image meta data alongside the serial ports from the flight controller. The out port is the radio modem to transmit to the base station.

Start with installing MAVProxy:
pip install MAVProxy

Now run the MAVProxy command on the drone in a terminal, the port for the modem is done via a serial connection and please make sure baud rate and port is correct!!
Throughout this project, the Jetson Nano was used as the companion computer on the drone, we used the UART pins 8 and 10 for TX and RX which was located at the port /dev/ttyTHS1
The port for the Flight Controller was connected to the PixHawk on the drone, though it was connected to one of the USB ports on the Jetson Nano, its port varied on the Nano.
Sometimes the port for the PixHawk was /dev/ttyACM0 while other times maybe a different number like /dev/ttyACM1 or even different port such as /dev/ttyUSB0 so be careful with this setup
Flight Controller was assigned 115200 as baud rate whereas the modems are still being used at their default 57600 baud rate
MAVProxy command line:
mavproxy.py --master=udpin:127.0.0.1:14550 --master=/dev/ttyACM0,115200 --out=/dev/ttyTHS1,57600
