import struct
import can
import time
import numpy as np


# ===================== 参数 =====================

P_MIN, P_MAX = -12.5, 12.5
V_MIN, V_MAX = -200.0, 200.0
T_MIN, T_MAX = -10.0, 10.0

MOTOR_ID = 0x0101
FREQ = 1000  # Hz

OPEN_POS = 0.53 # rad
CLOSE_POS = 0.76 # rad


# ===================== 工具函数 =====================

def uint_to_float(x_int, x_min, x_max, bits):
    span = x_max - x_min
    return float(x_int) * span / ((1 << bits) - 1) + x_min


def parse_motor_feedback(data: bytes):
    if len(data) != 8:
        raise ValueError(f"Invalid data length: {len(data)}, expected 8")

    d = list(data)

    error = d[0] >> 4
    pos_int = (d[1] << 8) | d[2]
    spd_int = (d[3] << 4) | (d[4] >> 4)
    t_int = ((d[4] & 0x0F) << 8) | d[5]

    temp_driver = d[6]
    temp_motor = d[7]

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
    data = struct.pack("<ff", pos, vel)

    msg = can.Message(
        arbitration_id=can_id,
        data=data,
        is_extended_id=False
    )

    try:
        bus.send(msg)
    except can.CanError as e:
        print(f"[WARN] CAN send failed: {e}")


def enable_motor(bus, can_id):
    msg = can.Message(
        arbitration_id=can_id,
        data=[0xFF]*7 + [0xFC],
        is_extended_id=False
    )
    bus.send(msg)
    print("Motor enabled")


def disable_motor(bus, can_id):
    msg = can.Message(
        arbitration_id=can_id,
        data=[0xFF]*7 + [0xFD],
        is_extended_id=False
    )
    bus.send(msg)
    print("Motor disabled")


# ===================== 主程序 =====================

def main():

    target_motor_pos = []
    real_motor_pos = []
    ts = []

    with can.interface.Bus(channel="slcan0", interface="socketcan") as bus:

        # enable
        enable_motor(bus, MOTOR_ID)

        time.sleep(0.1)  # 等待设备稳定

        # 尝试读取一次当前位姿（非阻塞）
        message = bus.recv(timeout=0.1)
        if message:
            feedback = parse_motor_feedback(message.data)
            current_pos = feedback["pos"]
        else:
            print("[WARN] No feedback received, using 0 as initial pos")
            raise RuntimeError("No feedback received, cannot get initial position")

        start_time = time.time()
        next_time = start_time

        # 控制循环
        for i in range(10000):

            now = time.time()
            t = now - start_time

            # ===== 控制信号 =====
            if i < 5000:
                target_pos = OPEN_POS
            else:                
                target_pos = CLOSE_POS
            target_vel = 1.0
            target_motor_pos.append(target_pos)

            send_pos_vel(bus, MOTOR_ID, target_pos, target_vel)

            # ===== 读取反馈（非阻塞）=====
            message = bus.recv(timeout=0.0)
            if message:
                feedback = parse_motor_feedback(message.data)
                real_motor_pos.append(feedback["pos"])
            else:
                real_motor_pos.append(np.nan)

            ts.append(t)

            # ===== 精确频率控制 =====
            next_time += 1.0 / FREQ
            sleep_time = next_time - time.time()

            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # 频率已经跟不上
                next_time = time.time()

        # disable
        disable_motor(bus, MOTOR_ID)

    # ===================== 统计 =====================

    actual_freq = len(ts) / ts[-1]
    print(f"Actual control frequency: {actual_freq:.2f} Hz")


if __name__ == "__main__":
    main()