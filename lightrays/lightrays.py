import numpy as np
import cv2
import imutils
import CamTools
import TrackTools
import DrawTools
import CanvasTools
import config
import CamGUI
from imutils.video import FPS

# Windows names
camera_window_name = "Camera"
cv2.namedWindow(camera_window_name,cv2.WINDOW_NORMAL)
# camera_window = cv2.namedWindow(camera_window_name,cv2.WINDOW_NORMAL)
canvas = CanvasTools.Canvas(screen_resolution=(1280,720))


video_file = False #Set this flag to False if using a webcam
video_file = './bin/laserwall.mp4'

if video_file:
    red_lower = (config.laser_settings['red_lower_video'])
    red_upper = (config.laser_settings['red_upper_video'])
    video_stream = cv2.VideoCapture(video_file)
else:
    red_lower = (config.laser_settings['red_lower_k'])
    red_upper = (config.laser_settings['red_upper_k'])
    video_stream = CamTools.WebcamVideoStream(width=320, height=240).start()




ret, camera_frame = video_stream.read()
setup_flag = 1
camera_roi = None
user_defined_filter = 0 #flag if the user used custom HSV in the beginning
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
            cv2.imshow(camera_window_name, camera_frame)
            setup_flag =2

    #only stream the setup screen if it's from a webcam:
    if not video_file:
        ret, camera_frame = video_stream.read()

    if setup_flag ==2:
        key = cv2.waitKey(1) & 0xFF
        CamTools.draw_setup_text(camera_window_name,camera_frame)
        if key ==ord("s"):
            #Old school way of just utilizing a square:
            # camera_roi= CamTools.select_canvas_area(camera_window,camera_frame)

            camera_setup = CamTools.CameraSetup(
                camera_frame,canvas.frame_width,canvas.frame_height)


            cv2.setMouseCallback(camera_window_name,camera_setup.select_point)

            while len(camera_setup.points)<3:
                cv2.imshow(camera_window_name, camera_frame)
                cv2.waitKey(10)

            t_matrix = camera_setup.get_t_matrix()


            setup_flag =0
        if key ==ord("h"): #setup a new filter
            hsv_lower,hsv_upper = CamGUI.run_gui(camera_window,video_stream)
            user_defined_filter = 1
        if key == 13: #if enter key is hit first assume no cropping
            scale_factors = (1,1)
            setup_flag =0
        if camera_roi:
            camera_frame = CamTools.crop_by_bbox(camera_frame,camera_roi)
            scale_width = canvas.frame_width/camera_roi[2]
            scale_height = canvas.frame_height/camera_roi[3]
            scale_factors = (scale_width, scale_height)
        cv2.imshow(camera_window_name, camera_frame)


#Initialize trackers:
if user_defined_filter:
    red_laser = TrackTools.LaserTracker(hsv_lower,hsv_upper,scale_factors,100)
else:
    red_laser = TrackTools.LaserTracker(red_lower,red_upper,scale_factors,100)

#Dev note: Setup sliders in this file and just call them from the drawtools
#file

red_color = (0,255,0) #starting value for the pen
red_thickness = 3   #starting value for the pen

#Main loop:
DrawTools.DrawGUI.initialize_drawing_menu()
canvas.clear_image()
fps = FPS().start()
mode = 0
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
    elif key == ord("m"):
        canvas.clear_image()
        if mode>5:
            mode = 0
        mode +=1
        print("CLEARED")

    #Detect where the laser is:
    if ret == True:
        red_laser.run_full_detection(camera_frame)
        # green_laser.run_full_detection(camera_frame)
    else:
        break

    if red_laser.onScreen:
        if mode == 0:
            DrawTools.pen_mode(
                canvas.frame,canvas.window_name,red_laser.ptsDeque,
                red_color,red_thickness)
        elif mode ==1:
            DrawTools.draw_rainbow_snake(
                canvas.frame,canvas.window_name,
                red_laser.ptsDeque,thickness=-1)
        elif mode ==2:
            DrawTools.draw_3d_snake(
                canvas.frame,canvas.window_name,
                red_laser.ptsDeque, red_laser.polygonDeque,thickness=1)
        elif mode == 3:
            DrawTools.draw_simple_circle(
                canvas.frame,canvas.window_name,red_laser.ptsDeque)
        elif mode == 4:
            DrawTools.draw_rotating_triangles(
              canvas.frame, canvas.window_name,
              red_laser.ptsDeque, red_laser.polygonDeque)
        elif mode == 5:
            DrawTools.draw_comet(
              canvas.frame,canvas.window_name,
              red_laser.ptsDeque,color=0,tail_length = 200)


        DrawTools.draw_tracking_reticle(camera_frame,camera_window_name,red_laser)

    # if green_laser.onScreen:
    #     camera_frame = DrawTools.draw_tracking_reticle(camera_frame,green_laser)
    #     canvas.frame = DrawTools.draw_canvas_circle(canvas.frame, green_laser, (255, 0, 0))

    cv2.imshow(camera_window_name, camera_frame)
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
