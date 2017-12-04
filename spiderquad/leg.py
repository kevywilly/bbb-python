from inverse_kinematics import IK
from joint import Joint
from utils import delay

class Leg:
    def __init__(self, coxa, femur, tibia):
        self.coxa = coxa
        self.femur = femur
        self.tibia = tibia
        self.ik = IK(self.coxa.length, self.femur.length, self.tibia.length)
        self.joints = [self.coxa, self.femur, self.tibia]
        
    def __str__(self):
        return "coxa: {}, femur: {}, tibia: {}, {}".format(self.coxa, self.femur, self.tibia, self.ik)
        
    def solve_for_xyz_offset(self, x, y, z, speed = 1):
        self.ik.solve_for_xyz_offset(x,y,z)
        self.coxa.set_target(self.ik.a, speed)
        self.femur.set_target(self.ik.b, speed)
        self.tibia.set_target(self.ik.c, speed)
        
    def seek_targets(self):
        for joint in self.joints:
            joint.seek_target(False)
        
    def goto_targets(self):
        for joint in self.joints:
            joint.goto_target()
            
    def targets_reached(self):
        for joint in self.joints:
            if not joint.target_reached():
                return False
                
        return True
        