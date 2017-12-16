#!/usr/bin/python

import socket
import sys
import os
from utils import enum, delay, opposite
from body import Body
from leg import Leg
from joint import Joint
from command import Command
import numpy as np
import struct
import json
from jsonsocket import Server




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

DEFAULT_SPEED = 30

COXA_MASK = np.array(((1,1,1),(-1,1,1),(1,1,1),(-1,1,1)))
TIBIA_OFFSET = -20

POFFSETS = (0,0,-20)


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
cLen = 37.5
fLen = 70
tLen = 166

# Create all Joints
'''
rfCoxa = Joint(pwm, 8,cLen, direction=1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B, offset=-5)
rfFemur = Joint(pwm, 9,fLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A, offset = -10)
rfTibia = Joint(pwm, 10,tLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A, offset = 0)

lfCoxa = Joint(pwm, 12,cLen, direction=-1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B, offset = 0)
lfFemur = Joint(pwm, 13,fLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A, offset = 10)
lfTibia = Joint(pwm, 14,tLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A, offset = 0)

lhCoxa = Joint(pwm, 0,cLen, direction=-1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B, offset = 0)
lhFemur = Joint(pwm, 1,fLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A, offset = -10)
lhTibia = Joint(pwm, 2,tLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A, offset = -4)

rhCoxa = Joint(pwm, 4,cLen, direction=1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B, offset = 5)
rhFemur = Joint(pwm, 5,fLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A, offset = 10)
rhTibia = Joint(pwm, 6,tLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A, offset = -10)
'''

rfCoxa = Joint(pwm, 8,cLen, direction=1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
rfFemur = Joint(pwm, 9,fLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
rfTibia = Joint(pwm, 10,tLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)

lfCoxa = Joint(pwm, 12,cLen, direction=-1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
lfFemur = Joint(pwm, 13,fLen, direction=
1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
lfTibia = Joint(pwm, 14,tLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)

lhCoxa = Joint(pwm, 0,cLen, direction=-1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
lhFemur = Joint(pwm, 1,fLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
lhTibia = Joint(pwm, 2,tLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)

rhCoxa = Joint(pwm, 4,cLen, direction=1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
rhFemur = Joint(pwm, 5,fLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
rhTibia = Joint(pwm, 6,tLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)


# Assign joints to legs
rfLeg = Leg(rfCoxa, rfFemur, rfTibia)
lfLeg = Leg(lfCoxa, lfFemur, lfTibia)
lhLeg = Leg(lhCoxa, lhFemur, lhTibia)
rhLeg = Leg(rhCoxa, rhFemur, rhTibia)


# Put legs into an array
body = Body(rfLeg,lfLeg,lhLeg,rhLeg)



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
    

def execute_turn(command):
    for i in range(0,command.get_or("steps",1)):
        body.turn(
            lift = command.get_or("lift",30), 
            stride = command.get_or("stride",80), 
            speed = command.get_or("speed", DEFAULT_SPEED),
        )
        
def execute_walk(command):
    
    for i in range(0,command.get_or("steps",1)):
        body.walk(
            lift = command.get_or("lift",30), 
            stride = command.get_or("stride",80), 
            speed = command.get_or("speed", DEFAULT_SPEED),
            heading = Heading[command.get_or("heading",0)],
        )
    
    

''' Accepts Json payload and executes command! ''' 
def dispatch(payload):
    
    command = Command(payload)
    
    cmd = command.cmd
    
    if cmd == "stop":
        body.send_to_home_position(50)
    elif cmd == "walk":
        execute_walk(command)
    elif cmd == "turn":
        execute_turn(command)
    else:
        print >>sys.stderr, 'I don''t know what to do with {}'.format(command.cmd)
        

'''    
def start_server():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', 8001)
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
            data = connection.recv(1024).decode('utf-8')
            if data:
                sdata = str(data)
                jdata = json.loads(sdata)
            
                connection.sendall("ok")
                print >>sys.stderr, 'received "%s"' % data
                dispatch(jdata)
                data = None
        finally:
            # Clean up the connection
            connection.close()    
            sock.shutdown
            sock.close()
 
'''

def start_server():
    server = Server("localhost",8002)
    
    while True:
        print("hello")
        server.accept()
        data = server.recv()
        server.send({'status': 'ok'})
        dispatch(data)
        print data
            
    
    
def main():
    
    #print POFFSETS
    body.set_offsets(POFFSETS)
    body.go_home()
    delay(1000)
    
    '''
    dispatch('{"cmd":"walk", "lift":30, "stride":80, "heading":0, "speed":20, "steps":1}')
    dispatch('{"cmd":"turn", "lift":30, "stride":80, "speed":20, "steps":1}')
    '''
    
    start_server()
   

if __name__ == "__main__": main()

