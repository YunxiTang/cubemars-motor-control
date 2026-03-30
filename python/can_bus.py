import can


class CANBus:
    def __init__(self, channel:str = 'slcan0', interface: str ='socketcan', bitrate=1000000):
        self.channel = channel
        self.interface = interface
        self.bitrate = bitrate
        self.bus = None
        
        if self.interface == 'socketcan':
            self.setup()
        else:
            print(f"Unsupported interface: {self.interface}. Only 'socketcan' is supported.")

    def setup(self):
        '''Set up the CAN interface using python-can.'''
        try:
            self.bus = can.interface.Bus(channel=self.channel, interface=self.interface, bitrate=self.bitrate)
            print(f"CAN interface {self.channel} is set up with a bitrate of {self.bitrate} bps.")
        except Exception as e:
            print(f"Error setting up CAN interface: {e}")

    def send_message(self, arbitration_id, data):
        if self.bus is None:
            print("CAN bus is not set up. Call setup() first.")
            return
        
        message = can.Message(
            arbitration_id=arbitration_id, 
            data=data, 
            is_extended_id=False
            )
        try:
            self.bus.send(message)
        except Exception as e:
            print(f"Error sending message: {e}")


    def receive_message(self):
        if self.bus is None:
            print("CAN bus is not set up. Call setup() first.")
            return
        
        try:
            message = self.bus.recv(timeout=1.0)  # Wait for a message for 1 second
            if message:
                return message
            else:
                print("No message received within the timeout period.")
                return None
            
        except Exception as e:
            print(f"Error receiving message: {e}")