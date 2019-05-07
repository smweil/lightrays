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

#Inspired by https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
def draw_contrails(frame,pts,color,tail_length=255,dbg=0):
    height = frame.shape[0]
    width = frame.shape[1]

    #check if the buffer is smaller than the number of points:
    #I.e. the very beginning
    if tail_length > len(pts):
        tail_length = len(pts)

    #if color = (0,0,0) we attempt a rainbow
    color_flag = 0

    #Iterate through the list of tracked points:
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
            cv2.line(frame, pts[i - 1], pts[i], color, thickness,lineType=cv2.LINE_AA)
        else: #solid color
            cv2.line(frame, pts[i - 1], pts[i], color, thickness)
    return frame


def draw_rotating_triangles(frame,pts,color,tail_length=255,dbg=0):
    height = frame.shape[0]
    width = frame.shape[1]
    #blackout the canvas:

    tail_length = len(pts)
    #check if the buffer is smaller than the number of points:
    if tail_length > len(pts):
        #set the tail length to the number of points we have:
        tail_length = len(pts)

    #if color = (0,0,0) we attempt a rainbow
    color_flag = 1

    #if we do not want infinite tails:
    if tail_length> 0:
        frame = np.zeros((height, width), dtype=np.uint8)

    for i in range(1, tail_length):
		# if either of the tracked points are None, ignore
        if pts[i - 1] is None or pts[i] is None or pts[i] ==0:
            continue
        tri_pts = tri_from_center(pts[i],height=20,rotation=i*2,scale=1)
        if not color_flag: #display colors!
            #hue_modifier = int((LaserTracker.disDeque[i]**4)*2)
            # hue_modifier = LaserTracker.upperRange[0]
            color = hsv2rgb((i)/360,1,1)
            cv2.polylines(frame,[tri_pts],True,color,lineType=cv2.LINE_AA)
        else:
            print("here")
            cv2.polylines(frame,[tri_pts],True,color,lineType=cv2.LINE_AA)

    return frame


def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))


def tri_from_center(center_pt,height,rotation=0,scale =1):
    #Generates an equalateral triangle from the center point
    #Rotation is counterclockwise in degrees
    x = center_pt[0]
    y = center_pt[1]
    center_pt = (x,y)
    dx = (height)/np.sqrt(3) #x_distance for bottom two points
    dy = height/3 #the y distance for bottom two points
    #(top)(bot left)(bot right)
    pts = np.array([[x,y+height],[x-dx,y-dy],[x+dx,y- dy]],np.int32)
    if rotation >0:
        # rotation = -rotation
        ones = np.ones(shape=(len(pts), 1))
        pts_ones = np.hstack([pts, ones])

        rot_mat = cv2.getRotationMatrix2D(center_pt, rotation, scale)
        rot_pts = rot_mat.dot(pts_ones.T).T
        pts = np.array(rot_pts,np.int32)
    return pts
