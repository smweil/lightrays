import numpy as np
import cv2
import imutils
import CamTools
import TrackTools
import DrawTools

from imutils.video import FPS

# Windows names
camera_window = "Computer Vision:"
canvas_window = "Canvas:"

canvas_width = 500
canvas_size = canvas_width, canvas_width, 3
canvas_image = np.zeros(canvas_size, dtype=np.uint8)

#redLaser:
red_lower = (170,0,208)
red_upper = (255,255,255)

blue_lower = (105, 133, 88)
blue_upper = (142, 255, 255)
green_lower= (0, 180, 26)
green_upper = (13, 255, 255)

red_lowerVideo = (0,110,84)
red_upperVideo = (11,144,255)


blue_laser = TrackTools.LaserTracker(blue_lower,blue_upper,50)
green_laser = TrackTools.LaserTracker(green_lower,green_upper,255)
red_laser = TrackTools.LaserTracker(red_lowerVideo,red_upperVideo,255)
# red_laser = TrackTools.LaserTracker(red_lower,red_upper,100)


# video_stream = CamTools.WebcamVideoStream(width=500, height = 500).start()
video_stream = cv2.VideoCapture('./bin/laserwall.mp4')

fps = FPS().start()


#Main loop:
while(1):
    #Reload the new frames
    ret, frame = video_stream.read()

    #Detect keyboard inputs:
    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    elif key == ord("c"):
        canvas_image = np.zeros(canvas_size, dtype=np.uint8)

    #Detect where the laser is:
    if ret == True:
        red_laser.run_full_detection(frame)
        # green_laser.run_full_detection(frame)
    else:
        break

    if red_laser.onScreen:
        # canvas_image =DrawTools.draw_contrails(canvas_image, red_laser.ptsDeque,
        # (0,255,0),100,0)


        # canvas_image = np.zeros(canvas_size, dtype=np.uint8)
        DrawTools.draw_rotating_triangles(canvas_image, canvas_window,red_laser.ptsDeque,
        red_laser.polygonDeque,(0,255,0),tail_length=100,dbg = 0)

        # canvas_image = DrawTools.draw_trail_simple(canvas_image, red_laser,
        # (0,255,0))

        # frame = DrawTools.draw_tracking_reticle(frame,red_laser)

    # if green_laser.onScreen:
    #     frame = DrawTools.draw_tracking_reticle(frame,green_laser)
    #     canvas_image = DrawTools.draw_canvas_circle(canvas_image, green_laser, (255, 0, 0))

    fps.update()
fps.stop()


print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
print("[INFO] Lost Track: {:.2f}".format(red_laser.lostTrackCounter))

#Housekeeping
if ret == 1:
    video_stream.stop()

cv2.waitKey()
cv2.destroyAllWindows()
