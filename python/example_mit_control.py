import time
from can_bus import CANBus
from motor import CubeMarsMotor

def main():
    bus = CANBus(channel='slcan0', bustype='socketcan', bitrate=1000000)
    motor = CubeMarsMotor(can_id=0x01, can_bus=bus)
    
    print("[INFO] Enable motor-ing")
    motor.enable()
    time.sleep(1)
    
    motor.clear_error()
    
    motor.zero()
    
    print( motor.get_state() )
    
    motor.disable()
    
    
if __name__ == '__main__':
    main()