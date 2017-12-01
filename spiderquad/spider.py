#!/usr/bin/python


from utils import *
from body import Body
from leg import Leg
from joint import Joint
from time import sleep
import numpy as np
import imp
import math

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


COXA_MASK = np.array(((1,1,1),(-1,1,1),(1,1,1),(-1,1,1)))

P0 = np.zeros((4,3))
POFFSETS = np.array(((0,0,-5),(0,0,5),(0,0,5),(0,0,-5)))

Headings = enum(NORTH=1,SOUTH=2,EAST=3,WEST=4)
Gaits = enum(WALK="walk",TROT="trot")


HeadingsMap = { 
    1 : { "walk": [2,1,3,0], "trot": [2,0,3,1], "mask": (1,1,1)},  #North
    2 : { "walk": [0,3,1,2], "trot": [0,2,1,3], "mask":  (-1,1,1)}, #South
    3 : { "walk": [1,0,2,3], "trot": [1,3,2,0], "mask": ((-1,1,1),(1,1,1),(-1,1,1),(1,1,1))}, #East
    4 : { "walk": [3,2,0,1], "trot": [3,1,0,2], "mask": ((1,1,1),(-1,1,1),(1,1,1),(-1,1,1))}, #West
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




############################ Methods ######################

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

def gait1(gait_period = 20, duty_factor = 0.25, lift=30, stride=50, speed=40, gait = Gaits.WALK, heading = Headings.NORTH):

    X = 0
    Z = 2

    pos = P0+POFFSETS
    mask = HeadingsMap[heading]["mask"]
    order = HeadingsMap[heading][gait]

    stepping = int(duty_factor*gait_period)
    in_air = stepping - 1
    on_ground = gait_period - stepping
    
    first_steps = [0,0,0,0]
    
    for i in range(0,4):
        first_steps[order[i]] = i*stepping

    current_step = first_steps[:]
    print current_step

    active_leg = None
    for counter in range(0,gait_period):

        # get the active leg
        if active_leg != order[int(counter/stepping)]:
            active_leg = order[int(counter/in_air)]
            
            #print "active_leg: {}\n".format(active_leg)

        

        # Calculate position

        for leg in range(0,4):
            step = current_step[leg]
            if step == 0:
                # shift
                pos[leg][Z] = lift
            elif step == 1:
                pos[leg][Z] = -lift/(in_air/2)
                pos[leg][X] = (stride/2)/(in_air)
            elif step <= stepping/2:
                pos[leg][Z] -= lift/(in_air/2)
                pos[leg][X] += (stride/2)/(in_air)
            elif step < stepping:
                pos[leg][Z] += lift/(in_air/2)
                pos[leg][X] += (stride/2)/(in_air)
            elif step == stepping:
                pos[leg][Z] = 0
            else:
                pos[leg][X] -= stride/on_ground
                if leg == opposite(active_leg):
                    if step % stepping == 0:
                        pos[leg][Z] = -lift
                    else:
                        pos[leg][Z] += lift/in_air
                else:
                    pos[leg][Z] = 0



        ## increment the current step
        for i in range(0,4):
            current_step[i] += 1
            if current_step[i] >= gait_period:
                current_step[i] = 0

   
        print(pos[2])
    

def gait2(lift=30, stride=50, speed=40, gait = Gaits.WALK, heading = Headings.NORTH):
    
    pos = P0+POFFSETS
    
    mask = HeadingsMap[heading]["mask"]
    order = HeadingsMap[heading][gait]

    num_steps = 20
    
    in_air = num_steps/4
    
    on_ground = num_steps - in_air
    
    steps = [0,0,0,0]
    for i in range(0,4):
        steps[order[i]] = 0+i*in_air
        
    print "steps: {}".format(steps)
    
    z = 2
    x = 0

    for step in range(0,num_steps):
        active_leg = order[int(step/in_air)]
        
            
        for index, leg in enumerate(body.legs):
            
            if step == steps[index]:        #1
                pos[index][z] = lift  
            elif step == steps[index]+1:    #2
                pos[index][x] = 0
                pos[index][z] = -lift
            elif step == steps[index]+2:     #3
                pos[index][x] = stride/2
                pos[index][z] = -lift/2
            elif step == steps[index]+3:     #4
                pos[index][z] = 0
            else:
                pos[index][x] -= stride/on_ground
                if abs(index - active_leg) == 2:
                    if step % in_air == 0:
                        pos[index][z] = -lift
                    else:
                        pos[index][z] += lift/in_air
                else:
                    pos[index][z] = 0
                        
        #set_position(pos*mask, speed = speed, go = True)
        print(pos[2])               


def main():
    
    body.go_home()
    delay(1000)
    #set_position(pos, speed = 100, go = True)
    #twist_demo(60)
    #up_down_demo()
    #walk_demo(steps=4, lift=30, turn=50)
    #trot(steps=40, speed=20, lift=40, stride=50)

    gait1(speed=20, stride=50, lift=30, gait = Gaits.WALK, heading = Headings.NORTH)
    print "-----------------------------------"
    gait2(speed=20, stride=50, lift=30, gait = Gaits.WALK, heading = Headings.NORTH)
    #gait2(speed=20, stride=100, gait = Gaits.WALK, heading = Headings.EAST)
    #gait2(speed=20, stride=100, gait = Gaits.WALK, heading = Headings.SOUTH)
    #gait2(speed=20, stride=100, gait = Gaits.WALK, heading = Headings.WEST)
  

if __name__ == "__main__": main()

