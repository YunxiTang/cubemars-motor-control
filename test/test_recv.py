import struct
import can
import time
# bus = can.interface.Bus(channel="slcan0", interface="socketcan")

motor_id = 0x01
pos = 0.7   # 建议用 0
vel = 0.0   # enable 用 0 更安全

data = struct.pack("<Bff", motor_id, pos, vel)


with can.interface.Bus(channel="slcan0", interface="socketcan") as bus:
    for i in range(100):
        msg = can.Message(
            arbitration_id=0x0101,
            data=[0x00, 0x00, 0x40, 0x40, 0x00, 0x00, 0x80, 0x3F],
            is_extended_id=False
        )
        time.sleep(0.001)
        bus.send(msg)
        print('[INFO] Sent message: ID=0x0101, Data=[0x00, 0x00, 0x40, 0x40, 0x00, 0x00, 0x80, 0x3F]')
