from time import sleep

def enum(**named_values):
	return type('Enum',(),named_values)
	
def delay(t):
    sleep(t/1000.0)
    
def scale(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def opposite(index):
	return index ^ 2
	
def adjacent(index):
	l1 = index + 1
	if l1 > 3:
		l1 = 0
	
	return l1, opposite(l1)

def ifNone(a,b):
	if a == None:
		return b

	return a
	
def get_or(dict,key,default=None):
	if key in dict:
		return dict[key]
	return default