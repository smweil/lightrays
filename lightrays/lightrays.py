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

blueLower = (105, 133, 88)
blueUpper = (142, 255, 255)
greenLower= (0, 180, 26)
greenUpper = (13, 255, 255)


blueCap = TrackTools.LaserTracker(blueLower,blueUpper,50)
greenCap = TrackTools.LaserTracker(greenLower,greenUpper,255)


video_stream = CamTools.WebcamVideoStream(width=500, height = 500).start()
fps = FPS().start()

#Main loop:
while(1):
    #Reload the new frames
    frame = video_stream.read()
    canvas_image = np.zeros(canvas_size, dtype=np.uint8)

    #Detect keyboard inputs:
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    #Detect where the laser is:
    blueCap.run_full_detection(frame)
    # greenCap.run_full_detection(frame)

    if blueCap.onScreen:
        # frame = DrawTools.draw_tracking_reticle(frame,blueCap)
        # canvas_image = DrawTools.draw_canvas_circle(canvas_image, blueCap, (255, 0, 0))
        canvas_image =DrawTools.draw_contrails(canvas_image, blueCap,
        (255,0,0),255,1)



    # if greenCap.onScreen:
    #     frame = DrawTools.draw_tracking_reticle(frame,greenCap)
    #     canvas_image = DrawTools.draw_canvas_circle(canvas_image, greenCap, (255, 0, 0))

    cv2.imshow(camera_window, frame)
    cv2.imshow(canvas_window, canvas_image)
    fps.update()

fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

#Housekeeping
video_stream.stop()
cv2.destroyAllWindows()
