# BallBalancingBot
Uses a Logitech Camera hooked up to my computer and pySerial to communicate to the ESP32 controlling 3 servo motors to balance the ball. 

In this case I am using a Table Tennis ball but honestly it totally depends on your use case, you just have to tweak the HSV values to detect something other than the orange I've kept here. I haven't tuned the PID values to perfection because I got lazy 😭😭. My method uses openCV to use the webcam input and map the general coordinates of the ball relative to the center of the platform. 

The x-distance and the y-distance are scaled down and sent to the ESP32 which does some basic inverse kinematics and maps servo values. The PID values are tuned on the ESP32 code itself and I might make a web version to tune it without having to flash the code all the time if I really have to.

In terms of hardware, any ESP32 works, I'm using 3 MG996R servo motors, a working webcam with a tripod and a laptop.

In terms of software, Arduino IDE and VSCode with OpenCV installed.

Some Small Things:
- Added a large circle on the python overlay to fit the platform and another small circle on the right to have a fixed reference point
- DO NOT open the serial monitor on Arduino IDE while the programs are running or else it just won't communicate.
- Center the Servo motors before attaching the hardware.
- If you're experiencing a LOT of oscillations, then try scaling down the dx and dy values in the "send" variable in python (default = 30) but you will have to redo the PID tuning.
- Consistent lighting (learnt this the hard way..)

This was pretty fun to make even though the concept is so simple and I'm definitely not the first one to do it this way so you'll find a lot of helpful resources online to improve this :)
