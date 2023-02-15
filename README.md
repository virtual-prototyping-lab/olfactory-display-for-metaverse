# olfactory-display-for-metaverse

For paper "An open-source Olfactory Display to add the sense of smell to the Metaverse"

## Experiment setup

Provide the power for transducers from a different source than Arduino pins or the same USB cable. If they use the voltage line, the serial tends to hang (brownout?). Verified that a USB cable from different port works fine

The mix of aromas used is 10 drops per 1mL of water. After filling, and closing with cap, mix well by shaking. When starting the trial, use the buttons in window to check that both channels emit reliably. When recharged with 2mL each, both channels ran out during 8th participant that day.

To use the Python GUI, connect to Quest Link and show desktop. When the participant is wearing the Oculus Quest 2 HMD, the desktop view can be centered by pressing the Oculus button on the right motion controller.

## GUI

### Getting started

If using virtual environment, create it with system packages to make `tkinter` work properly.

```
python -m venv --system-site-packages venv
```

## Hardware

### Bill of Materials

Wearable configuration for Quest 2

- 3D printed [models at Thingiverse](https://www.thingiverse.com/thing:5852014):
  - Clip x7
  - FrontMount x1
  - Housing x2
  - Plug x2
- Arduino UNO x1
- Grove - Water Atomization x2
- _Optional: Grove Base Shield_ - can be replaced by cutting cables included with atomizers and soldering to male jumper cables
