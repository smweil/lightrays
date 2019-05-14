import cv2
import numpy as np


#This class will handle the drawing canvas
class Canvas:
    def __init__(self, screen_resolution, screen=2):
        '''Sets up the drawing canvas
        need to autodetect screen_resolution
        '''
        self.screen_number = screen
        self.screen_res = screen_resolution
        self.window_name = "Canvas"

        #initalize image:
        self.frame_width = int(screen_resolution[0]/2)
        self.frame_height = int(screen_resolution[1]/2)

        #initalize window
        self.window_width = self.frame_width
        self.window_height =self.frame_height

        self.window = cv2.namedWindow(self.window_name,cv2.WINDOW_NORMAL)
        self.frame = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)

        #draw border here:
        self.draw_borders()

        #add target:


        cv2.imshow(self.window_name, self.frame)

    def draw_borders(self):
        center = (int(self.frame_width/2),int(self.frame_height/2))
        cv2.circle(self.frame,center, 50, (0, 0, 255), 3)
        top_left = (0,0)
        bottom_right = (self.frame_width,self.frame_height)
        cv2.rectangle(self.frame,  top_left, bottom_right, (0, 0, 255), 5)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(self.frame,'Canvas Setup',(int(self.frame_width/3),30),
         font, 1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(self.frame,'Resize: Q,E',(0,80), font, 1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(self.frame,'Fullscreen: F',(0,115), font, 1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(self.frame,'Done: <Enter>',(0,150), font, 1,(255,255,255),2,cv2.LINE_AA)
    def full_screen(self):
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def clear_image(self):
        height, width,_= self.frame.shape
        self.frame= np.ones((height, width, 3), dtype=np.uint8)
        cv2.imshow(self.window_name, self.frame)

    def resize_image(self,key):
         #Sizing the resolution with 'ASDW' keys
        '''
        need to add error checking if exceeds window
        '''
        if key  == ord("a"):
            #if self.frame_width<max:
            self.frame_width +=10
        elif key == ord("s"):
            if self.frame_height > 400:
                self.frame_height -=10
        elif key == ord("d"):
            if self.frame_width > 400:
                self.frame_width -=10
        elif key == ord("w"):
            self.frame_height +=10
        #Preserve aspect ratios:
        elif key == ord("e"):
            if self.frame_width > 400:
                self.frame_width -=10
                self.frame_height -=int(10*(self.frame_height/self.frame_width))
        elif key == ord("q"):
            self.frame_width +=10
            self.frame_height+=int(10*(self.frame_height/self.frame_width))

        self.frame= cv2.resize(self.frame, (self.frame_width, self.frame_height))

        self.clear_image()
        self.draw_borders()
        cv2.imshow(self.window_name, self.frame)

    def resize_window(self,key):
         #Sizing the resolution with 'ASDW' keys
        '''
        need to add error checking if exceeds window
        '''
        #Assume that widow size is the same as image size
        #Insert cross-plateform window size here eventually
        self.window_width = self.window_width
        self.window_height = self.window_height

        if key  == ord("j"):
            #if self.self.window_width<max:
            self.window_width +=10
        elif key == ord("k"):
            if self.window_height > 400:
                self.window_height -=10
        elif key == ord("l"):
            if self.window_width > 400:
                self.window_width -=10
        elif key == ord("i"):
            self.window_height +=10
        #Preserve aspect ratios:
        elif key == ord("e"):
            if self.window_width > 400:
                self.window_width -=10
                self.window_height -=int(10*(self.window_height/self.window_width))
        elif key == ord("q"):
            self.window_width +=10
            self.window_height+=int(10*(self.window_height/self.window_width))

        cv2.resizeWindow(self.window_name, self.window_width,self.window_height)
        cv2.imshow(self.window_name, self.frame)

        def get_screen_info(self):
            pass
