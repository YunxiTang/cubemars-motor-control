import struct
import can
import time
import numpy as np


P_MIN, P_MAX = -12.5, 12.5
V_MIN, V_MAX = -200.0, 200.0
T_MIN, T_MAX = -10.0, 10.0


def uint_to_float(x_int, x_min, x_max, bits):
    """
    将无符号整数映射为浮点数
    """
    span = x_max - x_min
    return float(x_int) * span / ((1 << bits) - 1) + x_min


def parse_motor_feedback(data: bytes):
    """
    解析电机反馈（8字节CAN数据）

    输入:
        data: bytes 或 list[int]，长度必须为8

    返回:
        dict: {
            pos, vel, torque,
            temp_driver, temp_motor,
            error
        }
    """

    if len(data) != 8:
        raise ValueError(f"Invalid data length: {len(data)}, expected 8")

    # 转成 list[int] 方便处理
    if isinstance(data, bytes):
        d = list(data)
    else:
        d = data

    # ====== 按照C代码解析 ======

    error = d[0] >> 4

    pos_int = (d[1] << 8) | d[2]

    spd_int = (d[3] << 4) | (d[4] >> 4)

    t_int = ((d[4] & 0x0F) << 8) | d[5]

    temp_driver = d[6]
    temp_motor = d[7]

    # ====== 转换为浮点 ======

    pos = uint_to_float(pos_int, P_MIN, P_MAX, 16)
    vel = uint_to_float(spd_int, V_MIN, V_MAX, 12)
    torque = uint_to_float(t_int, T_MIN, T_MAX, 12)

    return {
        "pos": pos,
        "vel": vel,
        "torque": torque,
        "temp_driver": temp_driver,
        "temp_motor": temp_motor,
        "error": error,
    }


def send_pos_vel(bus, can_id, pos, vel):
    """
    位置速度模式控制（对应 ctrl_motor2）

    参数:
        can_id : 电机ID（CAN ID）
        pos    : 位置 (float, -12.5 ~ 12.5 rad)
        vel    : 速度 (float, -200 ~ 200 rad/s)
    """

    # float → 4 bytes (little-endian)
    data = struct.pack("<ff", pos, vel)

    msg = can.Message(
        arbitration_id=can_id,
        data=data,   # 8 bytes
        is_extended_id=False
    )

    bus.send(msg)


motor_id = 0x0101

freq = 1000  # Hz
vel = 100   # enable 用 0 更安全

target_motor_pos = []
real_motor_pos = []
ts = []

with can.interface.Bus(channel="slcan0", interface="socketcan") as bus:
    
    # enable motor
    message = can.Message(
            arbitration_id=0x0101, 
            data=[0xFF]*7 + [0xFC], 
            is_extended_id=False
            )
    try:
        bus.send(message)
        print(f"Message sent: ID=0x0101, Data={[0xFF]*7 + [0xFC]}")
        
    except Exception as e:
        print(f"Error sending message: {e}")

    t = time.time()
    last_time = t
    
    message = bus.recv()
    feedback = parse_motor_feedback(message.data)
    current_pos = feedback["pos"]
    # start sending position and velocity commands at 100 Hz
    for i in range(10000):
        curr_t = time.time() - t
        
        pos = np.sin(curr_t) * 2.0 + current_pos  # Example: sinusoidal position command with amplitude of 5 rad
        target_motor_pos.append(pos)
        send_pos_vel(bus, can_id=motor_id, pos=pos, vel=vel)
        
        dt = time.time() - last_time
        if dt < 1.0 / freq:
            time.sleep(1.0 / freq - dt)
        
        ts.append(time.time() - t)
        
        # message = bus.recv(timeout=1.0)
        
        # if message:
        #     feedback = parse_motor_feedback(message.data)
        #     real_motor_pos.append(feedback["pos"])         
            # print(f'actual_freq: {1./ (time.time() - last_time + 1e-6):.2f} Hz')
        last_time = time.time()

    # disable motor
    message = can.Message(
            arbitration_id=motor_id, 
            data=[0xFF]*7 + [0xFD], 
            is_extended_id=False
            )
    bus.send(message)     
# import matplotlib.pyplot as plt

# plt.plot(ts, target_motor_pos, label="Target Position")
# plt.plot(ts, real_motor_pos, label="Real Position")
# plt.xlabel("Time (s)")
# plt.ylabel("Position (rad)")
# plt.title("Motor Position Tracking")
# plt.legend()
# plt.show()

# compute frequency
actual_freq = len(ts) / ts[-1]
print(f"Actual control frequency: {actual_freq:.2f} Hz")