from math import *

class IK:
    
    def __init__(self, lCoxa, lFemur, lTibia):
        self.lCoxa = float(lCoxa)
        self.lFemur = float(lFemur)
        self.lTibia = float(lTibia)
        
        self.aCoxa = 0
        self.aTibia = 90
        self.aFemur = 90
        
        self.aCoxa0 = self.aCoxa
        self.aFemur0 = self.aFemur
        self.aTibia0 = self.aTibia
        
        self.a = int(round(self.aCoxa))
        self.b = int(round(self.aFemur-90))
        self.c = int(round(self.aTibia-90))
        
        self.solve_for_angles(self.aCoxa, self.aTibia, self.aFemur)
        
        self.xBase = self.x
        self.yBase = self.y
        self.zBase = self.z
        
    def __str__(self):
        return "IK: ({},{},{}) : ({},{},{}) \n ({},{},{}) ".format(self.x, self.y, self.z, self.aCoxa, self.aFemur, self.aTibia, self.a, self.b, self.c)
        
    def solve_for_angles(self, angleCoxa, angleFemur, angleTibia):
        
        self.aCoxa = angleCoxa;
        self.aFemur = angleFemur;
        self.aTibia = angleTibia
        
        zFemur = sin(radians(self.aFemur-90))*self.lFemur
        yFemur = cos(radians(self.aFemur-90))*self.lFemur
        hypToFemurTip = self.lCoxa + yFemur
        
        a1 = self.aFemur
        a2 = self.aTibia - a1
        
        zTibia = cos(radians(a2))*self.lTibia
        yTibia = sin(radians(a2))*self.lTibia
        hypToTibiaTip = hypToFemurTip + yTibia
        
        self.y = cos(radians(self.aCoxa))*hypToTibiaTip
        self.x = sin(radians(self.aCoxa))*hypToTibiaTip
        self.z = zTibia - zFemur
		
    def solve_for_xyz_offset(self, xOff, yOff, zOff):
		self.solve_for_xyz(self.xBase+xOff, self.yBase+yOff, self.zBase+zOff)
	
    def solve_for_xyz(self, xVal, yVal, zVal):

        L1 = sqrt(pow(xVal,2) + pow(yVal,2))
        
        ZOffset = zVal
        
        gamma = atan(xVal/yVal)
        
        L = sqrt((pow(ZOffset,2)+pow((L1-self.lCoxa),2)))
        
        alpha = acos(ZOffset/L) + acos((pow(self.lTibia,2) - pow(self.lFemur,2) - pow(L,2))/((-2)*self.lFemur*L))
        
        beta = acos((pow(L,2) - pow(self.lTibia,2) - pow(self.lFemur,2))/((-2)*self.lTibia*self.lFemur))
        
        self.aCoxa = degrees(gamma)
        self.aFemur = degrees(alpha)
        self. aTibia = degrees(beta)
        
        self.x = xVal
        self.y = yVal
        self.z = zVal
        
        ''' recalc x,y,z based on angles calculated '''
        self.solve_for_angles(self.aCoxa, self.aFemur, self.aTibia);
        
        self.a = int(round(self.aCoxa))
        self.b = int(round(self.aFemur-90))
        self.c = int(round(self.aTibia-90))