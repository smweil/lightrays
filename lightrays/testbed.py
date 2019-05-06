import numpy as np
import cv2
import DrawTools


center = (50,50)
height = 20


img = np.zeros((100,100,3), np.uint8)

pts = DrawTools.tri_from_center(center,height,270,1)


cv2.polylines(img,[pts],True,(0,255,255),lineType=cv2.LINE_AA)
cv2.imshow("test",img)
cv2.waitKey(0) # waits until a key is pressed
cv2.destroyAllWindows() # destroys the window showing image

# print(os.getcwd())
