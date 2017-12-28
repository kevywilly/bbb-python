from math import *
from utils import *
import time

class Target:
    def __init__(self, angle, speed, step):
        self.angle = angle
        self.speed = speed
        self.step = step
        pass
    
    def __str__(self):
        return "Target:{}@{}".format(self.angle, self.speed)
    
class Joint:
    def __init__(self, pwm, id, length, minPulse, maxPulse, minAngle = -90, maxAngle = 90, direction = 1, offset = 0):
        self.id = id
        self.length = length
        self.maxAngle = maxAngle
        self.minAngle = minAngle
        self.target = Target(angle=0,speed=1,step=1)
        self.current = 0
        self.defaultSpeed = 1
        self.offset = offset
        self.minPulse = minPulse
        self.maxPulse = maxPulse
        self.direction = direction
        self.pwm = pwm
        self.home_angle = self.current
        self.rest_pulse = (self.minPulse + self.maxPulse)/2
        
        
    def __str__(self):
        return "<Joint id:{}, Angle:{}, {}>".format(self.id,self.current,self.target)
	
    # set angle offset
    def set_offset(self, offs):
        self.offset = offs
        
    # set target angle
    def set_target(self, angle, speed = 1):
       
        # get safe speed
        speed = max(min(speed, 100), 0);
        
        #get safe target angle
        target_angle = self.safe_angle(angle+self.home_angle);
        
        # what is the difference
        diff = (target_angle - self.current);
        
        # store the sign
        sign = 1.0
        if diff < 0:
            sign = -1.0
        
        # map 0-1 to 0 - abs(diff)
        desired_step = scale(speed, 0, 100, 0, abs(diff))*sign;
        
        if (desired_step == 0) and (target_angle <> self.current):
        	step = 1*sign;
        else:
        	step = desired_step;
        	
        self.target = Target(target_angle, speed, step)


   
    # return angle between min and max
    def safe_angle(self, angle):
        if angle < self.minAngle:
            return self.minAngle
        if angle > self.maxAngle:
            return self.maxAngle
        return angle
        
    # convert an angle to pulse for pwm
    def angle_to_pulse(self, angle):
        return scale(self.safe_angle(angle*self.direction + self.offset), self.minAngle, self.maxAngle, self.minPulse, self.maxPulse)
      
	    
    # go directly to angle  
    def goto_angle(self,angle):
    	a = self.safe_angle(angle)
    	pulse = int(round(self.angle_to_pulse(a)))
    	#print "moving joint {} to angle {} using pulse {}".format(self.id, a, pulse)
        if self.pwm != None:
    	   self.pwm.set_pwm(self.id, 0, pulse)
    	self.current = a
	
	    
	# rest
    def rest(self):
        
        if self.pwm != None:
            self.pwm.set_pwm(self.id, self.rest_pulse, self.rest_pulse)
	    
	def wakeup(self):
	    self.goto_target()
	    
    # go directly to target angle
    def goto_target(self):
        self.goto_angle(self.target.angle)
        

    # is target reached
    def target_reached(self):
        return self.target.angle == self.current
	    
    def seek_target(self, with_delay = False):
    
        # Do nothing if target is already reached
        if self.target_reached():
        	self.target.step = 0
        	return
        
        
        # Calc new angle and make sure it is safe
        new_angle = self.safe_angle(self.current + self.target.step)
        
        # Are we stepping too far? If so, go to the angle
        if (((self.target.step > 0) and (new_angle > self.target.angle)) or ((self.target.step < 0) and (new_angle < self.target.angle))):
        	new_angle = self.target.angle
        	self.target.step = 0
        
        # go to the angle
        self.goto_angle(new_angle)
        
        if with_delay:
            time.sleep(0.012)
    
