import struct
import can
import time

# ====== 参数范围（根据你的说明书）======
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
    
    # get the motor state for 100 iterations
    for i in range(100):
        
        msg = bus.recv(timeout=1.0)

        if msg is None:
            print("No message received")
            continue

        try:
            
            state = parse_motor_feedback(msg.data)

            print(f"""
                [Motor State]
                pos     = {state['pos']:.3f} rad
                vel     = {state['vel']:.3f} rad/s
                torque  = {state['torque']:.3f} Nm
                temp_d  = {state['temp_driver']} °C
                temp_m  = {state['temp_motor']} °C
                error   = {state['error']}
                """)
            
            time.sleep(0.01)

        except Exception as e:
            print("Parse error:", e)