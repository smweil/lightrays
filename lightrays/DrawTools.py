import cv2
import random
import numpy as np
import colorsys
from collections import deque
import itertools
import DrawGUI

# Dev note:
# make each on it's own class with it's own menu? Probably no...
# Need to make the drawings a seperate image so we can blue them when we overlay them onto the background


def draw_tracking_reticle(frame, window, LaserTracker):
    # Function draws a circle where it detects the laser on the cam screen
    # Largely used to make sure we are detecting a laser
    cv2.circle(frame, LaserTracker.center, 10, (0, 0, 255), 5)
    cv2.imshow(window, frame)


def draw_simple_circle(frame, window, pts, color=(0, 0, 255)):
    # Simple example drawing method that draws a circle on the canvas
    if len(pts) > 0:
        x = int(pts[0][0])
        y = int(pts[0][1])
        point = (x, y)
        cv2.circle(frame, point, 10, color, 5)
        cv2.imshow(window, frame)


def pen_mode(frame, window, pts, new_line_count, color=(0, 255, 0), thickness=4):
    # COLOR IN BGR
    # Allows the user to cycle through colors and brush width with keyboard
    # new_line_count is the amount of time before we start a newline
    height = frame.shape[0]
    width = frame.shape[1]

    thickness, hue = DrawGUI.get_trackbar_values(["Size", "Hue"])
    thickness = 1 if thickness < 1 else thickness

    color = hsv2rgb(hue, 360, 360)
    if len(pts) > 1:
        cv2.line(frame, pts[0], pts[1], color, thickness, lineType=cv2.LINE_AA)
        # print("pt0:", pts[0],"pt1:",pts[1])
    cv2.imshow(window, frame)


def draw_brush(frame, window, pts, color=(0, 255, 0), speed=4):
    # COLOR IN BGR
    # Allows the user to cycle through colors and brush width with keyboard
    height = frame.shape[0]
    width = frame.shape[1]
    overlay = frame.copy()  # overlay for alpha blending
    # hue = DrawGUI.get_trackbar_values(["Hue"])
    # alpha = thickness  # scale on thickness7
    alpha = 1
    thickness = round(speed)
    if thickness < 4:
        thickness = 4

    if thickness > 50:
        thickness = 50
    # print("thickness: ", thickness)
    thickness_noise = thickness + random.randint(0, 2)
    # color = hsv2rgb(hue, 360, 360)
    if len(pts) > 1:
        cv2.line(overlay, pts[0], pts[1], color, thickness, lineType=cv2.LINE_AA)

        # cv2.line(
        #     overlay,
        #     pts[0],
        #     pts[1],
        #     color,
        #     thickness + thickness_noise,
        #     lineType=cv2.LINE_AA,
        # )

    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    cv2.imshow(window, frame)
    return frame


def draw_3d_snake(frame, window, pts, polygon_list, thickness=4, rotation_factor=0.3):
    """
    This one rotates the line segments between drawn points
    It may be inaccurate, but it looks really neat.
    """
    height = frame.shape[0]
    width = frame.shape[1]
    tail_length = len(pts)  # iterate over the entire list of pts
    # rotation_factor = DrawGUI.get_trackbar_values(["Rotation"])/100
    rotation_factor = 0.1

    # Iterate through the list of tracked points:
    for i in range(1, tail_length):
        # if either of the tracked points are None, ignore
        if pts[i - 1] is None or pts[i] is None:
            continue

        # segment = np.array([pts[i-1],pts[i]],np.int32)
        #  #store the line segment we wish to rotate
        # polygon_list.appendleft(segment)
        rot_pts = rotate_line_segment(pts[i - 1], pts[i], (i * rotation_factor))
        if thickness < 0:
            thickness = int(np.sqrt(tail_length / float(i + 1)) * 1.5)
        color = hsv2rgb((i), 360, 360)

        pt_i1 = (rot_pts[1][0], rot_pts[1][1])
        pt_i = (rot_pts[0][0], rot_pts[0][1])

        cv2.line(frame, pt_i1, pt_i, color, thickness, lineType=cv2.LINE_AA)

        # Rewrite the backend of the tail:
        # if tail_length > 0 and i > int(tail_length/2):
        #     cv2.line(frame,pt_i1, pt_i,(0,0,0),thickness,lineType=cv2.LINE_AA)

    cv2.imshow(window, frame)


