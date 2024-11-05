import board
import pwmio
import time

# Set up PWM on GPIO 15
Fan_PWM = pwmio.PWMOut(board.GP10, frequency=2500, duty_cycle=0)

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
    set_fan_speed(100)  # 100% speed
    time.sleep(5)
    set_fan_speed(50)   # 50% speed
    time.sleep(5)
    set_fan_speed(0)    # 0% speed (off)
    time.sleep(5)
