"""
Inpainting sample.
Inpainting repairs damage to images by floodfilling
the damage with surrounding image areas.
Usage:
  inpaint.py [<image>]
Keys:
  SPACE - inpaint
  r     - reset the inpainting mask
  ESC   - exit
"""

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2 as cv


class Sketcher:
    def __init__(self, windowname, dests, colors_func):
        self.prev_pt = None
        self.windowname = windowname
        self.dests = dests
        self.colors_func = colors_func
        self.dirty = False
        self.show()
        cv.setMouseCallback(self.windowname, self.on_mouse)

    def show(self):
        cv.imshow(self.windowname, self.dests[0])

    def on_mouse(self, event, x, y, flags, param):
        pt = (x, y)
        if event == cv.EVENT_LBUTTONDOWN:
            self.prev_pt = pt
        elif event == cv.EVENT_LBUTTONUP:
            self.prev_pt = None

        if self.prev_pt and flags & cv.EVENT_FLAG_LBUTTON:
            cv.line(pt, self.prev_pt, pt, self.colors_func, 5)
            self.dirty = True
            self.prev_pt = pt
            self.show()


def main():
    img = np.zeros((600, 600, 3), dtype=np.uint8)

    img_mark = np.zeros((600, 600, 3), dtype=np.uint8)
    mark = np.zeros(img.shape[:2], np.uint8)
    sketch = Sketcher("img", [img_mark, mark], lambda: ((255, 255, 255), 255))

    while True:
        ch = cv.waitKey()
        if ch == 27:
            break
        if ch == ord(" "):
            res = cv.inpaint(img_mark, mark, 3, cv.INPAINT_TELEA)
            cv.imshow("inpaint", res)
        if ch == ord("r"):
            img_mark[:] = img
            mark[:] = 0
            sketch.show()

    print("Done")


if __name__ == "__main__":
    print(__doc__)
    main()
    cv.destroyAllWindows()
