from threading import Thread
from picamera import PiCamera
import picamera.array
import cv2

class PiVideoStream:
    def __init__(self, resolution = (640, 480), framerate=20): #initialize video stream and get first frame
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rowCapture = picamera.array.PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        
        self.frame = None
        self.stopped = False
        #self.stream = cv2.videoCapture(src)
        #(self.grabbed, self.frame) = self.stream.read()
        
        #self.stopped = False
        
    def start(self): #start thread to read frames
        Thread(target=self.update, args=()).start()
        return self
    
    def update(self): #keep looping until thread stops
        while True:
            for f in self.stream:
                self.frame = f.array
                self.rawCapture.truncate(0)
                if self.stopped:
                    self.stream.close()
                    self.rapCapture.close()
                    self.camera.close()
                    return
    
    def read(self): #return most recent frame
        return self.frame
    
    def stop(self):
        self.stopped = True
