#!/bin/bash

sudo chmod 666 /dev/ttyTHS1

mavproxy.py --master=/dev/ttyACM0,115200 --master=/dev/ttyTHS1,57600 --master=udpin:127.0.0.1:14550 --out=/dev/ttyUSB0,57600

sleep infinity
