import cv2
import numpy as np
import colorsys
from collections import deque
import itertools

def draw_tracking_reticle(frame,window,LaserTracker):
    #Function draws what the computer is tracking
    cv2.circle(frame, LaserTracker.center, 10, (0, 0, 255), 5)
    cv2.imshow(window, frame)

#Inspired by https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
def draw_contrails(frame,window,pts,color,tail_length=255,dbg=0):
    height = frame.shape[0]
    width = frame.shape[1]

    #check if the buffer is smaller than the number of points:
    #I.e. the very beginning
    if tail_length > len(pts):
        tail_length = len(pts)

    #if color = (0,0,0) we attempt a rainbow
    color_flag = 0

    if tail_length> 0:
        frame = np.zeros((height, width), dtype=np.uint8)
    #Iterate through the list of tracked points:
    for i in range(1, tail_length):
		# if either of the tracked points are None, ignore
        if pts[i - 1] is None or pts[i] is None:
            continue
		# otherwise, compute the thickness of the line and
		# draw the connecting lines
        thickness = int(np.sqrt(tail_length/ float(i + 1)) * 1.5)

        if color_flag: #display colors!
            #hue_modifier = int((LaserTracker.disDeque[i]**4)*2)
            # hue_modifier = LaserTracker.upperRange[0]
            color = hsv2rgb((i)/360,1,1)
            cv2.line(frame, pts[i - 1], pts[i], color, thickness,lineType=cv2.LINE_AA)
        else: #solid color
            cv2.line(frame, pts[i - 1], pts[i], color, thickness)
    cv2.imshow(window, frame)


def draw_rotating_triangles(frame,window,pts,polygon_list, color = (0,255,0),
tail_length=255, dbg=0):
    '''
    Points are the center points of the triangle to be drawn
    Count is the running iteration count of the program -1 means that no
    staicking will occur
    tail_length is the length of the desired tail
    tail_stack is the amount of frames to stack up giving the blur effect
    '''
    height = frame.shape[0]
    width = frame.shape[1]

    #check if the buffer is smaller than the number of points:
    if tail_length > len(pts):
        #set the tail length to the number of points we have:
        tail_length = len(pts)

    #if color = (0,0,0) we attempt a rainbow
    color_flag = 1

    #we add one for the one that will be erased
    for i in range(1, tail_length):
        if pts[i] is None:
            continue
        #compute distance between this point and the last point for interp:

        tri_pts = tri_from_center(pts[i],height=20,rotation=i*2,scale=1)
        if color_flag: #display colors!
            #hue_modifier = int((LaserTracker.disDeque[i]**4)*2)
            # hue_modifier = LaserTracker.upperRange[0]
            color = hsv2rgb((i)/360,1,1)
            cv2.polylines(frame,[tri_pts],True,color,3,lineType=cv2.LINE_AA)
            #add triangle points to the returned list
            polygon_list.appendleft(tri_pts)
        else:
            cv2.polylines(frame,[tri_pts],True,color,3,lineType=cv2.LINE_AA)
            polygon_list.appendleft(tri_pts)
        #This is where we color the tails or erase the tail:
        #If tail_length < 0 we dont do anything (-1 flag)
        if tail_length > 0 and i > int(tail_length/2):
            cv2.polylines(frame,[tri_pts],True,(0,0,0),1,lineType=cv2.LINE_AA)
    # cv2.waitKey()

    cv2.imshow(window, frame)

def draw_rotating_triangles_interp(frame,window,pts,polygon_list, color = 0,
tail_length=255, dbg=0):
    '''
    Same function as draw_rotating_triangles but it has a linear interpolation
    function built in to bridge big gaps where the laser is moving quickly
    It is an attempt at smoothing drawing
    '''
    height = frame.shape[0]
    width = frame.shape[1]

    #check if the buffer is smaller than the number of points:
    if tail_length > len(pts):
        tail_length = len(pts)
    #if the user specified a color
    if color:
        color_flag = 0
    else:
        color_flag = 1

    interp_density = .01 # 1 would be a triangle every pixel
    interp_distance = 120 #distance between points to trigger interpolated values
    i = 0
    while i < tail_length:
        if pts[i] is None:
            continue
        #compute distance between this point and the last point for interp:
        interpolated_pts = distance_interp(pts[i],pts[i-1],
                            interp_distance,interp_density)

        if interpolated_pts:
        #interpolated_pts returns a list of points only if there is a "gap"
        #here we insert points into the main points list
            tail_length += len(interpolated_pts) #extend the loop
            [pts.insert(i+1,pt) for pt in reversed(interpolated_pts)] #add pts

        tri_pts = tri_from_center(pts[i],height=20,rotation=i*2,scale=1)
        if color_flag: #display colors!
            color = hsv2rgb((i)/360,1,1)
            cv2.polylines(frame,[tri_pts],True,color,3,lineType=cv2.LINE_AA)
            #add triangle points to the returned list
            polygon_list.appendleft(tri_pts)
        else: #no rainbow, use the specified color
            cv2.polylines(frame,[tri_pts],True,color,3,lineType=cv2.LINE_AA)
            polygon_list.appendleft(tri_pts)
        #This is where we color the tails or erase the tail:
        #If tail_length < 0 we dont do anything (-1 flag)
        if tail_length > 0 and i > int(tail_length/2):
            #paints over the drawn triangles in the back half the lists
            cv2.polylines(frame,[tri_pts],True,(0,0,0),1,lineType=cv2.LINE_AA)
        i+=1
    cv2.imshow(window, frame)

def distance_interp(a,b,threshold,density):
    #calculates the distance between points and returns a list of pts in between
    #a,b are points. Threshold is the trigger distance, density is density of
    #interpolated points
    dis = np.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)
    interpolated_pts_list = None
    if dis > threshold:
        xp = [a[0],b[0]]
        fp = [a[1],b[1]]
        x = np.linspace(a[0], b[0], dis*density)
        x = x[1:-1]#remove first and last as they are duplicates
        yinterp = np.interp(x, xp, fp)
        # interpolated_pts_list = list(map(list,zip(x,yinterp)))
        interpolated_pts_list = list(zip(x,yinterp))
    return interpolated_pts_list




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

def clear_frame(frame):
    cv2.rectangle(frame,(0,0), (frame.shape[1],frame.shape[0]), 0,-1)
