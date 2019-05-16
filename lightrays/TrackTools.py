import numpy   as np
import cv2
import imutils
import CamTools
import math
from collections import deque

#This class will handle the detection and tracking of the laser
class LaserTracker:
    def __init__(self,lowerRange,upperRange,scale_factors,reset_trigger = 100):
        '''
        This class holds detection parameters, and collects detected points

        Keyword arguments:
        lowerRange -- the lower HSV detection values (H,S,V)
        upperRange -- the upper HSV detection values (H,S,V)

        scale_factors -- these factors are the difference between the detection
        screen coordinates and the display screen (canvas) coordinates.

        reset_trigger is the amount of frames the laser has not been detected
        before it resets the list of detected points (trail)

        if reset_counter=0 the trails never disappear.
        '''
        self.scale_factors = scale_factors #the difference in size between cam and canvas
        self.upperRange = upperRange
        self.lowerRange = lowerRange
        self.trackerStatus = False #initally there is no tracker running
        self.onScreen = False #Tell us if the laser is currently detected
        self.ptsDeque = deque() #empty list for tracked points
        self.polygonDeque = deque() #list of drawn shapes
        self.lostTrackCounter = -1; #initialize the number of times we've lost it
        self.reset_trigger = reset_trigger

    def detect(self, frame): #initial detection of the laser contour
        #Should be resized from the source:
        # frame = imutils.resize(frame, width=500) #resize the frame
        blurred = cv2.GaussianBlur(frame, (11, 11), 0) #blur the frame
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) #convert to HSV

        #create the mask:
        mask = cv2.inRange(hsv, self.lowerRange, self.upperRange) #localization
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        #Find the contours:
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        center = None
        radius = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and centroid
            c = max(cnts, key=cv2.contourArea)
            ((self.x, self.y), radius) = cv2.minEnclosingCircle(c)
            center = (int(self.x), int(self.y)) #convert to pixels

            #We detected a contour so the laser is onscreen
            self.onScreen = True

            #scale the points based on the difference between the cam and the canvas:
            scaled_center = (int(center[0]*self.scale_factors[0]),
                            int(center[1]*self.scale_factors[1]))
            self.ptsDeque.appendleft(scaled_center) #add points to display

        else: #nothing detected
            self.onScren = False
        self.center = center
        self.radius = radius

    def initialize_tracker(self,center,radius,frame):
        tracker_type = 'KCF'
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'MOSSE':
            tracker = cv2.TrackerMOSSE_create()

        #Compute inital bounding box with center rand radius:
        bbox = (center[0]-radius, center[1]-radius, 2.5*radius, 2.5*radius)

        # Initialize tracker with first frame and bounding box
        self.trackerStatus = tracker.init(frame, bbox)
        self.tracker = tracker

    def update_tracker(self,frame):

            self.trackerStatus, bbox = self.tracker.update(frame)
            if self.trackerStatus:
                self.onScreen = True
                #x coord is xmin+width/2
                self.center = (int(bbox[0]+bbox[2]/2),int(bbox[1]+bbox[3]/2))
                self.radius = bbox[2]/2
                #add points to list
                scaled_center = (int(self.center[0]*self.scale_factors[0]),
                                int(self.center[1]*self.scale_factors[1]))
                self.ptsDeque.appendleft(scaled_center)
            else :
                #We have lost the tracker:
                self.onScreen = False


    def run_full_detection(self,frame):
        '''
        This is the "main" function: it will detect and initiate the tracker
        and re-detect if the tracker becomes inactive
        '''
        if self.trackerStatus:#if the tracker is working update the tracker
            self.update_tracker(frame)
        else:#if the tracker failed, redetect the contour
            self.detect(frame)
            self.lostTrackCounter +=1
            if self.center: #if we have detected the object
                self.initialize_tracker(self.center,self.radius,frame)
                self.lostTrackCounter = 0 #reset the counter

        #If we have lost the tracker for longer than the reset_trigger
        #I.e. the laser is off, reset the trails
        if self.reset_trigger !=0 and self.lostTrackCounter > self.reset_trigger:
            self.reset()

            frame = np.zeros(frame.shape, dtype=np.uint8)

    def reset(self):
        self.ptsDeque = deque() #empty list for tracked points
        self.lostTrackCounter= 0
