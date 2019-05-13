import numpy as np
import cv2
import imutils
import CamTools
import TrackTools
import DrawTools
import CanvasTools
import config
from imutils.video import FPS

# Windows names
camera_window = "Computer Vision:"
canvas = CanvasTools.Canvas(screen_resolution=(1280,720))

#This will have to be a autodetect stretch function of some sort:
# canvas_width = 640
# canvas_height = 480
# canvas_size = canvas_width, canvas_height, 3
# canvas.frame = np.zeros(canvas_size, dtype=np.uint8)


# red_lower = (config.laser_settings['red_lower'])
# red_upper = (config.laser_settings['red_upper'])
# video_stream = CamTools.WebcamVideoStream(width=500, height = 500).start()


red_lower = (config.laser_settings['red_lower_video'])
red_upper = (config.laser_settings['red_upper_video'])
video_stream = cv2.VideoCapture('./bin/laserwall.mp4')

red_laser = TrackTools.LaserTracker(red_lower,red_upper,100)


ret, frame = video_stream.read()
setup_flag = 1
while setup_flag:
    #Setup script:
    key = cv2.waitKey(1) & 0xFF
    if key in [ord("a"),ord("d"), ord("w"),ord("s"),ord("q"),ord("e")]:
        canvas.resize_image(key)
    if key in [ord("j"), ord("i"), ord("k"), ord("l"),ord("u"), ord("o")]:
        canvas.resize_window(key)
    elif key == 13: #Enter key
        setup_flag =0





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
        #canvas.clear_image1()
        canvas.frame = np.zeros(canvas_size, dtype=np.uint8)
        cv2.imshow(canvas.window_name, canvas.frame)

    #Detect where the laser is:
    if ret == True:
        red_laser.run_full_detection(frame)
        # green_laser.run_full_detection(frame)
    else:
        break

    if red_laser.onScreen:
        # canvas.frame =DrawTools.draw_contrails(canvas.frame, red_laser.ptsDeque,
        # (0,255,0),100,0)

        # DrawTools.draw_rotating_triangles(canvas.frame, canvas.window_name,red_laser.ptsDeque,
        # red_laser.polygonDeque,(0,255,0),tail_length=100,dbg = 0)

        DrawTools.draw_rotating_triangles_interp(canvas.frame, canvas.window_name,red_laser.ptsDeque,
        red_laser.polygonDeque,0,tail_length=100,dbg = 0)

        # DrawTools.draw_rotating_tri_fractals(canvas.frame, canvas.window_name,red_laser.ptsDeque,
        # red_laser.polygonDeque,(0,255,0),tail_length=100,dbg = 0)


        DrawTools.draw_tracking_reticle(frame,camera_window,red_laser)

    # if green_laser.onScreen:
    #     frame = DrawTools.draw_tracking_reticle(frame,green_laser)
    #     canvas.frame = DrawTools.draw_canvas_circle(canvas.frame, green_laser, (255, 0, 0))

    cv2.imshow(camera_window, frame)
    fps.update()
fps.stop()


print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
print("[INFO] Lost Track: {:.2f}".format(red_laser.lostTrackCounter))

#Housekeeping
if ret == 1:
    video_stream.stop()
cv2.destroyAllWindows()
