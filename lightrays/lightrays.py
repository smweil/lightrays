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


video_file = False
# video_file = './bin/laserwall.mp4' #Set this flag to False if using a webcam


if video_file:
    red_lower = (config.laser_settings['red_lower_video'])
    red_upper = (config.laser_settings['red_upper_video'])
    video_stream = cv2.VideoCapture('./bin/laserwall.mp4')
else:
    red_lower = (config.laser_settings['red_lower_tv'])
    red_upper = (config.laser_settings['red_upper_tv'])
    video_stream = CamTools.WebcamVideoStream(width=500, height = 500).start()




ret, camera_frame = video_stream.read()
setup_flag = 1
camera_roi = None
while setup_flag:
    #Setup Canvas:
    if setup_flag ==1:
        key = cv2.waitKey(1) & 0xFF
        if key in [ord("a"),ord("d"), ord("w"),ord("s"),ord("q"),ord("e")]:
            canvas.resize_image(key)
        if key in [ord("j"), ord("i"), ord("k"), ord("l"),ord("u"), ord("o")]:
            canvas.resize_window(key)
        if key == ord("f"):
            canvas.full_screen()
        elif key == 13: #Enter key move on to camera setup
            ret, camera_frame = video_stream.read()
            cv2.imshow(camera_window, camera_frame)
            setup_flag =2

    #crop the camera to only see the canvas
    if setup_flag ==2:
        key = cv2.waitKey(1) & 0xFF
        ret, camera_frame = video_stream.read()
        CamTools.draw_setup_text(camera_window,camera_frame)
        if key ==ord("s"):
            camera_roi= CamTools.select_canvas_area(camera_window,camera_frame)
            setup_flag =0
        if camera_roi:
            camera_frame = CamTools.crop_by_bbox(camera_frame,camera_roi)
        cv2.imshow(camera_window, camera_frame)


#Width of the canvas/width of the camera
scale_width = canvas.frame_width/camera_roi[2]
scale_height = canvas.frame_height/camera_roi[3]
scale_factors = (scale_width, scale_height)


red_laser = TrackTools.LaserTracker(red_lower,red_upper,scale_factors,100)


canvas.clear_image()
fps = FPS().start()
#Main loop:
while(1):
    #Reload the new frame and crop image
    ret, camera_frame = video_stream.read()
    if ret and camera_roi: #crop the frame
        camera_frame = CamTools.crop_by_bbox(camera_frame,camera_roi)

    #Detect keyboard inputs:
    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    elif key == ord("c"):
        canvas.clear_image()
        print("CLEARED")

    #Detect where the laser is:
    if ret == True:
        red_laser.run_full_detection(camera_frame)
        # green_laser.run_full_detection(camera_frame)
    else:
        break

    if red_laser.onScreen:
        # canvas.frame =DrawTools.draw_contrails(canvas.frame, red_laser.ptsDeque,
        # (0,255,0),100,0)

        # DrawTools.draw_simple_circle(canvas.frame,canvas.window_name,red_laser.ptsDeque)

        DrawTools.draw_rotating_triangles_interp(canvas.frame, canvas.window_name,red_laser.ptsDeque,
        red_laser.polygonDeque,0,tail_length=100)

        DrawTools.draw_tracking_reticle(camera_frame,camera_window,red_laser)

    # if green_laser.onScreen:
    #     camera_frame = DrawTools.draw_tracking_reticle(camera_frame,green_laser)
    #     canvas.frame = DrawTools.draw_canvas_circle(canvas.frame, green_laser, (255, 0, 0))

    cv2.imshow(camera_window, camera_frame)
    fps.update()
fps.stop()


print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
print("[INFO] Lost Track: {:.2f}".format(red_laser.lostTrackCounter))

#Housekeeping
if ret == 1:
    video_stream.stop()
cv2.destroyAllWindows()
