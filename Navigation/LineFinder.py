import threading
import time
import numpy
import cv2
import math

class LineFinder (threading.Thread):
    def __init__(self, img):
        threading.Thread.__init__(self)
        self.img = img
        
    def run(img):
        print("running line detection thread")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#        gray = cv2.equalizeHist(gray)
#        gray = cv2.GaussianBlur(gray, (9,9), 0)
        
        edged = cv2.Canny(gray, 50, 150, apertureSize = 3)
        lines = cv2.HoughLines(edged, 1, numpy.pi/180.0, 100, numpy.array([]), 0, 0)
        
#        for x1, y1, x2, y2 in lineThread[0]:
#            cv2.line(img, (x1,y1),(x2,y2),(0,255,0),2)

        a,b,c = lines.shape
        for i in range(a):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0, y0 = a*rho, b*rho
            pt1 = (int(x0+1000*(-b)), int(y0+1000*(a)))
            pt2 = (int(x0-1000*(-b)), int(y0-1000*(a)))
            cv2.line(img, pt1, pt2, (0,0,255), 2, cv2.LINE_AA)

        
        print("exiting line detection thread")
        