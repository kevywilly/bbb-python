#!/usr/bin/python

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


COXA_MASK = np.array(((1,1,1),(-1,1,1),(1,1,1),(-1,1,1)))

P0 = np.zeros((4,3))
POFFSETS = np.array(((0,0,0),(0,0,0),(0,0,0),(0,0,0)))

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
    body.set_position(pos + (0,0,-20), go=True)
    delay(200)
    body.set_position(pos + (0,0,20), go=True)
    delay(200)
    body.set_position(pos, go=True)
    delay(200)
    
def twist_demo(distance):
    pos = np.zeros((4,3))
    
    mask = np.array(((1,1,1),(-1,1,1),(-1,1,1),(1,1,1)))
    
    
    for i in dir:
        body.set_position((pos + (distance*i,0,0))*mask, go=True, speed=10)
        delay(500)
    
    body.set_position(pos, go=True)

def walk_demo(steps = 2, lift=30, turn = 50, speed = 40):
    for _ in range(0,steps):
        gait1(lift = lift, turn = turn, speed = speed)
        delay(50)
    
    
    
def mirror(ar):
    return np.array((ar[1],ar[0],ar[3],ar[2]))

def gait(gait_period = 20, duty_factor = 0.25, lift=30, stride=50, speed=40, gait = Gaits.WALK, heading = Headings.NORTH, testing=False):

    X = 0
    Z = 2

    pos = P0+POFFSETS
    mask = HeadingsMap[heading]["mask"]
    order = HeadingsMap[heading][gait]

    stepping = int(duty_factor*gait_period)
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
            active_leg = order[int(counter/stepping)]
            print(active_leg)
            
        # Calculate position

        for leg in range(0,4):
            step = current_step[leg]
            if step <= stepping/2:
                pos[leg][Z] -= 2*lift/stepping
                pos[leg][X] += stride/2/stepping
            elif step < stepping:
                pos[leg][Z] += 2*lift/stepping
                pos[leg][X] += 0.5*stride/stepping
            elif step == stepping:
                pos[leg][Z] = 0
            else:
                pos[leg][X] -= stride/on_ground
                '''
                if leg == opposite(active_leg):
                    if step % stepping == 0:
                        pos[leg][Z] = -lift
                    else:
                        pos[leg][Z] += lift/in_air
                else:
                    pos[leg][Z] = 0
                '''


        ## increment the current step
        for i in range(0,4):
            current_step[i] += 1
            if current_step[i] >= gait_period:
                current_step[i] = 0

   
        
        if not testing :
            body.set_position(pos*mask, speed = speed, go = True)
        else:
            print(pos[2])
            
            
def gait1(gait_period = 20, gait_cycle = 6, lift=30, stride=50, speed=40, gait = Gaits.WALK, heading = Headings.NORTH, testing=False):

    X = 0
    Z = 2

    pos = P0+POFFSETS
    mask = HeadingsMap[heading]["mask"]
    order = HeadingsMap[heading][gait]

    stepping = gait_cycle
    in_air = stepping - 2
    on_ground = gait_period - stepping
    
    first_steps = [0,3*stepping,2*stepping,stepping]

    current_step = first_steps[:]
    print current_step

    active_leg = None
    for counter in range(0,gait_period):

        # get the active leg
        if active_leg != order[int(counter/stepping)]:
            active_leg = order[int(counter/stepping)]
            print "Active Leg: {}".format(active_leg)
            
        # Calculate position

        for idx, leg in enumerate(order):
            step = current_step[idx]
            if step == 0:
                # shift
                pos[leg][Z] = lift
            elif step <= in_air/2:
                pos[leg][Z] = -step*2*lift/in_air
                pos[leg][X] = step*(stride/2)/in_air
            elif step < stepping:
                pos[leg][Z] = (step-1)*2*lift/in_air - 2*lift
                pos[leg][X] = step*(stride/2)/in_air
            else:
                pos[leg][X] -= stride/on_ground
                if leg == opposite(active_leg):
                    if step % stepping == 0:
                        pos[leg][Z] = -lift
                    else:
                        pos[leg][Z] += lift/(stepping-1)
                else:
                    pos[leg][Z] = 0



        ## increment the current step
        for i in range(0,4):
            current_step[i] += 1
            if current_step[i] >= gait_period:
                current_step[i] = 0

   
        
        if not testing :
            body.set_position(pos*mask, speed = speed, go = True)
        else:
            ##a1,a2,a3,b1,b2,b3,c1,c2,c3,d1,d2,d3 = 
            print ',\t'.join(map(str, pos.flatten().tolist()))
            
    
