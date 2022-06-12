import cv2

# Tweaked version of imutils range-detector
# https://github.com/jrosebr1/imutils/blob/master/bin/range-detector


def initialize_cam_menu():
    camera_settings_window = "Camera Settings"
    cv2.namedWindow(camera_settings_window, 0)
    range = "HSV"
    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255
        for j in range:
            cv2.createTrackbar(
                "%s_%s" % (j, i), camera_settings_window, v, 255, callback
            )


def get_trackbar_values():
    values = []
    range = "HSV"
    for i in ["MIN", "MAX"]:
        for j in range:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Camera Settings")
            values.append(v)
    return values


def filter_cam(frame, values):
    frame_to_thresh = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    min_v = values[:3]
    max_v = values[3:6]
    thresh = cv2.inRange(frame_to_thresh, tuple(min_v), tuple(max_v))
    return thresh


def callback(value):
    pass


def run_gui(window, video_stream):
    initialize_cam_menu()
    hsv_values = []  # H_min, S_min, V_min, H_max, S_max, V_max

    while 1:
        # key = cv2.waitKey(1) & 0xFF
        key = cv2.waitKey(1) & 0xFF
        ret, frame = video_stream.read()
        hsv_values = get_trackbar_values()
        if ret:
            thresh_frame = filter_cam(frame, hsv_values)
            cv2.imshow(window, thresh_frame)
        if key == 13:  # Enter
            min_v = hsv_values[:3]
            max_v = hsv_values[3:6]
            print("MIN: ", min_v)
            print("MAX: ", max_v)
            cv2.destroyWindow("Camera Settings")
            return tuple(min_v), tuple(max_v)
            break
