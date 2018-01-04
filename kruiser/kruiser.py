#!/usr/bin/python3

from rcpy.motor import motor1, motor2
from time import sleep
import socketserver
import signal
import sys
import threading
import json

# Setup server
server = None

# angles
d1 = 0
d2 = 0

class Command:
    
    def __init__(self, json_string):
        self.json_data = json.loads('{}')
        try: 
            self.json_data = json.loads(json_string)
            self.cmd = self.json_data["cmd"]
        except:
            print("Could not read JSON")
            self.cmd = None
        
        
    def get(self,key):
        if key in self.json_data:
            return self.json_data[key]
        return None
        
        
    def get_or(self,key,default):
        v = self.get(key)
        if v == None:
            return default
        
        return v
        
class EchoRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # Echo the back to the client
        data = self.request.recv(1024)
        print(data)
        dispatch(data)
        self.request.send(b'ok')
        return
       
def close_server():
	global server
	try:
		server.shutdown(1)
	except:
		print("server not connected")
	finally:
		server.socket.close()

def signal_handler(signal, frame):
	print('You pressed Ctrl+C!')
	close_server()
	sys.exit(0)


def start_server(port):
    global server
    
    server = socketserver.TCPServer(('192.168.1.83',port), EchoRequestHandler)
    signal.signal(signal.SIGINT, signal_handler)
    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True) # don't hang on exit
    t.start()
    print("started server ... waiting for connections")
    
    while 1:
        pass
    
# delay milliseconds
def delay(t):
    sleep(t/1000.0)
    
# drive speed and angle
def drive(speed = 0.0, angle = 0.0):
    
    if speed == 0.0 and angle == 0.0:
        free()
        return
    
    if angle == 0 or angle ==360:
        d1 = speed
        d2 = 0.0
    elif angle <= 90:
        d1 = speed
        d2 = (angle/90.0)
    elif angle <= 180:
        d1 = -speed
        d2 = 1.0-(angle-90)/90.0
    elif angle < 270:
        d1 = -speed
        d2 = -(1.0-(angle-180)/90.0)
    elif angle < 360:
        d1 = speed
        d2 = -(1.0-(angle-270)/90.0)
        
    d1 = -d1
    d2 = -d2
    
    motor1.set(d1)
    motor2.set(d2)
    
# free spin
def free():
    motor1.free_spin()
    motor2.free_spin()

# Dispatch message
def dispatch(data):
    print(data)
    
    command = Command(data.decode('utf-8'))
    cmd = command.cmd
    
    if cmd == "drive":
        drive(command.get_or("speed",0.0),command.get_or("angle",0.0))
    else:
        print("unknown command")
    
def main():
    
    #for angle in range(0,360,45):
        
    #    print(angle)
        
    #    drive(0.75,angle)
    #    delay(500)
    #    free()
    
    start_server(8000)
    #dispatch(b'{"cmd":"drive","speed":0.531293733793099,"angle":120.127052307129}')
    #delay(200)
    #drive(0,0)
    pass
    
    
    
    
    

if __name__ == "__main__": main()