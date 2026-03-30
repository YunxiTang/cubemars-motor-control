import time
from can_bus import CANBus
from motor import CubeMarsMotor
from utils import parse_motor_feedback

def main():
    bus = CANBus(channel='slcan0', interface='socketcan', bitrate=1000000)
    motor = CubeMarsMotor(can_id=0x0101, can_bus=bus)
    
    print("[INFO] Enable motor-ing")
    
    motor.enable()
    time.sleep(1)
    
    motor.clear_error()
    
    motor_state = motor.get_state()
    
    for key, value in parse_motor_feedback(motor_state.data).items():
        print(f"{key}: {value}")
    
    # motor.zero()
    
    # motor.disable()
    
if __name__ == '__main__':
    main()