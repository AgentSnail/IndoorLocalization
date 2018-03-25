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

#color boundaries
##boundaries = [
##    ([86, 31, 4], [50, 56, 200]), #blue range
##    ([255, 140, 0], [255, 165, 0]) #orange range
##]
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
        #bot.robot.drive_straight(speed)
    elif(text == "LeftDrift"):
        bot.robot.drive(speed, correctradius)
        #bot.robot.drive_straight(speed)
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
        #print("running color detection thread")
#        threading.Lock().acquire()
        
        hsv = cv2.cvtColor(self.color, cv2.COLOR_BGR2HSV)
        #amount = numpy.array(amount)
        blue = 0
        for(lower, upper) in boundaries:
            #create arrays from boundaries
            lower = numpy.array(lower, dtype = numpy.uint8)
            upper = numpy.array(upper, dtype = numpy.uint8)
            
            
            color = cv2.inRange(hsv, lower, upper)
##            for i in range(height):
##                for j in range (width):
##                    if (color[i,j] == 255):
##                        blue+=1
        blue = cv2.countNonZero(color)
        if (blue >= 3000):
            print("I see Blue (" + str(blue) + ")")
            #color = cv2.bitwise_and(self.color, self.color, mask)
        cv2.imshow("color mask", color)
            #cv2.imshow("color", numpy.hstack([self.img, output]))
##            cv2.waitKey(0)
        

        #cv2.imshow("blue                    orange", numpy.hstack([maskBlue, maskOrange]))
        #print("exiting color detection thread")
#        threading.Lock().release()
        
        
class LineFinder (threading.Thread):
    def __init__(self, line):
        threading.Thread.__init__(self)
        self.line = line 
        
    def run(self):
#        threading.Lock().acquire()
        #print("running line detection thread")
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
        
        #print("exiting line detection thread")
###        threading.Lock().release()


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
    #cam = WebcamVideoStream(src=0).start();
    camera = PiCamera()
    camera.resolution = (320, 240)
    camera.framerate = 20
    rawCapture = PiRGBArray(camera)
    time.sleep(2)
    #stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
    

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
        
        #threads.append(lineThread)
        #threads.append(colorThread)

        lineThread.join()
        colorThread.join();
        
#        img = lineThread.img
        cv2.imshow("line                    color", numpy.hstack([line, color]))#        cv2.imshow("color", line, color)
        #cv2.imshow('linedetect', line)
        rawCapture.truncate(0)
        if 0xFF & cv2.waitKey(5) == 27:
            break
    cv2.destroyAllWindows()



        
    
 