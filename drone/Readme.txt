Before running the sendcv.py, please make sure you have the dependencies installed on the drone (Linux Ubuntu 22.04)

Assuming you have python installed first, follow these libraries installation as well
Open CV on python:
pip install opencv-python

Pymavlink on python:
pip install pymavlink

All in one line:
pip install opencv-python pymavlink

############

Since the code is listening for the udp port rather than directly from the radio modem, we must set up a MAVProxy routing protocol that would route the modem data to the UDP ports
The MAVProxy routing is done so that MissionPlanner is listening to the default UDP port of udpin:127.0.0.1:14550 and the GUI is listening to a different UDP port which is 14552 in our case

Start with installing MAVProxy:
pip install MAVProxy

Now run the MAVProxy command on the base in a terminal, the port for the modem is done via a serial connection and please make sure baud rate and port is correct!!
Throughout this project, the Jetson AGX Orin was used as the base station, we used the UART pins 8 and 10 for TX and RX which was located at the port /dev/ttyTHS1
MAVProxy command line:
mavproxy.py --master=/dev/ttyTHS1,57600 --out=udpout:127.0.0.1:14550 --out=udpout:127.0.0.1:14552
