# bachi
swing to hit taiko motion controls with Joy-Con

### huh?
I play Taiko no Tatsujin on my Nintendo Switch occasionally, and there's an option to use motion controls to swing as if there was an actual taiko in front of you, rather than using the buttons. It's fun, but it kinda sucks. I think it's a neat gimmick however, and I play Taiko simulators and clones on PC sometimes, so I thought I'd implement it for PC Taiko players.

**disclaimer:** Uh, okay so, the way this works is, when you swing and it's supposed to be a hit, input is injected using evdev. Most things play nice with this, but certain applications may not like this. The degree of "not like this" can vary from simply not working to triggering anti-cheat measures if they exist.

It's good to check beforehand if this is okay to use in whatever taiko simulator you're playing, especially if there's score submission and leaderboards involved.

### quick setup
this script uses a few packages to do its thing: joycon-python, hid, evdev, and PyGLM. to avoid package confusion and the hassle of distro shipped python packages vs. what's supposed to be used, I recommend a local venv setup: 

```
git clone https://github.com/mutmux/bachi.git
cd bachi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Then, connect your left and right Joy-Con to your PC via Bluetooth. Certain Linux users may need to use [these udev rules](https://www.reddit.com/r/Stadia/comments/egcvpq/using_nintendo_switch_pro_controller_on_linux/fc5s7qm/) to access the devices without root (or at all). Depending on your distro and setup, you may or may not also require [joycond](https://github.com/DanielOgorchock/joycond). I don't actually know if this script works fine on Windows, hopefully it does!

After working all that out, you can finally run the script with `python bachi.py` inside the local venv, **with your Joy-Con upright on a flat surface**. If everything went okay, the two Joy-Con connected should be picked up by the script, and polling should start after a brief moment. Once text starts spewing out in the terminal, you can use the Joy-Con like bachi in whatever taiko simulator or clone you want.

### configuration
You can change keybinds in the script yourself if you'd like. The default is DFJK (KDDK layout). As part of registering hits, I needed to make up a few constants for stuff like minimum force required, thresholds for swinging and tilting the Joy-Con. The default settings there are what I find the least annoying for how I play, but you can fiddle with it and see what works better for you. It's a pain, though. There's also a basic hit delay in place after a successfully registered hit, just for a simple means of preventing misfire as you complete a full swing.

### future plans, maybe
- add rumble support
- toggles for either Joy-Con
- alternative layout support
