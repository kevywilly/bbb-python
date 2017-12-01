
from leg import Leg
from utils import *

class Body:

	def __init__(self,l1, l2, l3, l4, default_speed = 20):
		self.leg1 = l1
		self.leg2 = l2
		self.leg3 = l3
		self.leg4 = l4
		self.legs = (self.leg1,self.leg2,self.leg3,self.leg4)
		
	def set_position(self, pos, speed = None, go = False):
		print "setting position:\n{}".format(pos)
		if speed == none:
			speed = default_speed

		for index, elem in enumerate(pos):
			x,y,z = elem.tolist()
			self.legs[index].solve_for_xyz_offset(x,y,z, ifNone(speed,self.default_speed))
		if go:
			seek_targets()

		pass

	def go_home(self):
		for leg in self.legs:
			leg.goto_targets()
		pass

# Are targets reached?
	def targets_reached(self):
		for leg in self.legs:
			if not leg.targets_reached():
				return False

		return True

# Seek targets - move until targets reached
	def seek_targets(self):
		while(not targets_reached()):
			for leg in self.legs:
				leg.seek_targets()
				delay(15)



		return True