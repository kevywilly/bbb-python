import rcpy.gpio as gpio
pause_button = gpio.Input(gpio.PAUSE_BTN)

class MyInputEvent(gpio.InputEvent):
    def action(self, event):
        print('Got <PAUSE>!')
        
        
        
pause_event = MyInputEvent(pause_button, gpio.InputEvent.LOW)

pause_event.start()

print("Hello")
