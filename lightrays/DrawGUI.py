import cv2
#Dev note: this could be a huge mistake?
slider_list = ["Size","Hue","Future 1","Future 2"]

def initialize_drawing_menu(slider_list,min):
    '''
    Adds a gui for drawing adjustment on the fly
    '''
    cv2.namedWindow("Drawing Options", cv2.WINDOW_NORMAL)

    slider_value_max = [40,360,255,255]
    slider_value_min = [0,0,0,0]
    for i in range(len(slider_list)):
        cv2.createTrackbar(slider_list[i], "Drawing Options",
            slider_value_min[i], slider_value_max[i], callback)

def callback(value):
    pass

def get_trackbar_values():
    values = []
    for i in range(len(slider_list)):
        v = cv2.getTrackbarPos(slider_list[i], "Drawing Options")
        values.append(v)
    values[0] = 1 if values[0]<1 else values[0]#thickness can't be 0
    return values
