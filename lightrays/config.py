"""
This file contains laser detection settings as HSV values
"""
general_settings = {
    # number of lasers to use -- color is in the order in "laser_settings"
    "lasers": 1,
    "projector_resolution": (800, 600),  # width,height
}


laser_settings = {
    # The order here determines which colors are used first to last
    "red_lower": (170, 0, 208),
    "red_upper": (255, 255, 255),
    "red_lower_k": (150, 125, 164),
    "red_upper_k": (255, 255, 255),
    "red_lower_tv": (120, 0, 133),
    "red_upper_tv": (255, 255, 255),
    "green_lower": (0, 180, 26),
    "green_upper": (13, 255, 255),
    "green_lower_video": (0, 100, 229),
    "green_upper_video": (107, 255, 255),
    "blue_lower": (105, 133, 88),
    "blue_upper": (255, 255, 255),
    "red_lower_video": (0, 110, 84),
    "red_upper_video": (11, 144, 255),
}
