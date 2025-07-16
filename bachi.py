import sys
import threading
import time

from evdev import UInput, ecodes as e
from pyjoycon import JoyCon, get_L_id, get_R_id

pid_joycons = {
    0x2006: "Joy-Con (L)",
    0x2007: "Joy-Con (R)"
}

cap = {
    e.EV_KEY: [e.KEY_D, e.KEY_F, e.KEY_J, e.KEY_K]
}

POLL_RATE = 300             # times per second to poll joy-con
HIT_DELAY = 100             # time in ms to block polling thread after a registered hit

FORCE_REQ = 3500            # swing force requirement based on gyro_z to prevent misfire
MIN_DIFF = 6000             # minimum difference between accel_y of current and previous poll
DOWN_SWING_THRES = 3250     # downward swing angle (via accel_y) to determine hit
TILT_SWING_THRES = 2000     # sideways swing angle (via accel_z) to determine don/kat

def send_key(ui, key):
    # briefly block thread after sending a key to prevent extraneous hits as swing completes.
    # TODO: a better approach than this
    # TODO: rumble on hit?
    ui.write(e.EV_KEY, key, 1)
    ui.write(e.EV_KEY, key, 0)
    ui.syn()
    time.sleep(HIT_DELAY / 1000)

def poll_joycon(pid, joycon):
    print(f"Started polling {pid_joycons[pid]}")

    accel_y_prev = 0

    with UInput(cap) as ui:
        while True:
            # TODO: filter considerations in future for any accelerometer drift
            accel_y_cur = joycon.get_accel_y()
            accel_z = joycon.get_accel_z()
            gyro_z = joycon.get_gyro_z()

            print(f"{pid_joycons[pid]}\ty:{accel_y_cur}  z:{accel_z}  gyro:{gyro_z}")

            # provided there's enough force on the gyro, register a hit if:
            # - difference between previous & current accel_y readings is significant, AND
            # - current accel_y reading is more than previous reading (implied), AND
            # - current accel_y reading meets the hit threshold (is at a minimum downward angle)
            if gyro_z < FORCE_REQ * -1:
                if accel_y_cur - accel_y_prev > MIN_DIFF and accel_y_cur >= DOWN_SWING_THRES:
                    if pid == 0x2006:
                        if accel_z > TILT_SWING_THRES:
                            send_key(ui, e.KEY_D)
                        else:
                            send_key(ui, e.KEY_F)
                    elif pid == 0x2007:
                        if accel_z < TILT_SWING_THRES * -1:
                            send_key(ui, e.KEY_K)
                        else:
                            send_key(ui, e.KEY_J)

            accel_y_prev = accel_y_cur
            time.sleep(1 / POLL_RATE)

def main():
    try:
        # start your joycons...
        joycon_l_id = get_L_id()
        joycon_r_id = get_R_id()

        joycon_l = JoyCon(*joycon_l_id)
        joycon_r = JoyCon(*joycon_r_id)
    except ValueError:
        print("Failed to detect Joy-Con L/R (either, or both)")
        sys.exit(1)
    except OSError:
        print("Joy-Con detected, but failed to connect")
        sys.exit(1)
    except AssertionError:
        print("Joy-Con thread not ready (joycon-python quirk)")
        sys.exit()

    thread_joycon_l = threading.Thread(target=poll_joycon, args=(joycon_l_id[1], joycon_l))
    thread_joycon_l.daemon = True
    thread_joycon_r = threading.Thread(target=poll_joycon, args=(joycon_r_id[1], joycon_r))
    thread_joycon_r.daemon = True

    thread_joycon_l.start()
    thread_joycon_r.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping polling and exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
