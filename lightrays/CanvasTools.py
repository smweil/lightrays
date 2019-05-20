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
        cv2.putText(self.frame,'Resize Image: Q,E',(0,80), font, 1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(self.frame,'Resize Window: U,O',(0,115), font, 1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(self.frame,'Fullscreen: F',(0,150), font, 1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(self.frame,'Done: <Enter>',(0,185), font, 1,(255,255,255),2,cv2.LINE_AA)

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
        if key  == ord("d"):
            #if self.frame_width<max:
            self.frame_width +=10
        elif key == ord("s"):
            if self.frame_height > 400:
                self.frame_height -=10
        elif key == ord("a"):
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

        if key  == ord("l"):
            #if self.self.window_width<max:
            self.window_width +=10
        elif key == ord("k"):
            if self.window_height > 400:
                self.window_height -=10
        elif key == ord("j"):
            if self.window_width > 400:
                self.window_width -=10
        elif key == ord("i"):
            self.window_height +=10
        #Preserve aspect ratios:
        elif key == ord("u"):
            if self.window_width > 400:
                self.window_width -=10
                self.window_height -=int(10*(self.window_height/self.window_width))
        elif key == ord("o"):
            self.window_width +=10
            self.window_height+=int(10*(self.window_height/self.window_width))

        cv2.resizeWindow(self.window_name, self.window_width,self.window_height)
        cv2.imshow(self.window_name, self.frame)

    def get_screen_info(self):
        pass

    def get_canvas_transform(pts):
        self.t_matrix = four_point_transform(self.frame_width,
                                        self.frame_height,pts)




class CoordinateStore:
    def __init__(self,window_name):
        self.points = []
        self.click_count = 0
        self.window_name = window_name
        print("initiated")

    def select_point(self,event,x,y,flags,param):
            print("clicky")
            if event == cv2.EVENT_LBUTTONDBLCLK:
                print("click")
                cv2.circle(self.window_name,(x,y),3,(255,0,0),-1)
                self.points.append((x,y))
                self.click_count +=1




    def order_points(self):
        '''
        From:
        https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
        '''
    	# initialzie a list of coordinates that will be ordered
    	# such that the first entry in the list is the top-left,
    	# the second entry is the top-right, the third is the
    	# bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype = "float32")

    	# the top-left point will have the smallest sum, whereas
    	# the bottom-right point will have the largest sum
        s = self.points.sum(axis = 1)
        rect[0] = self.points[np.argmin(s)]
        rect[2] = self.points[np.argmax(s)]

    	# now, compute the difference between the points, the
    	# top-right point will have the smallest difference,
    	# whereas the bottom-left will have the largest difference
        diff = np.diff(self.points, axis = 1)
        rect[1] = self.points[np.argmin(diff)]
        rect[3] = self.points[np.argmax(diff)]

    	# return the ordered coordinates
        self.points = rect


def four_point_transform(width,height,pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect

	dst = np.array([
		[0, 0],
		[width - 1, 0],
		[width - 1, height - 1],
		[0, height - 1]], dtype = "float32")

	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)

	# return the transformation matrix
	return M
