import numpy as np
import cv2
import imutils
import CamTools
import math
from collections import deque

# This class will handle the detection and tracking of the laser
class LaserTracker:
    def __init__(self, lowerRange, upperRange, t_matrix, reset_trigger=100):
        """
        This class holds detection parameters, and collects detected points

        Keyword arguments:
        lowerRange -- the lower HSV detection values (H,S,V)
        upperRange -- the upper HSV detection values (H,S,V)

        t_matrix -- this is the warped transformation matrix

        reset_trigger is the amount of frames the laser has not been detected
        before it resets the list of detected points (trail)

        if reset_counter=0 the trails never disappear.
        """
        self.t_matrix = t_matrix  # the difference in size between cam and canvas
        self.upperRange = upperRange
        self.lowerRange = lowerRange
        self.trackerStatus = False  # initally there is no tracker running
        self.onScreen = False  # Tell us if the laser is currently detected
        self.ptsDeque = deque()  # empty list for tracked points
        # self.accDeque = deque()  # Acelleration list

        self.velDeque = deque()  # velocity list CHANGE maybe doesn't need to be a deque
        self.velDeque.appendleft(1)

        self.brush_width = 1  # initialize brush width
        # initialize first value
        self.dirDeque = deque()  # direction 1 N 2 E 3 S 4 W
        self.dirDeque.appendleft(0)

        self.polygonDeque = deque()  # list of drawn shapes
        self.lostTrackCounter = -1
        # initialize the number of times we've lost it
        self.reset_trigger = reset_trigger

    def detect(self, frame):  # initial detection of the laser contour
        # Should be resized from the source:
        # frame = imutils.resize(frame, width=500) #resize the frame
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)  # blur the frame
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)  # convert to HSV

        # create the mask:
        mask = cv2.inRange(hsv, self.lowerRange, self.upperRange)  # localization
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Find the contours:
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        center = None
        radius = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and centroid
            c = max(cnts, key=cv2.contourArea)
            ((self.x, self.y), radius) = cv2.minEnclosingCircle(c)
            center = (int(self.x), int(self.y))  # convert to pixels

            # We detected a contour so the laser is onscreen
            self.onScreen = True

            # https://www.learnopencv.com/homography-examples-using-opencv-python-c/
            original = (center[0], center[1], 1)
            transformed_points = self.t_matrix.dot((original))
            scaled_center = (int(transformed_points[0]), int(transformed_points[1]))
            self.ptsDeque.appendleft(scaled_center)  # add points to display

        # Calculate metrics:
        if len(self.ptsDeque) > 1:  # WORKING HERE
            distance = math.dist(self.ptsDeque[0], self.ptsDeque[1])
            deltaX = self.ptsDeque[0][0] - self.ptsDeque[1][0]
            deltaY = self.ptsDeque[0][1] - self.ptsDeque[1][1]

            direction = round(180 - math.atan2(deltaX, deltaY) / math.pi * 180)
            self.dirDeque.appendleft(direction)
            # treat 1/16 of the screen as max speed
            height = frame.shape[0]
            width = frame.shape[1]

            diagonal = math.sqrt(
                height ** 2 + width ** 2
            )  # change dont calculate this every loop just pass it into the function

            brush_max_speed = (
                1 / 32  # when the brush travels of the screen it's max speed
            )
            speed = distance / (diagonal * brush_max_speed)
            self.velDeque.appendleft(speed)

            self.speed = speed

            # remove from this file move to draw tools:
            self.brush_width = 10 * (1 - min(speed, 1))
            print("Direction: ", self.dirDeque[0])
            # print("Width: ", self.brush_width)

        else:  # nothing detected
            self.onScren = False
        self.center = center
        self.radius = radius

    def initialize_tracker(self, center, radius, frame):
        tracker_type = "KCF"

        if tracker_type == "KCF":
            tracker = cv2.TrackerKCF_create()
        if tracker_type == "TLD":
            tracker = cv2.TrackerTLD_create()
        if tracker_type == "MOSSE":
            tracker = cv2.TrackerMOSSE_create()
        # Compute inital bounding box with center rand radius:
        bbox = (
            int(center[0] - radius),
            int(center[1] - radius),
            int(2.5 * radius),
            int(2.5 * radius),
        )

        # Initialize tracker with first frame and bounding box
        self.trackerStatus = tracker.init(frame, bbox)
        self.tracker = tracker

    def update_tracker(self, frame):
        self.trackerStatus, bbox = self.tracker.update(frame)
        if self.trackerStatus:
            self.onScreen = True
            # x coord is xmin+width/2
            self.center = (int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3] / 2))
            self.radius = bbox[2] / 2
            # add points to list
            original = (center[0], center[1], 1)
            transformed_points = self.t_matrix.dot((original))
            scaled_center = (int(transformed_points[0]), int(transformed_points[1]))
            self.ptsDeque.appendleft(scaled_center)  # add points to display
        else:
            # We have lost the tracker:
            self.onScreen = False

    def run_full_detection_tracker(self, frame):
        """
        This is the "main" function: it will detect and initiate the tracker
        and re-detect if the tracker becomes inactive
        """
        if self.trackerStatus:  # if the tracker is working update the tracker
            self.update_tracker(frame)
        else:  # if the tracker failed, redetect the contour

            self.detect(frame)
            self.lostTrackCounter += 1
            if self.center:  # if we have detected the object
                self.initialize_tracker(self.center, self.radius, frame)
                self.lostTrackCounter = 0  # reset the counter

        # If we have lost the tracker for longer than the reset_trigger
        # I.e. the laser is off, reset the trails
        if self.reset_trigger != 0 and self.lostTrackCounter > self.reset_trigger:
            self.reset()

    def run_full_detection(self, frame):
        """
        This detects the object and doesn't utilize any trackers
        """
        self.detect(frame)
        if self.center:  # if we have detected the object
            self.initialize_tracker(self.center, self.radius, frame)
            self.lostTrackCounter = 0  # reset the counter
        else:
            self.lostTrackCounter += 1

        # If we have lost the tracker for longer than the reset_trigger
        # I.e. the laser is off, reset the trails
        if self.reset_trigger != 0 and self.lostTrackCounter > self.reset_trigger:
            self.reset()

    def reset(self):
        self.ptsDeque = deque()  # empty list for tracked points
        self.lostTrackCounter = 0
