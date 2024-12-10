import board
import pwmio
import time

# Set up PWM on GPIO 15
Fan_PWM = pwmio.PWMOut(board.GP0, frequency=2500, duty_cycle=0)
temp = 69
set_temp = 70
setting = "heating on"

# Function to set fan speed (0 to 100%)
def set_fan_speed(speed):
    if 0 <= speed <= 100:
        duty_cycle = int((speed / 100) * 65535)
        Fan_PWM.duty_cycle = duty_cycle
        return speed
    else:
        print("Speed must be between 0 and 100")

# Example usage
while True:
    if temp < set_temp -5 and setting == "heating on":
        set_fan_speed(100)  
        time.sleep(5)
        temp = 71
        setting = "cooling on"
    elif temp <= set_temp -3 and setting == "heating on":
        set_fan_speed(50)  
        time.sleep(5)
        temp = 71
        setting = "cooling on"
    elif temp <= set_temp -1 and setting == "heating on":
        set_fan_speed(25)  
        time.sleep(5)
        temp = 71
        setting = "cooling on"
    elif temp > set_temp + 5 and setting == "cooling on":
        set_fan_speed(100)   
        time.sleep(5)
        setting = "on"
    elif temp >= set_temp + 3 and setting == "cooling on":
        set_fan_speed(50)   
        time.sleep(5)
        setting = "on"
    elif temp >= set_temp + 1and setting == "cooling on":
        set_fan_speed(25)   
        time.sleep(5)
        setting = "on"
    elif setting == "on":
        set_fan_speed(100)    # 0% speed (off)
        time.sleep(5)
        setting = "off"
    elif setting == "off":
        set_fan_speed(0)
        time.sleep(5)
        
