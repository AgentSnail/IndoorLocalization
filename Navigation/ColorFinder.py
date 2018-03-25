import threading
import time
import numpy
import cv2

#color boundaries
boundaries = [
    ([86, 31, 4], [50, 56, 200]), #blue range
    ([255, 140, 0], [255, 165, 0]) #orange range
]

class ColorFinder(threading.Thread):
    def __init__(self, img):
        threading.Thread.__init__(self)
        self.img = img

    def run(self):
        for(lower, upper) in boundaries:
        #create arrays from boundaries
        lower = numpy.array(lower, dtype = "uint8")
        upper = numpy.array(upper, dtype = "uint8")
        
        mask = cv2.inRange(img, lower, upper)
        img = cv2.bitwise_and(img, img, mask = mask)