#!/bin/bash

sudo slcand -o -c -sB /dev/ttyACM1 slcan0

sudo ip link set slcan0 down

sudo ip link set slcan0 type can bitrate 1000000

sudo ip link set slcan0 up

echo "CAN interface slcan0 is set up with a bitrate of 1 Mbps."