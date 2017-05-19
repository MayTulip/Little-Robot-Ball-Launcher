# Mei Yang (mny8), Jia Lin Zhu (jz352)
# Lab 3
# 3/16/2017

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.OUT)

p = GPIO.PWM(13, 1/0.0215)
p.start(100*1.5/21.5)

input('Press return to stop:')   # use raw_input for Python 2
p.stop()
GPIO.cleanup()
