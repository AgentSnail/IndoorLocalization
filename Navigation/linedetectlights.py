#!/usr/bin/env python

'''
face detection using haar cascades

USAGE:
    facedetect.py [--cascade <cascade_fn>] [--nested-cascade <cascade_fn>] [<video_source>]
'''

# Python 2/3 compatibility
from __future__ import print_function

import imutils
import numpy
from imutils.video.pivideostream import PiVideoStream
from picamera import PiCamera
from picamera.array import PiRGBArray
import threading
import time
from breezycreate2 import Robot
#from imutils.video import FPS

import cv2

# local modules
from common import clock, draw_str

#These are all imports for lighting
from neopixel import *
import argparse
import signal
import sys

def signal_handler(signal, frame):
        colorWipe(strip, Color(0,0,0))
        sys.exit(0)

def opt_parse():
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', action='store_true', help='clear the display on exit')
        args = parser.parse_args()
        if args.c:
                signal.signal(signal.SIGINT, signal_handler)

# LED strip configuration:
LED_COUNT      = 10      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


global bot

boundaries = [
    ([5, 50, 50], [25, 230, 230]), #orange
    ([100, 50, 50], [120, 230, 230]) #blue
    ]

def robotcontrol(linefollowinput):
    global bot
    speed = 15
    rotspeed = 150
    correctradius = -600
    correctradiusmedium = -400
    correctradiushard= -100
    text = linefollowinput
    
    if(text == "Test"):
        bot.playNote('A4', 50)
    elif(text == "ReCon"):
        bot = Robot()
    elif(text == "Forward"):
        bot.robot.drive_straight(speed)
    elif(text == "Backward"):
        bot.robot.drive_straight(-speed)
    elif(text == "Left90"):
        bot.robot.turn_counter_clockwise(rotspeed)
    elif(text == "Right90"):
        bot.robot.turn_clockwise(rotspeed)
    elif(text == "LeftCorrect"):
        bot.robot.drive(speed, correctradius)
    elif(text == "RightCorrect"):
        bot.robot.drive(speed, -correctradius)
    elif(text == "LeftCorrectMedium"):
        bot.robot.drive(speed, correctradiusmedium)
    elif(text == "RightCorrectMedium"):
        bot.robot.drive(speed, -correctradiusmedium)
    elif(text == "LeftCorrectHard"):
        bot.robot.drive(speed, correctradiushard)
    elif(text == "RightCorrectHard"):
        bot.robot.drive(speed, -correctradiushard)
    elif(text == "RightDrift"):
        bot.robot.drive(speed, -correctradius)
    elif(text == "LeftDrift"):
        bot.robot.drive(speed, correctradius)
    elif(text == "Stop"):
        bot.robot.drive_straight(0)
    elif(text == "Terminator"):
        bot.playNote('A4', 5)
    else:
        bot.robot.drive_straight(0)
        print("incorrect command")
            


class ColorFinder(threading.Thread):
    def __init__(self, color):
        threading.Thread.__init__(self)
        self.color = color

    def run(self):
        
        hsv = cv2.cvtColor(self.color, cv2.COLOR_BGR2HSV)
        blue = 0
        for(lower, upper) in boundaries:
            #create arrays from boundaries
            lower = numpy.array(lower, dtype = numpy.uint8)
            upper = numpy.array(upper, dtype = numpy.uint8)
            color = cv2.inRange(hsv, lower, upper)
        blue = cv2.countNonZero(color)
        if (blue >= 3000):
            print("I see Blue (" + str(blue) + ")")
        cv2.imshow("color mask", color)

        
class LineFinder (threading.Thread):
    def __init__(self, line):
        threading.Thread.__init__(self)
        self.line = line 
        
    def run(self):
        gray = cv2.cvtColor(self.line, cv2.COLOR_BGR2GRAY)
        edged = cv2.Canny(gray, 50, 150, apertureSize = 3)
        minLineLength = 30
        maxLineGap = 10
        command = ""
        lines = cv2.HoughLinesP(edged, 1, numpy.pi/180,15,minLineLength,maxLineGap)
        if lines is not None:
            slope = 0;
            drift = 0;
            for x in range(0, len(lines)):
                for x1, y1, x2, y2 in lines[x]:
                    cv2.line(line, (x1,y1),(x2,y2),(0,255,0),2)
                    slope = slope + (y2-y1)/(x2-x1)
                    drift = x1 + drift
                print(drift)
            slope = slope/len(lines)
            drift = drift/len(lines)
            if((slope > 0) & (slope < 7)):
                print("robot should turn right hard")
                command = "RightCorrectHard"
                
            elif((slope < 0) & (slope > -7)):
                print("robot should turn left hard")
                command = "LeftCorrectHard"
                
            elif((slope < -7) & (slope > -14)):
                print("robot should turn left")
                command = "LeftCorrectMedium"
                
            elif((slope > 7) & (slope < 14)):
                print("robot should turn right")
                command = "RightCorrectMedium"
                      
            elif((slope < -14) & (slope > -20)):
                print("robot should turn left slightly")
                command = "LeftCorrect"
                
            elif((slope > 14) & (slope < 20)):
                print("robot should turn right slightly")
                command = "RightCorrect"
                
            elif(drift<120):
                print("robot should correct drift left")
                command = "RightDrift"
            elif(drift>200):
                print("robot should correct drift right")
                command = "LeftDrift"
            else:
                print("robot should go straight")
                command = "Forward"
            
        else:
            print("No lines found")
            command = "Stop"
            
        robotcontrol(command)

threads = []       
if __name__ == '__main__':
    import sys, getopt
#    print(__doc__)
    print("Setting up webcam...")
    args, video_src = getopt.getopt(sys.argv[1:], '', ['cascade=', 'nested-cascade='])
    bot = Robot()
    print("Connected to Robot")
    try:
        video_src = video_src[0]
    except:
        video_src = 0
    args = dict(args)
    print("Found Webcam!")
    camera = PiCamera()
    camera.resolution = (320, 240)
    camera.framerate = 20
    rawCapture = PiRGBArray(camera)
    
    opt_parse() #this is for the LED setup

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    strip.begin()
	
    for i in range(strip.numPixels()):
	strip.setPixelColor(i, Color(127,127,127))
	strip.show()
    
    time.sleep(2)
    

    while(True):
        #print("reading cam")
        camera.capture(rawCapture, format = "bgr")
        img = rawCapture.array
        #img = frame.array
        line = img.copy()
        color = img.copy()
        
        lineThread = LineFinder(line)
        lineThread.start()
        
        colorThread = ColorFinder(color)
        colorThread.start()

        lineThread.join()
        colorThread.join();
        
#        img = lineThread.img
        cv2.imshow("line                    color", numpy.hstack([line, color]))#        cv2.imshow("color", line, color)
        #cv2.imshow('linedetect', line)
        rawCapture.truncate(0)
        if 0xFF & cv2.waitKey(5) == 27:
            break
    cv2.destroyAllWindows()



        
    
 