def draw_rainbow_snake(frame, window, pts, thickness=4):
    """
    Draws a rainbow trail on the canvas

    Key arguments:
    thickness -- if -1, it will grow dynamically otherwise it stays at the
    specified thickness
    """
    height = frame.shape[0]
    width = frame.shape[1]
    tail_length = len(pts)  # iterate over the entire list of pts

    # Iterate through the list of tracked points:
    for i in range(1, tail_length):
        # if either of the tracked points are None, ignore
        if pts[i - 1] is None or pts[i] is None:
            continue

        if thickness < 0:
            thickness = int(np.sqrt(tail_length / float(i + 1)) * 1.5)
        color = hsv2rgb((i), 360, 360)
        cv2.line(frame, pts[i - 1], pts[i], color, thickness, lineType=cv2.LINE_AA)

    cv2.imshow(window, frame)


def draw_comet(frame, window, pts, color=0, tail_length=255):
    """
    #Inspired by:
    https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
    Draws a line with a color changing tail that decreases in thickness

    Key arguments
    color -- if color is not specified it will be a rainbow
    """
    height = frame.shape[0]
    width = frame.shape[1]

    # check if the buffer is smaller than the number of points:
    # I.e. the very beginning
    if tail_length > len(pts):
        tail_length = len(pts)

    color_flag = 0 if color else 1

    # Iterate through the list of tracked points:
    for i in range(1, tail_length):
        # if either of the tracked points are None, ignore
        if pts[i - 1] is None or pts[i] is None:
            continue

        # Compute the thickness of the line and draw the connecting lines
        thickness = int(np.sqrt(tail_length / float(i + 1)) * 1.5)

        if color_flag:  # display colors!
            # hue_modifier = LaserTracker.upperRange[0]
            color = hsv2rgb((i), 360, 360)
            cv2.line(frame, pts[i - 1], pts[i], color, thickness, lineType=cv2.LINE_AA)
        else:  # solid color
            cv2.line(frame, pts[i - 1], pts[i], color, thickness)

    cv2.imshow(window, frame)


def draw_rotating_triangles(
    frame,
    window,
    pts,
    polygon_list,
    color=0,
    tail_length=150,
    rotation_factor=2,
    scale_factor=0.012,
):
    """
    pts -- The center points of the triangle to be drawn
    color -- if not specified, will be a rainbow
    tail_length is the length of the desired tail before we start drawing over it

    Has a linear interpolation function built in to bridge big gaps where the
    laser is moving quickly.

    Key arguments:
    rotation_factor -- how much to shift the triangles in the tail
    scale_factor --how much to scale the triangles in the tail

    Key variables in the method:
    interp_density -- 1 would be a triangle every pixel
    interp_distance -- distance between points to trigger interpolated values
    set to a large number to not interpolate
    """
    interp_density = 0.01  # 1 would be a triangle every pixel
    interp_distance = 120  # distance between points to trigger interpolated values

    # rotation_factor = DrawGUI.get_trackbar_values(["Rotation"])/40
    # scale_factor = DrawGUI.get_trackbar_values(["Scale"])/1000

    height = frame.shape[0]
    width = frame.shape[1]
    # check if the buffer is smaller than the number of points:
    if tail_length > len(pts):
        tail_length = len(pts)

    # if the user specified a color turn off flag
    color_flag = 0 if color else 1

    i = 0
    while i < tail_length:
        if pts[i] is None:
            continue
        # compute distance between this point and the last point for interp:
        interpolated_pts = distance_interp(
            pts[i], pts[i - 1], interp_distance, interp_density
        )

        if interpolated_pts:
            # interpolated_pts returns a list of points only if there is a "gap"
            # Insert points into the main points list:
            tail_length += len(interpolated_pts)  # extend the loop
            [pts.insert(i + 1, pt) for pt in reversed(interpolated_pts)]  # add pts

        tri_pts = tri_from_center(
            pts[i], height=20, rotation=i * rotation_factor, scale=i * scale_factor + 1
        )

        if color_flag:
            color = hsv2rgb((i), 360, 360)  # Colors are cycled as a function of i

        cv2.polylines(frame, [tri_pts], True, color, 3, lineType=cv2.LINE_AA)
        polygon_list.appendleft(tri_pts)  # add triangle points to the returned list

        # This is where we color the tails or erase the tail:
        # If tail_length < 0 we dont do anything (-1 flag)
        if tail_length > 0 and i > int(tail_length / 2):
            # paints over the drawn triangles in the back half the lists
            cv2.polylines(frame, [tri_pts], True, (0, 0, 0), 1, lineType=cv2.LINE_AA)
        i += 1
    cv2.imshow(window, frame)


