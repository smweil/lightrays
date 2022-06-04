from threading import Thread, Lock
import cv2
import numpy as np

# From: https://gist.github.com/allskyee/7749b9318e914ca45eb0a1000a81bf56


def crop_by_bbox(frame, bbox):
    # crops an image with a bounding box bbox = (xmin, ymin, width, height)
    frame = frame[bbox[1] : (bbox[1] + bbox[3]), bbox[0] : (bbox[0] + bbox[2])]
    return frame


def draw_setup_text(window_name, frame):
    width, height, _ = frame.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(
        frame,
        "Camera Setup",
        (int(width / 3), 30),
        font,
        1,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame, "Select Area: S", (0, 80), font, 1, (255, 255, 255), 2, cv2.LINE_AA
    )
    cv2.putText(
        frame, "New HSV Filter: H", (0, 115), font, 1, (255, 255, 255), 2, cv2.LINE_AA
    )
    cv2.putText(
        frame, "Done: <Enter>", (0, 150), font, 1, (255, 255, 255), 2, cv2.LINE_AA
    )


def select_canvas_area(window_name, frame):
    """
    displays the camera image and asks user to draw a bounding box
    to define the canvas

    This needs to be a four point transformation like L.A.S.E.R Tag
    """
    bbox = cv2.selectROI(window_name, frame, fromCenter=False, showCrosshair=True)
    return bbox


class CameraSetup:
    """
    Crops the camera frame and genterates a transformation matrix to use to
    undistort furture frames utilizing a 4 point transformation matrix.
    """

    def __init__(self, camera_window_name, image, canvas_width, canvas_height):
        self.points = []  # user selected points
        self.width = canvas_width
        self.height = canvas_height
        self.image = image
        cv2.setMouseCallback(camera_window_name, self.select_point)

        while len(self.points) < 4:
            cv2.imshow(camera_window_name, image)
            cv2.waitKey(10)
        t_matrix = self.get_t_matrix()

        print("setup complete")

    def select_point(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            cv2.circle(self.image, (x, y), 4, (0, 0, 255), -1)
            self.points.append((x, y))

    def get_t_matrix(self):
        self.points = self.order_points(self.points)
        destination_pts = np.array(
            [
                [0, 0],
                [self.width - 1, 0],
                [self.width - 1, self.height - 1],
                [0, self.height - 1],
            ],
            dtype="float32",
        )

        self.t_matrix = cv2.getPerspectiveTransform(self.points, destination_pts)
        return self.t_matrix

    def order_points(self, pts):
        # from: https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
        # initialzie a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype="float32")
        pts = np.array(pts)
        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        # return the ordered coordinates
        return rect


class WebcamVideoStream:
    def __init__(self, src=0, width=320, height=240):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()

    def start(self):
        if self.started:
            print("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            (grabbed, frame) = self.stream.read()
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

    def read(self):
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return 1, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.release()


if __name__ == "__main__":
    vs = WebcamVideoStream().start()
    while True:
        frame = vs.read()
        cv2.imshow("webcam", frame)
        if cv2.waitKey(1) == 27:
            break

    vs.stop()
    cv2.destroyAllWindows()
