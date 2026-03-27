import can


class CANBus:
    def __init__(self, channel:str = 'slcan0', bustype: str ='socketcan', bitrate=1000000):
        self.channel = channel
        self.bustype = bustype
        self.bitrate = bitrate
        self.bus = None
        
        if self.bustype == 'socketcan':
            self.setup()
        else:
            print(f"Unsupported bus type: {self.bustype}. Only 'socketcan' is supported.")

    def setup(self):
        try:
            self.bus = can.interface.Bus(channel=self.channel, interface=self.bustype, bitrate=self.bitrate)
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
            print(f"Message sent: ID={arbitration_id}, Data={data}")
        except Exception as e:
            print(f"Error sending message: {e}")

    def receive_message(self):
        if self.bus is None:
            print("CAN bus is not set up. Call setup() first.")
            return
        
        try:
            message = self.bus.recv(timeout=1.0)  # Wait for a message for 1 second
            if message:
                print(f"Message received: ID={message.arbitration_id}, Data={message.data}")
                return message
            else:
                print("No message received within the timeout period.")
                return None
        except Exception as e:
            print(f"Error receiving message: {e}")