def gait2(lift=30, stride=50, speed=40, gait = Gaits.WALK, heading = Headings.NORTH, testing = False):
    
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
                        
        if not testing :
            body.set_position(pos*mask, speed = speed, go = True)
        else:
            ##a1,a2,a3,b1,b2,b3,c1,c2,c3,d1,d2,d3 = 
            print ',\t'.join(map(str, pos.flatten().tolist()))
            
def crawl(lift=35, stride=100, speed=40, gait = Gaits.WALK, heading = Headings.NORTH, testing = False):
    
    pos = P0
    
    X=0
    Y=1
    Z=2
    
    mask = HeadingsMap[heading]["mask"]
    order = HeadingsMap[heading][gait]
    
    support_cycles = 10.0

    side1 = order[:2]
    side2 = order[2:]
    
    for stepping_leg in order:
        if stepping_leg in side1:
            stepping_side = side1
        else:
            stepping_side = side2
            
        for step in range(0,4):
            for leg in order:
                if step == 0: 
                   
                    if leg == stepping_leg:
                        pos[leg][Z] = lift/2
                    elif leg == opposite(stepping_leg):
                        pos[leg][Z] = -lift/2
                    else:
                        pos[leg][X] -= stride/support_cycles

                elif step == 1: 
                   
                    if leg == stepping_leg:
                        pos[leg][Z] = lift
                    elif leg == opposite(stepping_leg):
                        pos[leg][Z] = -lift
                    else:
                        pos[leg][X] -= stride/support_cycles  
                        
                elif step == 2: 
                   
                    if leg == stepping_leg:
                        pos[leg][Z] = -lift/2
                        pos[leg][X] = stride/2
                    elif leg == opposite(stepping_leg):
                        pos[leg][Z] = -lift/2
                    
                    if leg != stepping_leg:
                        pos[leg][X] -= stride/support_cycles  
                        
                
                elif step == 3: 
                   
                    if leg == stepping_leg:
                        pos[leg][Z] = 0
                    elif leg == opposite(stepping_leg):
                        pos[leg][Z] = 0

                    if leg != stepping_leg:
                        pos[leg][X] -= stride/support_cycles   
    
                        
            if not testing :
                body.set_position(pos*mask, speed = speed, go = True)
            else:
                ##a1,a2,a3,b1,b2,b3,c1,c2,c3,d1,d2,d3 = 
                print ',\t'.join(map(str, pos.flatten().tolist()))
        
        

def main():
    
    body.go_home()
    delay(1000)
    #set_position(pos, speed = 100, go = True)
    #twist_demo(60)
    #up_down_demo()
    #walk_demo(steps=4, lift=30, turn=50)
    #trot(steps=40, speed=20, lift=40, stride=50)

    for _ in range(0,2):
        #gait1(gait_period = 24, gait_cycle = 6, speed=20, stride=50, lift=35, gait = Gaits.WALK, heading = Headings.NORTH, testing=False)
    #print "-----------------------------------"
        crawl()
        #gait2(speed=20, stride=80, lift=40, gait = Gaits.WALK, heading = Headings.SOUTH, testing = False)
    #gait2(speed=20, stride=100, gait = Gaits.WALK, heading = Headings.EAST)
    #gait2(speed=20, stride=100, gait = Gaits.WALK, heading = Headings.SOUTH)
    #gait2(speed=20, stride=100, gait = Gaits.WALK, heading = Headings.WEST)
  

if __name__ == "__main__": main()

