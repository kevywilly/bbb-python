#!/usr/bin/python

from utils import *
from leg import Leg
from joint import Joint
from time import sleep
import numpy as np

import Adafruit_PCA9685

MIN_PULSE_A = 110
MAX_PULSE_A = 660

MIN_PULSE_B = 150
MAX_PULSE_B = 650

DEFAULT_SPEED = 10

COXA_MASK = np.array(((1,1,1),(-1,1,1),(1,1,1),(-1,1,1)))

HOME = np.zeros((4,3))

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)

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

lhCoxa = Joint(pwm, 2,cLen, direction=1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
lhFemur = Joint(pwm, 6,fLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
lhTibia = Joint(pwm, 10,tLen, direction=1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)

rhCoxa = Joint(pwm, 3,cLen, direction=-1, minPulse=MIN_PULSE_B, maxPulse=MAX_PULSE_B)
rhFemur = Joint(pwm, 7,fLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)
rhTibia = Joint(pwm, 11,tLen, direction=-1, minPulse=MIN_PULSE_A, maxPulse=MAX_PULSE_A)

# Assign joints to legs
rfLeg = Leg(rfCoxa, rfFemur, rfTibia)
lfLeg = Leg(lfCoxa, lfFemur, lfTibia)
lhLeg = Leg(lhCoxa, lhFemur, lhTibia)
rhLeg = Leg(rhCoxa, rhFemur, rhTibia)


# Put legs into an array
legs = [rfLeg,lfLeg,lhLeg,rhLeg]

GAITLEGSTEP = [6,16,11,1]
NUMLIFTE_POS = 5  # number of steps that the leg is in the air
TLDIVFACTOR = 15 # number of steps that the leg is on the ground


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
    
    delay(5)
  
 
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
    
def twist_demo():
    pos = np.zeros((4,3))
    
    mask = np.array(((1,1,1),(-1,1,1),(1,1,1),(-1,1,1)))
    
    offsets = (80,-80, 0)
   
    for x in offsets:
        set_position((pos + (x,0,0)) * COXA_MASK, go=True)
        delay(500)

def walk_demo():
    
    home = np.zeros((4,3))
     
    #                       RF          LF        LR         RR
    step1 = home  +  ((-20, 0, 0), (0, 0,-20),   (20, 0, 0),    ( 0, 0, 20)) # rr step
    step2 = home  +  ((-25, 0, 0), (0, 0,-30),   (25, 0, 0),    (-40,0,-20)) # rr step
    step3 = home  +  ((-30, 0, 0), (0, 0, 0),    (30, 0, 0),     (-40,0,0)) # rr down
    step4 = home  +  ((20,0,-20), (0, 0, 0),    (20, 0, -20), (-20,0,0)) # RF Step
    step5 = home  +  ((20,0,0), (0, 0, 0),    (-20, 0, 0), (0,0,0)) # RF Step
    step6 = home  +  ((0, 0, 0),(0, 0, 0),    (0, 0, 0), (0,0,0)) # RF Down
    
    
    
    steps = [step1,step2,step3,step4,step5]
    
    

    for step in steps:
        set_position(step, go=True)
    
    for step in steps:
        set_position(mirror(step), go = True)
    
    
def mirror(ar):
    return np.array((ar[1],ar[0],ar[3],ar[2]))



def walk2():
    
    mask = np.array(((1,1,1),(1,1,1),(-1,1,1),(-1,1,1)))
    pos = np.zeros((4,3))
    pos[2][2]=5
    pos[1][2]=5
    pos[0][2]=-5
    pos[3][2]=-5
    in_air = 5.0
    num_steps = 20
    
    on_ground = num_steps - in_air
    steps = [16,6,1,11]
    lift = 25
    turn = 100
    z = 2
    x = 0

    for step in range(1,num_steps):
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
                pos[index][z] = -lift/3
            elif step == steps[index]+3:     #4
                pos[index][z] = 0
            else:
                pos[index][x] -= turn/on_ground
                if abs(index - active_leg) == 2:
                    if (step -1) % in_air == 0:
                        pos[index][z] = -lift
                    else:
                        pos[index][z] += lift/5.0
                        
        set_position(pos*mask, go = True)
        delay(10)
                        

    
def main():
    
   
    go_home()
    
    walk2()
    walk2()
    
    #step1 = home  +  ((0, 0, 0), (0, 0, 0), (0, 0, 0), (0,0,15))
    #set_position(step1, go=True)
    
    #pos = np.zeros((4,3))
    
    #for i in range(1,20):
    
    #    gait_calculate(i)
   
  

if __name__ == "__main__": main()



'''
def gait_calculate(step):
    leg_lift_height = 60
    walk_length = 100

    pos = np.zeros((4,3))
    Z = 2
    X = 0
    mask = np.array(((1,1,1),(1,1,1),(-1,1,1),(-1,1,1)))
    for index, leg in enumerate(legs):
        if step == GAITLEGSTEP[index]:
            pos[index][Z] = -leg_lift_height/2
        elif step == GAITLEGSTEP[index]+1:
            pos[index][X] = 0
            pos[index][Z] = -leg_lift_height
        elif step == GAITLEGSTEP[index]+2:
            pos[index][X] = walk_length/2
            pos[index][Z] = -leg_lift_height/2
        elif step == GAITLEGSTEP[index]+3:
            pos[index][Z] = 0
        else:
            pos[index][X] = -walk_length/TLDIVFACTOR
       
    adj_pos = pos*mask     
    print "###### step {} ######".format(step)
    print adj_pos
    print "#####################"
        
   
    set_position(adj_pos, go=True)
    delay(10)
'''