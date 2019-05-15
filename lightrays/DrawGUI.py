import cv2
#Dev note: this could be a huge mistake?
#Should each drawing function have it's own custom menu?? Probably no...
SLIDER_LIST = ["Size","Hue","Rotation","Scale"]

def initialize_drawing_menu():
    '''
    Adds a gui for drawing adjustment on the fly
    '''
    cv2.namedWindow("Drawing Options", cv2.WINDOW_NORMAL)

    slider_value_max = [40,360,255,255]
    slider_value_min = [0,0,0,0]
    for i in range(len(SLIDER_LIST)):
        cv2.createTrackbar(SLIDER_LIST[i], "Drawing Options",
            slider_value_min[i], slider_value_max[i], callback)

def callback(value):
    pass

def get_trackbar_values(slider_names = []):
    values = []
    #Dev note: be able to make this grab values by name

    if not slider_names: #get all values
        for i in range(len(SLIDER_LIST)):
            v = cv2.getTrackbarPos(SLIDER_LIST[i], "Drawing Options")
            values.append(v)
    else:
        for i in range(len(slider_names)):
            v =cv2.getTrackbarPos(slider_names[i],"Drawing Options")
            values.append(v)
    return values
