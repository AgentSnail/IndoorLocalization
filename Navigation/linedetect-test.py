#!/usr/bin/env python

'''
face detection using haar cascades

USAGE:
    facedetect.py [--cascade <cascade_fn>] [--nested-cascade <cascade_fn>] [<video_source>]
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy

import threading
import time
import numpy
from breezycreate2 import Robot

global bot

def robotcontrol(linefollowinput):
    global bot
    speed = 15
    rotspeed = 150
    correctradius = -600
    correctradiusmedium = -400
    correctradiushard= -100

class testMove ():
    def move200(self):
        speed2 = 15
        runtime = 133.33
        bot.robot.drive_straight(speed2)
        time.sleep(runtime)
        # Speed 100 = 0.1 m per second, 10 seconds to make 1 meter
        # does faster speed mean less accuracy?
        # stop after certain amount of time
        bot.robot.drive_straight(0)

    def move400(self):      #double as fast, same time to get 2 times distance
        speed3 = 200
        runtime2 = 20
        bot.robot.drive_straight(speed3)
        time.sleep(runtime2)
        # stop after certain amount of time
        bot.robot.drive_straight(0)

threads = []
if __name__ == '__main__':
    import sys, getopt

#def main():
    try:
        bot = Robot()
        movement = testMove()
        movement.move200()
        str('testgood')
        #return 0
    except:
        str('test')
        #return 1