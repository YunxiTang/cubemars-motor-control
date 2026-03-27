from can_bus import CANBus


class CubeMarsMotor:
    def __init__(self, can_id: int, can_bus: CANBus):
        self.can_bus = can_bus
        self.can_id = can_id
        
    def enable(self):
        # Send a CAN message to enable the motor
        self.can_bus.send_message(self.can_id, [0xFF]*7 + [0xFC])
        
    def disable(self):
        # Send a CAN message to disable the motor
        self.can_bus.send_message(self.can_id, [0xFF]*7 + [0xFD])
        
        
    def zero(self):
        self.can_bus.send_message(self.can_id, [0xFF]*7 + [0xFE])
        
        
    def clear_error(self):
        self.can_bus.send_message(self.can_id, [0xFF]*7 + [0xFB])
        
    def get_state(self):
        self.can_bus.receive_message()