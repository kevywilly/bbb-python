#!/usr/bin/python

import socket
import sys

from utils import enum, delay, opposite
from body import Body
from leg import Leg
from joint import Joint
import numpy as np



try:
    import Adafruit_PCA9685
    #imp.find_module('Adafruit_PCA9685')
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(60)
except ImportError:
    pwm = None


MIN_PULSE_A = 110
MAX_PULSE_A = 660

MIN_PULSE_B = 150
MAX_PULSE_B = 650

DEFAULT_SPEED = 40

POFFSETS = ((0,0,0),(0,0,0),(0,0,0),(0,0,0))
COXA_MASK = np.array(((1,1,1),(-1,1,1),(1,1,1),(-1,1,1)))

NORTH = 0
SOUTH = 1
EAST = 2
WEST = 3


Heading = { 
    NORTH : { "order": [2,1,3,0], "mask": (1,1,1)},  #North
    SOUTH : { "order": [0,3,1,2], "mask":  (-1,1,1)}, #South
    EAST : { "order": [1,0,2,3], "mask": ((-1,1,1),(1,1,1),(-1,1,1),(1,1,1))}, #East
    WEST : { "order": [3,2,0,1], "mask": ((1,1,1),(-1,1,1),(1,1,1),(-1,1,1))}, #West
}


####################################### Define all Joints ###########################################
# Joint Lengths
cLen = 55
fLen = 70
tLen = 166

# Create all Joints
rfCoxa = Joint(pwm, 0,cLen, direction=1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
rfFemur = Joint(pwm, 4,fLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
rfTibia = Joint(pwm, 8,tLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)

lfCoxa = Joint(pwm, 1,cLen, direction=-1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
lfFemur = Joint(pwm, 5,fLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
lfTibia = Joint(pwm, 9,tLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)

lhCoxa = Joint(pwm, 2,cLen, direction=-1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
lhFemur = Joint(pwm, 6,fLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
lhTibia = Joint(pwm, 10,tLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)

rhCoxa = Joint(pwm, 3,cLen, direction=1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
rhFemur = Joint(pwm, 7,fLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
rhTibia = Joint(pwm, 11,tLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)

# Assign joints to legs
rfLeg = Leg(rfCoxa, rfFemur, rfTibia)
lfLeg = Leg(lfCoxa, lfFemur, lfTibia)
lhLeg = Leg(lhCoxa, lhFemur, lhTibia)
rhLeg = Leg(rhCoxa, rhFemur, rhTibia)


# Put legs into an array
body = Body(rfLeg,lfLeg,lhLeg,rhLeg)
body.set_offsets(POFFSETS)




############################ Methods ######################


def up_down_demo():
    body.send_to_home_position(speed = 10)
    for mm in [20,-20, 30,-30, 0]:
        body.set_z(mm, 5, True)
        delay(500)
        
def twist_demo():
    body.send_to_home_position(speed = 10)
    
    for x in range(1,5):
        body.set_x(20*x, 5, True)
        delay(500)
        body.set_x(-20*x,5, True)
        delay(500)
        
        body.set_x(0,5,True)
        delay(500)
    

def loop_walk(times, heading):
    for i in range(0,times):
        body.walk(lift = 40, heading = heading, speed = 50)
    
def accept_command(command):
    
    try:
        if ":" in command:
            cmd,data = command.split(":")
            data = int(data)
        else:
            cmd = command
            data = 0
            
        if cmd == "stop":
            body.send_to_home_position(80)
        elif cmd == "north":
            loop_walk(data, Heading[NORTH])
        elif cmd == "south":
            loop_walk(data, Heading[SOUTH])
        elif cmd == "east":
            loop_walk(data, Heading[EAST])
        elif cmd == "west":
            loop_walk(data, Heading[WEST])
        elif cmd == "turn":
            body.turn(stride=data)
        else:
            print >>sys.stderr, 'i do not understand command %s' % cmd
    except Exception as e:
        print e
        


def start_server():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', 8000)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    
    # Listen for incoming connections
    sock.listen(1)
    
    while True:
        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()
        
        
        try:
            print >>sys.stderr, 'connection from', client_address
    
            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                print >>sys.stderr, 'received "%s"' % data
                if data:
                    print >>sys.stderr, 'sending data back to the client'
                    #connection.sendall(data)
                    accept_command(data)
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
        
        finally:
            # Clean up the connection
            connection.close()    
    
    
def main():
    
    body.go_home()
    delay(1000)
    start_server()
    #data = 1
    #body.turn(stride=50)

if __name__ == "__main__": main()

