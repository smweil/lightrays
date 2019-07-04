import cv2
import numpy as np

src = np.array(
[[25, 25], [200, 20], [35, 210], [215, 200]], dtype=np.float32)
dest = np.array([[-50, -50], [50, -50], [-50, 50], [50, 50]], dtype=np.float32)
mtx = cv2.getPerspectiveTransform(src, dest)

print(mtx)
original = np.array(
[((40, 40), (1, 1))], dtype=np.float32)
print(original.shape)
# print(original)

converted = cv2.perspectiveTransform(original, mtx)
print(converted)
print(converted[0][0])

print(mtx.dot(([40,40,1])))
