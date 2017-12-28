
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
		self.currentPos = np.zeros((4,3))
		
	def print_absolute(self):
		print (self.currentPos - self.P0)
		
	def zeros(self):
		return np.zeros((4,3))
		
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
		if speed == None:
			speed = self.default_speed

		for index, elem in enumerate(pos):
			x,y,z = elem.tolist()
			self.legs[index].solve_for_xyz_offset(x,y,z, ifNone(speed,self.default_speed))
			
		self.currentPos = np.copy(pos)
		
		if go:
			self.print_absolute()
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
		
	def rest(self):
		
		for leg in self.legs:
			leg.rest()
		
	def wakeup(self):
		for leg in self.legs:
			leg.wakeup()
			
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
		
		
	def turn(self, amplitude = 20, stride = 50, speed = 20, testing = False):
		
		X=0
		Y=1
		Z=2
		
		pos = np.zeros((4,3))
		
		dirr = [1,-1,-1,1]
		
		if stride >= 0:
			order = [0,1,2,3]
		else:
			order = [0,3,2,1]
		
		
		for stepping_leg in order:
			
			for step in range(0,3):
				
				print "stepping leg {} step {}".format(stepping_leg, step)
				
				for leg in order:
					
					if step == 0:
						# lean away from stepping leg
						if leg == stepping_leg:
							pos[leg][Z] = amplitude/2
						elif leg == (stepping_leg ^ 2):
							pos[leg][Z] = -amplitude/2
						
					elif step == 1:
						# lift stepping leg
						if leg == stepping_leg:
							pos[leg][Z] = -amplitude/2
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
		
	
	def walk2(self, heading, amplitude=25, stride=80, speed=40, testing = False):
		
		pos = np.zeros((4,3))
		mask = heading["mask"]
		order = heading["order"]
		x=0
		z=2
		in_air = 4
		
		for active_leg in order:
			pos[active_leg][z] = amplitude
			pos[active_leg ^ 2][z] = -amplitude
			self.set_relative_position(pos, speed = speed, go = True, mask = mask)
			
			for step in range(0,in_air):
				for l in order:
					if step == 0 and l == active_leg:
						if l == active_leg: 
							pos[l][x] = 0
							pos[l][z] = -amplitude/2
					elif step == 1 and l == active_leg:
						pos[l][x] = stride/4
						pos[l][z] = -amplitude
					elif step == 2 and l == active_leg:
						pos[l][x] = stride/2
						pos[l][z] = -amplitude/2
					elif step == 3 and l == active_leg:
						pos[l][x] = stride/2
						pos[l][z] = 0
						
					if l != active_leg:
						pos[l][x] -= (stride)/(in_air*3)
						
					if step == 1 and l == (active_leg ^ 2):
						pos[l][z] = -amplitude*2/3
					if step == 2 and l == (active_leg ^ 2):
						pos[l][z] = -amplitude*1/3
					if step == 3 and l == (active_leg ^ 2):
						pos[l][z] = 0
						
				self.set_relative_position(pos, speed = speed, go = True, mask = mask)	
			
		self.send_to_home_position(speed)	
			
			
		
		
	def walk(self, heading, amplitude=25, stride=80, speed=40, testing = False):
	    
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
	                pos[index][z] = amplitude/2  
	            elif step == steps[index]+1:    #2
	                pos[index][x] = 0
	                pos[index][z] = -amplitude
	            elif step == steps[index]+2:     #3
	                pos[index][x] = stride/2
	                pos[index][z] = -amplitude/2
	            elif step == steps[index]+3:     #4
	                pos[index][z] = 0
	            else:
	                pos[index][x] -= stride/on_ground
	                if abs(index - active_leg) == 2: 
	                    if step % in_air == 0:
	                        pos[index][z] = -amplitude/2
	                    else:
	                        pos[index][z] += amplitude/2/in_air
	                else:
	                    pos[index][z] = 0
	                        
	        if not testing :
	            self.set_relative_position(pos, speed = speed, go = True, mask = mask)
	        else:
	            ##a1,a2,a3,b1,b2,b3,c1,c2,c3,d1,d2,d3 = 
	            print ',\t'.join(map(str, pos.flatten().tolist()))
	            
	    self.send_to_home_position(speed)
	 
	def reach(self, idx, cm, speed = None, go = False, relative = True):
		pos = np.copy(self.currentPos)
		pos[idx][1] += cm
		self.set_position(pos,speed,go)
		
	def lift(self, idx, cm, speed = None, go = False, relative = True):
		pos = np.copy(self.currentPos)
		pos[idx][2] -= cm
		self.set_position(pos, speed, go)
		
	def lean(self, idx, cm, speed = None, go = False, relative = True):
		legA = idx
		legB = opposite(idx)
		
		pos = np.copy(self.currentPos)
		pos[legA][2] -= cm
		pos[legB][2] += cm
		
		self.set_position(pos,speed,go)
	def shift(self, idx, cm, speed = None, go = False, relative = True):
		
		legA = idx
		legB = opposite(idx)
		legC, legD = adjacent(idx)
		
		pos = np.copy(self.currentPos)
		pos[legA][1] -= cm
		pos[legB][1] += cm
		if idx < 2:
			pos[legC][0] -= cm
			pos[legD][0] -= cm
		else:
			pos[legC][0] += cm
			pos[legD][0] += cm
		
		self.set_position(pos, speed , go)
		

	def amble(self, amplitude=30, speed = None, heading=0):
		
		amp = amplitude
	
		
		if amp > 30 or amp < 5:
			amp = 30
		
		
			
		order = [0,1]
		d = 50
		
		if(heading == 1):
			order = [2,3]
		elif(heading == 2):
			order = [0,3]
		elif(heading == 3):
			order = [1,2]
			
		for leg in order:
			print ('=======================')
			a = leg
			b = a ^ 2
			
			
			# step 1
			self.shift(a, -amp, speed = speed, go=True)  #shift away from a
			delay(d)
			
			# step 2
			self.lift(a,amp*2, speed = speed) # lift a
			self.reach(a,amp*2, speed = speed, go=True)   # reach a
			delay(d)
			
			# lower stepping leg
			# pull in 
			# reach rear leg
			# unshift
			self.shift(a, amp, speed = speed)  # unshift away from a
			self.lift(a,-amp*2, speed = speed) # unlift a
			self.reach(a,-amp*2, speed = speed) # unreach a
			
			self.lift(b,-amp, speed = speed) # push off b
			self.reach(b,amp*2, speed = speed, go = True) # reach b
			
			delay(d)
			
			# lean toward first stepping leg
			self.lean(a,amp, speed = speed, go=True) # lean toward a
			delay(d)
			
			# lift second stepping leg and reach
			self.lift(b,amp*2, speed = speed, go=True) # lift b
			self.reach(b,-amp*2, speed = speed, go=True) # unreach b
			delay(d)
			
			# both legs down
			self.lift(a,-amp, speed = speed, go = True) # unlift a
			
		
		
	            