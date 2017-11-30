#!/usr/bin/python


from utils import *
from leg import Leg
from joint import Joint
from time import sleep
import numpy as np
import imp
import math
import Adafruit_PCA9685
try:
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


COXA_MASK = np.array(((1,1,1),(-1,1,1),(1,1,1),(-1,1,1)))

P0 = np.zeros((4,3))
POFFSETS = np.array(((0,0,-5),(0,0,5),(0,0,5),(0,0,-5)))



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
legs = [rfLeg,lfLeg,lhLeg,rhLeg]



############################ Methods ######################

# Are targets reached?
def targets_reached():
    for leg in legs:
        if not leg.targets_reached():
            return False
    
    return True

# Seek targets - move until targets reached
def seek_targets():
    while(not targets_reached()):
        for leg in legs:
            leg.seek_targets()
        delay(15)
  
 
def go_home():
    for leg in legs:
        leg.goto_targets()
    
def set_xyz(x,y,z, speed = DEFAULT_SPEED, go = False):
    for leg in legs:
        leg.solve_for_xyz_offset(x,y,z, speed)
    if go:
        seek_targets()
        
def set_position(pos, speed =DEFAULT_SPEED, go = False):
    print "setting position:\n{}".format(pos)
    for index, elem in enumerate(pos):
        x,y,z = elem.tolist()
        legs[index].solve_for_xyz_offset(x,y,z, speed)
    if go:
        seek_targets()

def up_down_demo():
    pos = np.zeros((4,3))
    delay(200)
    set_position(pos + (0,0,-20), go=True)
    delay(200)
    set_position(pos + (0,0,20), go=True)
    delay(200)
    set_position(pos, go=True)
    delay(200)
    
def twist_demo(distance):
    pos = np.zeros((4,3))
    
    mask = np.array(((1,1,1),(-1,1,1),(-1,1,1),(1,1,1)))
    
    dir = [-1,1]
    for i in dir:
        set_position((pos + (distance*i,0,0))*mask, go=True, speed=10)
        delay(500)
    
    set_position(pos, go=True)

def walk_demo(steps = 2, lift=30, turn = 50, speed = 40):
    for i in range(0,steps):
        gait1(lift = lift, turn = turn, speed = speed)
        delay(50)
    
    
    
def mirror(ar):
    return np.array((ar[1],ar[0],ar[3],ar[2]))


def trot(lift=30, turn=30, speed=20):
    
    pos = P0 #+POFFSETS

    in_air = 5.0
    num_steps = 20
    
    on_ground = num_steps - in_air
    steps = [1,11,6,16]
    z = 2
    x = 0

    for step in range(1,num_steps+1):
        if(step < 6):
            active_leg = 0
        elif(step < 11):
            active_leg = 2
        elif(step < 16):
            active_leg = 1
        else:
            active_leg = 3
            
        for index, leg in enumerate(legs):
            
            if step == steps[index]:        #1
                pos[index][z] = lift    
            elif step == steps[index]+1:    #2
                pos[index][x] = 0
                pos[index][z] = -lift
            elif step == steps[index]+2:     #3
                pos[index][x] = turn/2
                pos[index][z] = -lift/2
            elif step == steps[index]+3:     #4
                pos[index][z] = 0
            else:
                pos[index][x] -= turn/on_ground
                if abs(index - active_leg) == 2:
                    print step
                    if (step -1) % in_air == 0:
                        pos[index][z] = -lift
                    else:
                        pos[index][z] += lift/5.0
                        
        set_position(pos, speed = speed, go = True)
                        


def gait1(lift=30, turn=50, speed=40):
    
    pos = P0+POFFSETS

    in_air = 5.0
    num_steps = 20
    
    on_ground = num_steps - in_air
    steps = [16,6,1,11]
    z = 2
    x = 0

    for step in range(1,num_steps+1):
        if(step < 6):
            active_leg = 2
        elif(step < 11):
            active_leg = 1
        elif(step < 16):
            active_leg = 3
        else:
            active_leg = 0
            
        for index, leg in enumerate(legs):
            
            if step == steps[index]:        #1
                pos[index][z] = lift    
            elif step == steps[index]+1:    #2
                pos[index][x] = 0
                pos[index][z] = -lift
            elif step == steps[index]+2:     #3
                pos[index][x] = turn/2
                pos[index][z] = -lift/2
            elif step == steps[index]+3:     #4
                pos[index][z] = 0
            else:
                pos[index][x] -= turn/on_ground
                if abs(index - active_leg) == 2:
                    if (step -1) % in_air == 0:
                        pos[index][z] = -lift
                    else:
                        pos[index][z] += lift/5.0
                        
        set_position(pos, speed = speed, go = True)
                        


def main():
    
    go_home()
    delay(1000)
    #set_position(pos, speed = 100, go = True)
    #twist_demo(60)
    #up_down_demo()
    #walk_demo(steps=4, lift=30, turn=50)
    #trot(steps=40, speed=20, lift=40, stride=50)
    
    for i in range(0,5):
        trot(speed = 20)
    
    #gait1()
  

if __name__ == "__main__": main()

