import numpy   as np
import cv2
import imutils
import CamTools
import math
from collections import deque

#This class will handle the detection and tracking of the laser
class LaserTracker:
    def __init__(self,lowerRange,upperRange,deque_buffer): #upper and lower HSV values
        self.upperRange = upperRange
        self.lowerRange = lowerRange
        self.trackerStatus = False #initally there is no tracker running
        self.onScreen = False #Tell us if the laser is currently detected
        self.ptsDeque = deque() #empty list for tracked points
        self.disDeque = deque() #empty list for tracked velocity
        self.dirDeque = deque() #empty list for tracked direciton
        self.lostTrackCounter = -1; #initialize the number of times we've lost it
    def detect(self, frame): #initial detection of the laser contour
        #Should be resized from the source:
        # frame = imutils.resize(frame, width=500) #resize the frame
        blurred = cv2.GaussianBlur(frame, (11, 11), 0) #blur the frame
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) #convert to HSV

        #create the mask:
        mask = cv2.inRange(hsv, self.lowerRange, self.upperRange) #localization
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)


        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None
        radius = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((self.x, self.y), radius) = cv2.minEnclosingCircle(c)
            center = (int(self.x), int(self.y)) #convert to pixels

            #This may be unecessary since it is a dot:
            # M = cv2.moments(c)
            # center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            self.onScreen = True
            self.ptsDeque.appendleft(center) #add points to list

            #need to keep them the same length (this must change later)
            self.disDeque.appendleft(-1) #add points to list
            self.dirDeque.appendleft(-1) #add points to list

        else: #nothing detected
            self.onScren = False

        self.center = center
        self.radius = radius

    def initialize_tracker(self,center,radius,frame):
        tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
        tracker_type = tracker_types[2]

        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()
        if tracker_type == 'MOSSE':
            tracker = cv2.TrackerMOSSE_create()
        if tracker_type == "CSRT":
            tracker = cv2.TrackerCSRT_create()

        #Compute inital bounding box with center rand radius:
        bbox = (center[0]-radius, center[1]-radius, 2.5*radius, 2.5*radius) #(xmin,ymin,boxwidth,boxheight)

        # Initialize tracker with first frame and bounding box
        self.trackerStatus = tracker.init(frame, bbox)
        self.tracker = tracker

    def update_tracker(self,frame):
            # Update tracker
            self.trackerStatus, bbox = self.tracker.update(frame)
            if self.trackerStatus:
                # Tracking success
                self.onScreen = True
                self.center = (int(bbox[0]+bbox[2]/2),int(bbox[1]+bbox[3]/2)) #x coord is xmin+width/2
                self.radius = bbox[2]/2
                self.ptsDeque.appendleft(self.center) #add points to list
                self.calc_direction_speed(self.ptsDeque)

            else :
                self.onScreen = False

    #This is the "main" function. It will detect and initiate the tracker
    #and re-detect if the tracker becomes inactive
    def run_full_detection(self,frame):
        if self.trackerStatus: #if the tracker is working
            self.update_tracker(frame)
        else:
            self.detect(frame) #run the detector if the tracker isn't working
            self.lostTrackCounter = self.lostTrackCounter+1 #increment the counter

            if self.center: #if we have detected the object
                self.initialize_tracker(self.center,self.radius,frame)  #initialize the tracker

    #Takes in a deque and calculates speed and direction of the pointer
    def calc_direction_speed(self, pts):
        # if pts[i - 10] is None or pts[i] is None: #do we have 10 pts
        #     continue
        dX = pts[1][0] - pts[0][0]
        dY = pts[1][1] - pts[0][1]
        self.dirDeque.appendleft(math.atan2(dY,dX))
        self.disDeque.appendleft(math.sqrt((dY*dY)+(dX*dX)))
