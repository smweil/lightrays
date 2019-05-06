import cv2
import numpy as np
import colorsys

def draw_tracking_reticle(frame,LaserTracker):
    #Function draws what the computer is tracking
    cv2.circle(frame, LaserTracker.center, 10, (0, 0, 255), 5)
    return frame

def draw_canvas_circle(frame,LaserTracker,color):
    cv2.circle(frame, LaserTracker.center, 5, color, -1)
    return frame


def draw_trail_simple(frame, LaserTracker, color):
    if len(LaserTracker.ptsDeque)>2:
        cv2.line(frame, LaserTracker.ptsDeque[0], LaserTracker.ptsDeque[1],
                 color, 5)
    return frame

#from:https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
def draw_contrails(frame,LaserTracker,color,tail_length=255,dbg=0):
    pts = LaserTracker.ptsDeque
    height = frame.shape[0]
    width = frame.shape[1]

    #blackout the canvas:
    # frame = np.zeros((height, width), dtype=np.uint8)

    #check if the buffer is smaller than the number of points:
    if tail_length > len(pts):
        tail_length = len(pts)

    #if color = (0,0,0) we attempt a rainbow
    color_flag = 0

    for i in range(1, tail_length):
		# if either of the tracked points are None, ignore
        if pts[i - 1] is None or pts[i] is None:
            continue
		# otherwise, compute the thickness of the line and
		# draw the connecting lines
        thickness = int(np.sqrt(tail_length/ float(i + 1)) * 1.5)

        if not color_flag: #display colors!
            #hue_modifier = int((LaserTracker.disDeque[i]**4)*2)

            # hue_modifier = LaserTracker.upperRange[0]
            color = hsv2rgb((i)/360,1,1)
            cv2.line(frame, pts[i - 1], pts[i], color, thickness)
        else:
            cv2.line(frame, pts[i - 1], pts[i], color, thickness)

        if dbg and i ==1:
            if LaserTracker.dirDeque:
                dir = (LaserTracker.dirDeque[i]*180)/3.1415
                cv2.putText(frame,
                "Direction: {:06.2f}, Distance: {:06.2f}".format(dir, LaserTracker.disDeque[i]),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.35, (0, 0, 255), 1)
    return frame

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))
