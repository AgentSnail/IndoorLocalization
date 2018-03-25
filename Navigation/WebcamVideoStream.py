from threading import Thread
import cv2

class WebcamVideoStream:
    def __init__(self, src=0): #initialize video stream and get first frame
        self.stream = cv2.videoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        
        self.stopped = False
        
    def start(self): #start thread to read frames
        Thread(target=self.update, args=()).start()
        return self
    
    def update(self): #keep looping until thread stops
        while True:
            if self.stopped:
                return
            #else, grab frame from stream
            (self.grabbed, self.frame) = self.stream.read() 
    
    def read(self): #return most recent frame
        return self.frame
    
    def stop(self):
        self.stopped = True