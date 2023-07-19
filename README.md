# olfactory-display-for-metaverse

Software and CAD files for paper ["An open-source Olfactory Display to add the sense of smell to the Metaverse"](https://asmedigitalcollection.asme.org/computingengineering/article/doi/10.1115/1.4062889/1164268/An-open-source-Olfactory-Display-to-add-the-sense) in Journal of Computing and Information Science in Engineering.

If you use this in your academic work, please cite as:

> Lukasiewicz, M. S., Rossoni, M., Spadoni, E., Dozio, N., Carulli, M., Ferrise, F., & Bordegoni, M. (2023). An open-source Olfactory Display to add the sense of smell to the Metaverse. *Journal of Computing and Information Science in Engineering,* 1–12. [https://doi.org/10.1115/1.4062889](https://doi.org/10.1115/1.4062889)

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

Models designed with Solidworks 2022 Education Edition

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
