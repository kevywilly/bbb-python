
from leg import Leg
from utils import *
import numpy as np

class Body:

	def __init__(self,l1, l2, l3, l4, speed = 20):
		self.leg1 = l1
		self.leg2 = l2
		self.leg3 = l3
		self.leg4 = l4
		self.legs = (self.leg1,self.leg2,self.leg3,self.leg4)
		self.default_speed = speed
		self.P0 = np.zeros((4,3))
		self.coxa_mask = ((1,1,1),(-1,1,1),(-1,1,1),(1,1,1))
		
		
	''' Accepts np array (4,3)'''
	def set_offsets(self, offsets):
		self.P0 = np.zeros((4,3)) + offsets
		
	'''
		Sets position relative to P0
		pos = new position
		speed = speed at which to articulate joints
		go = seek targets True / False
		mask = apply multiplicative mask to final position
	'''
	def set_relative_position(self, pos, speed = None, go = False, mask = (1,1,1)):
		self.set_position((pos+self.P0)*mask, speed, go)
		
	def set_position(self, pos, speed = None, go = False):
		print "setting position:\n{}".format(pos)
		if speed == None:
			speed = self.default_speed

		for index, elem in enumerate(pos):
			x,y,z = elem.tolist()
			self.legs[index].solve_for_xyz_offset(x,y,z, ifNone(speed,self.default_speed))
		if go:
			self.seek_targets()

		pass

	def go_home(self):
		self.set_position(self.P0)
		for leg in self.legs:
			leg.goto_targets()
		pass
	
	def send_to_home_position(self, speed = None):
		self.set_position(self.P0, speed, True)
		
	def set_z(self, mm, speed = None, go = False):
		self.set_relative_position(self.P0 + (0,0,mm), speed, go)
		
	def set_x(self, mm, speed = None, go = False):
		mask = mask = ((1,0,0),(-1,0,0),(-1,0,0),(1,0,0))
		self.set_relative_position((self.P0 + (mm,0,0))*mask, speed, go)
		

# Are targets reached?
	def targets_reached(self):
		for leg in self.legs:
			if not leg.targets_reached():
				return False

		return True

# Seek targets - move until targets reached
	def seek_targets(self):
		while(not self.targets_reached()):
			for leg in self.legs:
				leg.seek_targets()
			delay(10)



		return True
		
			
	def up_down(self, cm = 5, speed = 10, testing = False):
		pos = np.zeros((4,3)) + (0,0,cm)
		if not testing:
			self.set_relative_position(pos, speed = speed, go = True)
		else:
			print ',\t'.join(map(str, pos.flatten().tolist()))
			
	def twist(self, cm = 20, speed = 10, testing = False):
		pos = np.zeros((4,3)) + (cm,0,0)
		if not testing:
			self.set_relative_position(pos, speed = speed, go = True, mask = self.coxa_mask)
		else:
			print ',\t'.join(map(str, pos.flatten().tolist()))
		
		
	def turn(self, lift = 20, stride = 50, speed = 20, testing = False):
		
		X=0
		Y=1
		Z=2
		
		pos = np.zeros((4,3))
		
		dirr = [1,-1,-1,1]
		
		order = [0,1,2,3]
		
		
		for stepping_leg in order:
			
			for step in range(0,3):
				
				print "stepping leg {} step {}".format(stepping_leg, step)
				
				for leg in order:
					
					if step == 0:
						# lean away from stepping leg
						if leg == stepping_leg:
							pos[leg][Z] = lift
						elif leg == (stepping_leg ^ 2):
							pos[leg][Z] = -lift
						
					elif step == 1:
						# lift stepping leg
						if leg == stepping_leg:
							pos[leg][Z] = -lift
							pos[leg][X] = stride/2
						else:
							pos[leg][X] -= stride/8
						
					elif step == 2:
						if leg == stepping_leg:
							pos[leg][X] = stride
						else:
							pos[leg][X] -= stride/8
						
						pos[leg][Z] = 0
						
				
				if not testing:
					self.set_relative_position(pos, speed = speed, go = True, mask = self.coxa_mask)
				else:
					print ',\t'.join(map(str, pos.flatten().tolist()))
						
				
				
			
			
		self.send_to_home_position(speed)
		
		
	def walk(self, heading, lift=25, stride=80, speed=40, testing = False):
	    
	    pos = np.zeros((4,3)) #np.copy(self.P0)
	    
	    mask = heading["mask"]
	    order = heading["order"]
	
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
	        
	        for index, leg in enumerate(self.legs):
	            
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
	            self.set_relative_position(pos*mask, speed = speed, go = True)
	        else:
	            ##a1,a2,a3,b1,b2,b3,c1,c2,c3,d1,d2,d3 = 
	            print ',\t'.join(map(str, pos.flatten().tolist()))
	            
	    #self.send_to_home_position(speed)
	            