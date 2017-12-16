from time import sleep

def enum(**named_values):
	return type('Enum',(),named_values)
	
def delay(t):
    sleep(t/1000.0)
    
def scale(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def opposite(index, count=4):
	if index >= (count/2):
		return index-2
	else:
		return index+2

def ifNone(a,b):
	if a == None:
		return b

	return a
	
def get_or(dict,key,default=None):
	if key in dict:
		return dict[key]
	return default