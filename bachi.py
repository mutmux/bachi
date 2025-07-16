import sys
import threading
import time

from evdev import UInput, ecodes as e
from pyjoycon import JoyCon, get_L_id, get_R_id


pid_joycons = {
    0x2006: "Joy-Con (L)",
    0x2007: "Joy-Con (R)"
}

poll_rate = 1 / 300  # in hz
swing_force_thres = 3000   # misfire prevention, increase to require more swing force
swing_hit_thres = 4000   # downward swing angle (via accel_y) to determine hit
swing_tilt_thres = 1800   # sideways swing angle (via accel_z) to differentiate don/kat

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


def poll_joycon(pid, joycon):
    print(f"Started polling {pid_joycons[pid]}")

    # initialise right after starting polling
    accel_y_cur = joycon.get_accel_y()
    accel_y_prev = accel_y_cur

    with UInput({e.EV_KEY: [e.KEY_D, e.KEY_F, e.KEY_J, e.KEY_K]}) as ui:
        while True:
            accel_y_cur = joycon.get_accel_y()

            accel_z = joycon.get_accel_z()
            gyro_z = joycon.get_gyro_z()

            print(f"{pid_joycons[pid]}\ty:{accel_y_cur}  z:{accel_z}  gyro:{gyro_z}")

            # TODO: use madgwick filter with accel and gyro data for maintaining accuracy
            # redo all this shit!
            if (accel_y_prev < accel_y_cur and
                abs(accel_y_prev - accel_y_cur) > swing_force_thres and
                    accel_y_cur < swing_hit_thres):
                # TODO: better implementation
                # TODO: rumble on hit
                if gyro_z < swing_force_thres * -1:
                    if pid == 0x2006:
                        if accel_z > swing_tilt_thres:
                            ui.write(e.EV_KEY, e.KEY_D, 1)
                            ui.write(e.EV_KEY, e.KEY_D, 0)
                            ui.syn()
                        else:
                            ui.write(e.EV_KEY, e.KEY_F, 1)
                            ui.write(e.EV_KEY, e.KEY_F, 0)
                            ui.syn()
                    elif pid == 0x2007:
                        if accel_z < swing_tilt_thres * -1:
                            ui.write(e.EV_KEY, e.KEY_K, 1)
                            ui.write(e.EV_KEY, e.KEY_K, 0)
                            ui.syn()
                        else:
                            ui.write(e.EV_KEY, e.KEY_J, 1)
                            ui.write(e.EV_KEY, e.KEY_J, 0)
                            ui.syn()

            accel_y_prev = accel_y_cur
            time.sleep(poll_rate)


def main():
    thread_joycon_l = threading.Thread(target=poll_joycon, args=(joycon_l_id[1], joycon_l))
    thread_joycon_r = threading.Thread(target=poll_joycon, args=(joycon_r_id[1], joycon_r))

    thread_joycon_l.daemon = True
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
