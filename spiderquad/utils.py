from time import sleep

def enum(**named_values):
	return type('Enum',(),named_values)
	
def delay(t):
    sleep(t/1000.0)
    
def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def opposite(index, count=4):
	if index >= (count/2):
		return index-2
	else:
		return index+2