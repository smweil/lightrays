import cv2
import numpy as np

def draw_tracking_reticle(frame,LaserTracker):
    #Function draws what the computer is tracking
    cv2.circle(frame, LaserTracker.center, 10, (0, 0, 255), 5)
    return frame

def draw_canvas_circle(frame,LaserTracker,color):
    cv2.circle(frame, LaserTracker.center, 5, color, -1)
    return frame

#from:https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
def draw_contrails(frame,LaserTracker,color,buffer=255,dbg=0):
    pts = LaserTracker.ptsDeque
    for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
        if pts[i - 1] is None or pts[i] is None:
            continue
		# otherwise, compute the thickness of the line and
		# draw the connecting lines
        thickness = int(np.sqrt(buffer/ float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], color, thickness)
        if dbg and i ==1 :
            if LaserTracker.dirDeque:
                dir = (LaserTracker.dirDeque[i]*180)/3.1415
                cv2.putText(frame,
                "Direction: {:06.2f}, Distance: {:06.2f}".format(dir, LaserTracker.disDeque[i]),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.35, (0, 0, 255), 1)

    return frame