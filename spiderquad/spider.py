#!/usr/bin/python

import SocketServer
import signal
import sys
import threading

from utils import enum, delay, opposite
from body import Body
from leg import Leg
from joint import Joint
from command import Command
import numpy as np
import json

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

POFFSETS = (0,-10,-25)


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
rfCoxa = Joint(pwm, 8,cLen, direction=1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
rfFemur = Joint(pwm, 9,fLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
rfTibia = Joint(pwm, 10,tLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)

lfCoxa = Joint(pwm, 12,cLen, direction=-1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
lfFemur = Joint(pwm, 13,fLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
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


server = None
resting = False

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
    

def execute_twist(command):
    cm = command.get_or("cm",0)
    speed = command.get_or("speed",DEFAULT_SPEED)
    body.twist(cm = cm, speed = speed)

def execute_up_down(command):
    cm = command.get_or("cm",0)
    speed = command.get_or("speed",DEFAULT_SPEED)
    body.up_down(cm = cm, speed = speed)
        
    
def execute_turn(command):
    for i in range(0,command.get_or("steps",1)):
        body.turn(
            amplitude = command.get_or("amplitude",30), 
            stride = command.get_or("stride",80), 
            speed = command.get_or("speed", DEFAULT_SPEED),
        )
        
def execute_walk(command):
    
    for i in range(0,command.get_or("steps",1)):
        body.walk(
            amplitude = command.get_or("amplitude",30), 
            stride = command.get_or("stride",80), 
            speed = command.get_or("speed", DEFAULT_SPEED),
            heading = Heading[command.get_or("heading",0)],
        )

def execute_amble(command):
    
    for i in range(0,command.get_or("steps",1)):
        body.amble(
            amplitude = command.get_or("amplitude",30), 
            speed = command.get_or("speed", DEFAULT_SPEED),
            heading = command.get_or("heading",0)
        )
    
    

''' Accepts Json payload and executes command! ''' 
def dispatch(payload):
    
    command = Command(payload)
    
    cmd = command.cmd
    
    if cmd != "rest":
        body.wakeup()
    
    if cmd == "rest":
        body.rest()
    elif cmd == "stop":
        body.send_to_home_position(50)
    elif cmd == "amble":
        execute_amble(command)
    elif cmd == "walk":
        execute_walk(command)
    elif cmd == "turn":
        execute_turn(command)
    elif cmd == "up_down":
        execute_up_down(command)
    elif cmd == "twist":
        execute_twist(command)
    else:
        print >>sys.stderr, 'I don''t know what to do with {}'.format(command.cmd)
        

class EchoRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # Echo the back to the client
        data = self.request.recv(1024)
        print(data)
        dispatch(data)
        self.request.send(data)
        return

       
       
def close_server():
	global server
	try:
		server.shutdown(1)
	except:
		print "server not connected"
	finally:
		server.socket.close()

def signal_handler(signal, frame):
	print('You pressed Ctrl+C!')
	close_server()
	sys.exit(0)


def start_server(port):
    global server
    
    server = SocketServer.TCPServer(('192.168.1.78',port), EchoRequestHandler)
    signal.signal(signal.SIGINT, signal_handler)
    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True) # don't hang on exit
    t.start()
    print "started server ... waiting for connections"
    
    while 1:
        pass


def main():
    
    #print POFFSETS
    body.set_offsets(POFFSETS)
    body.go_home()
    delay(1000)
    start_server(8000)
    
    
    #dispatch('{"cmd":"amble", "amplitude":30, "speed":10, "heading": 0}')
    
    #delay(500)
   
    #dispatch('{"cmd":"walk", "amplitude":30, "speed":20, "stride":80, "heading": 0}')

    '''
    dispatch('{"cmd":"up_down", "cm":35, "speed":30}')
    delay(1000)
    dispatch('{"cmd":"up_down", "cm":0, "speed":30}')
    delay(1000)
    dispatch('{"cmd":"up_down", "cm":-35, "speed":30}')
    delay(1000)
    dispatch('{"cmd":"up_down", "cm":0, "speed":30}')
    delay(1000)
    
    dispatch('{"cmd":"twist", "cm":60, "speed":30}')
    delay(1000)
    dispatch('{"cmd":"twist", "cm":0, "speed":30}')
    delay(1000)
    dispatch('{"cmd":"twist", "cm":-60, "speed":30}')
    delay(1000)
    dispatch('{"cmd":"twist", "cm":0, "speed":30}')
    delay(1000)
    '''
    
    #dispatch('{"cmd":"turn", "lift":30, "stride":80, "speed":20, "steps":1}')
    
   

if __name__ == "__main__": main()

