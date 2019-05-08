import numpy as np
import cv2
import DrawTools
from collections import deque

pts= deque()
pts = [1, 5]
new_pts = [2, 3, 4]
pts[1:1] = new_pts
print(pts)

[pts.insert(1,pt) for pt in reversed(new_pts)]


print(pts)
