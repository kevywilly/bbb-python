import json

class Command:
    
    def __init__(self, json_data_):
        self.json_data = json_data_
        try: 
            #self.json_data = json.loads(json_string)
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