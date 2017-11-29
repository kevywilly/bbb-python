#!/usr/bin/python


from utils import *
from leg import Leg
from joint import Joint
from time import sleep
import numpy as np
import imp
import math
try:
    imp.find_module('Adafruit_PCA9685')
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
POFFSETS = np.array(((0,0,0),(0,0,0),(0,0,0),(0,0,0)))



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



def gait1(lift=30, turn=50, speed=40):
    
    pos = P0+POFFSETS
    
    in_air = 5.0
    num_steps = 20
    on_ground = 15
    steps = [16,6,1,11]

    z = 2
    x = 0

    for step in range(1,num_steps+1):
        print "====== step {}======\n".format(step) 
        if(step < 6):
            active_leg = 2
        elif(step < 11):
            active_leg = 1
        elif(step < 16):
            active_leg = 3
        else:
            active_leg = 0
            
        for index, leg in enumerate(legs):
            
            if step == steps[index]:        #1 16
                pos[index][z] = -lift/2.0    
            elif step == steps[index]+1:    #2 17
                pos[index][x] = 0
                pos[index][z] = -lift
            elif step == steps[index]+2:     #3 18
                pos[index][x] = turn/2.0
                pos[index][z] = -lift/2.0
            elif step == steps[index]+3:     #4 19
                pos[index][z] = 0
            else:
                pos[index][x] -= turn/15.0
                if abs(index - active_leg) == 2:
                    if (step -1) % in_air == 0:
                        pos[index][z] = -lift
                    else:
                        pos[index][z] += lift/5.0
                        
                
               
        set_position(pos, speed = speed, go = True)
        print "\n"
                        

def trot(steps=60, lift=30, stride=50, speed = 20, order = [2,1,3,0]):
    print "Beginning Trot steps: {}, lift: {}, stride: {}, speed: {}, order: {}\n".format(steps,lift,stride,speed,order)
    print "=====================================================================================\n"
    in_air = steps/4.0
    on_ground = steps * 3.0/4

    current_step = []
    positions = np.zeros((4,3))

    for i in range(0,4):
        if i == 0:
            current_step.append(0)
        else:
            current_step.append(steps - i*in_air)
        
    print current_step

    stepping_leg = order[0]
    for i in range(0,steps): 
        #print current_step       
        for index, leg in enumerate(order):
            # calculate z, x for this leg
            step = current_step[index]
            
            if step < in_air:
                stepping_leg = leg
                opposite_leg = opposite(leg)
            elif stepping_leg == leg:
                stepping_leg = -1
                opposite_leg = -1

            # set x
            if step < in_air:
                positions[leg][0] = round(math.sin(math.radians((step)*90.0/in_air))*stride,2) # X gradually step forward
                positions[leg][2] = -round(math.sin(math.radians((step)*180.0/in_air))*lift,2) # Z gradually lift leg
            else:
                positions[leg][0] -= round(stride*1.0/on_ground,2) # X gradually push backward
                if leg == opposite_leg:
                    #if(positions[leg][2] == 0):
                    #    positions[leg][2] = -lift
                    #else:
                        #positions[leg][2] -= lift/on_ground
                    positions[leg][2] = -abs(round(math.sin(math.radians((step)*90.0/in_air))*lift,2)) # drop down and lift
                else:
                    positions[leg][2] = 0

            # increment current step for this leg
            if current_step[leg] < steps:
                current_step[leg] +=1
            else:
                current_step[leg] = 1

        #set_position(positions, speed=speed, go = True)
        print positions[1]

def main():
    
    go_home()
    
    #set_position(pos, speed = 100, go = True)
    #twist_demo(60)
    #up_down_demo()
    #walk_demo(steps=1, lift=30, turn=80)
    trot(steps=50, speed=100, lift=40, stride=80)
  

if __name__ == "__main__": main()