def distance_interp(a, b, threshold, density):
    # calculates the distance between points and returns a list of pts in between
    # a,b are points. Threshold is the trigger distance, density is density of
    # interpolated points
    dis = np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    interpolated_pts_list = None
    if dis > threshold:
        xp = [a[0], b[0]]
        fp = [a[1], b[1]]
        x = np.linspace(a[0], b[0], int(dis * density))
        x = x[1:-1]  # remove first and last as they are duplicates
        yinterp = np.interp(x, xp, fp)
        yinterp_int = list(map(int, yinterp))
        x_int = list(map(int, x))  # convert to ints not floats
        interpolated_pts_list = list(zip(x_int, yinterp_int))
    return interpolated_pts_list


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h / 360, s / 360, v / 360))


def bgr2hsv(b, g, r):
    return tuple(int(i * 360) for i in colorsys.rgb_to_hsv(r / 255, g / 255, b / 255))


def tri_from_center(center_pt, height, rotation=0, scale=1):
    # Generates an equalateral triangle from the center point
    # Rotation is counterclockwise in degrees
    x = center_pt[0]
    y = center_pt[1]
    center_pt = (x, y)
    dx = (height) / np.sqrt(3)  # x_distance for bottom two points
    dy = height / 3  # the y distance for bottom two points
    # (top)(bot left)(bot right)
    pts = np.array([[x, y + height], [x - dx, y - dy], [x + dx, y - dy]], np.int32)
    if rotation > 0:
        # rotation = -rotation
        ones = np.ones(shape=(len(pts), 1))
        pts_ones = np.hstack([pts, ones])

        rot_mat = cv2.getRotationMatrix2D(center_pt, rotation, scale)
        rot_pts = rot_mat.dot(pts_ones.T).T
        pts = np.array(rot_pts, np.int32)
    return pts


def rotate_line_segment(pt_a, pt_b, rotation, scale=1):
    # rotate points about the center of the segment they create
    # Rotation is counterclockwise in degrees
    pts = np.array([pt_a, pt_b], np.int32)
    center_x = (pt_a[0] - pt_b[0]) / 2
    center_y = (pt_a[1] - pt_b[1]) / 2
    center = (center_x, center_y)
    ones = np.ones(shape=(len(pts), 1))
    pts_ones = np.hstack([pts, ones])

    rot_mat = cv2.getRotationMatrix2D(center, rotation, scale)
    rot_pts = rot_mat.dot(pts_ones.T).T
    pts = np.array(rot_pts, np.int32)
    return pts


def clear_frame(frame):
    cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), 0, -1)
