#### requirements
- a pair of Joy-Con controllers (Left and Right)
- a machine with a bluetooth adapter that works with Joy-Con
- `hidapi` (also known as `libhidapi-hidraw0` on some distros)

- for some distros, the appropriate [udev rules](https://www.reddit.com/r/Stadia/comments/egcvpq/comment/fc5s7qm) for your Joy-Con may also be necessary.

Python-specific requirements include:
- [evdev](https://pypi.org/project/evdev/)
- [PyGLM](https://pypi.org/project/PyGLM/)
- [hidapi](https://pypi.python.org/pypi/hidapi/) by trezor, built with hidraw API (**not libusb**)
- [joycon-python](https://pypi.org/project/joycon-python/)


depending on your system, you should be able to install all dependencies using pip:
```
pip install -r requirements.txt
```

if your system disallows installations using pip, you can use your system's package manager to install the associated requirements. *please make sure your system offers you the right packages, and not others that are similarly named.* for example, Ubuntu includes the package `python3-hidapi`, but it is **not** the right package.


#### how to use
1. place your Joy-Con parallel on a flat surface, buttons upward and pointing toward your display.
2. start the script with `python3 ./joycon_bachi.py`. on some systems, you may need elevated permissions to access or emulate input devices. `sudo python3 ./joycon_bachi.py`
3. wait for both controllers to start polling. then, you're ready to go :)

default keybinds for swings in joycon-bachi are DFJK -- that is, left kat, left don, right don, right kat respectively. at the moment, this can only be adjusted by modifying the script.

#### known issues
- pretty much all gyroscopes in consumer devices are susceptible to drift, which can be problematic when relied upon for angular velocity detection. an orientation reset and basic calibration is done at the start of the script using included joycon-python functions, but the script may require a restart if you find yourself needing to use exceptional force in your swings to register a hit. I may look into adding additional calculations to counter drift if it bothers me or others that use this.
- the current calculations used to determine swings and associated hits (don/kat) are not the best, and need further refinement. based on your preferences, you may find the range at which a hit is registered to be too narrow or too sparse. I intend to add customisation at some point, and maybe even some form of interactive calibration, but in the meantime, you can experiment and manually adjust the script.
