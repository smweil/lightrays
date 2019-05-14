from threading import Thread, Lock
import cv2
#From: https://gist.github.com/allskyee/7749b9318e914ca45eb0a1000a81bf56

def crop_by_bbox(frame,bbox):
    #crops an image with a bounding box bbox = (xmin, ymin, width, height)
    frame = frame[bbox[1]:(bbox[1]+bbox[3]),bbox[0]:(bbox[0]+bbox[2])]
    return frame

def draw_setup_text(window_name,frame):
    width, height,_ = frame.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame,'Camera Setup',(int(width/3),30),
     font, 1,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(frame,'Select Area: S',(0,80), font, 1,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(frame,'Done: <Enter>',(0,150), font, 1,(255,255,255),2,cv2.LINE_AA)

def select_canvas_area(window_name,frame):
    '''
    displays the camera image and asks user to draw a bounding box
    to define the canvas
    '''
    bbox = cv2.selectROI(window_name, frame, fromCenter=False,
			showCrosshair=True)
    return bbox


class WebcamVideoStream :
    def __init__(self, src = 0, width = 320, height = 240) :
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()

    def start(self) :
        if self.started :
            print ("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self) :
        while self.started :
            (grabbed, frame) = self.stream.read()
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

    def read(self) :
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return 1, frame

    def stop(self) :
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback) :
        self.stream.release()

if __name__ == "__main__" :
    vs = WebcamVideoStream().start()
    while True :
        frame = vs.read()
        cv2.imshow('webcam', frame)
        if cv2.waitKey(1) == 27 :
            break

    vs.stop()
    cv2.destroyAllWindows()
