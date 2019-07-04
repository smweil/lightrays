import cv2
import numpy as np



class CoordinateStore:
    def __init__(self,image):
        self.points = []
        self.image = image

    def select_point(self,event,x,y,flags,param):
            if event == cv2.EVENT_LBUTTONDBLCLK:
                cv2.circle(self.image,(x,y),3,(255,0,0),-1)
                self.points.append((x,y))


#instantiate class
img1 = np.zeros((512,512,3), np.uint8)
coordinateStore1 = CoordinateStore(img1)


# Create a black image, a window and bind the function to window

cv2.namedWindow('image')
cv2.setMouseCallback('image',coordinateStore1.select_point)

while(1):
    cv2.imshow('image',img1)
    k = cv2.waitKey(20) & 0xFF
    if k == 27:
        break
cv2.destroyAllWindows()


print("Selected Coordinates: ")
for i in coordinateStore1.points:
    print(i)
