import sys
import threading
import time

from evdev import UInput, ecodes as e
from pyjoycon import JoyCon, get_L_id, get_R_id


class status:
    RESET = '\033[0m'
    V = '\033[90m'
    ERR = '\033[91m'
    OK = '\033[92m'
    WARN = '\033[93m'


pid_joycons = {
    0x2006: "Joy-Con (L)",
    0x2007: "Joy-Con (R)"
}

hit_window = 5000    # minimum rotation angle to trigger swing
poll_rate = 0.0167
sensitivity = 4000   # mistrigger prevention during polling

try:
    # start your joycons...
    joycon_l_id = get_L_id()
    joycon_r_id = get_R_id()

    joycon_l = JoyCon(*joycon_l_id)
    joycon_r = JoyCon(*joycon_r_id)
except ValueError:
    print(f"{status.ERR}Failed to detect Joy-Con! Exiting...{status.RESET}")
    sys.exit(1)
except OSError:
    print(f"{status.ERR}Joy-Con detected, but failed to connect! Exiting..."
          f"{status.RESET}")
    sys.exit(1)
except AssertionError:
    print(f"{status.WARN}Joy-Con thread not ready, try again (joycon-python "
          f"quirk). Exiting...{status.RESET}")
    sys.exit()


def poll_joycon(pid, joycon):
    print(f"Started polling {pid_joycons[pid]}")

    # initialise right after starting polling
    cur_read = joycon.get_accel_y()
    prev_read = cur_read

    with UInput({e.EV_KEY: [e.KEY_D, e.KEY_F, e.KEY_J, e.KEY_K]}) as ui:
        while True:
            cur_read = joycon.get_accel_y()

            accel_z = joycon.get_accel_z()
            gyro_z = joycon.get_gyro_z()

            # print(f"[{pid_joycons[pid]}] cur:{cur_read} prev:{prev_read}")
            # TODO: little rumble action at some point? check github issues

            # dangerous maths (TODO: something that's maybe better?)
            if (prev_read < cur_read and
                abs(prev_read - cur_read) > sensitivity and
                    cur_read < hit_window):
                # TODO: better implementation, less magic numbers
                if gyro_z < -5000 or gyro_z > 5000:
                    if pid == 0x2006:
                        if accel_z > 1800:
                            ui.write(e.EV_KEY, e.KEY_D, 1)
                            ui.write(e.EV_KEY, e.KEY_D, 0)
                            ui.syn()
                        else:
                            ui.write(e.EV_KEY, e.KEY_F, 1)
                            ui.write(e.EV_KEY, e.KEY_F, 0)
                            ui.syn()
                    elif pid == 0x2007:
                        if accel_z < -1800:
                            ui.write(e.EV_KEY, e.KEY_K, 1)
                            ui.write(e.EV_KEY, e.KEY_K, 0)
                            ui.syn()
                        else:
                            ui.write(e.EV_KEY, e.KEY_J, 1)
                            ui.write(e.EV_KEY, e.KEY_J, 0)
                            ui.syn()

            prev_read = cur_read
            time.sleep(poll_rate)


def main():
    thread_joycon_l = threading.Thread(target=poll_joycon,
                                       args=(joycon_l_id[1], joycon_l))
    thread_joycon_r = threading.Thread(target=poll_joycon,
                                       args=(joycon_r_id[1], joycon_r))

    thread_joycon_l.daemon = True
    thread_joycon_r.daemon = True

    thread_joycon_l.start()
    thread_joycon_r.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nStopping polling and exiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
