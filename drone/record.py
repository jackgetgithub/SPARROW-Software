# This script was used for testing purposes and does not involve in the final product/demo purposes
# This script was used to record footage of a camera while being in the air on the drone so footage can be gathered to train the human detection model

import cv2

output_path = 'RGB.mp4'
output_path2 = 'FLIR.mp4'

cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Cannot open the camera")
    exit()

if not cap2.isOpened():
    print("Cannot open the FLIR")
    exit()

ret, frame = cap.read()
if not ret:
    print("Cannot read a frame from the camera")
    exit()
    
ret2, frame2 = cap2.read()
if not ret2:
    print("Cannot read a frame from the FLIR")
    exit()

height, width, layers = frame.shape
height2, width2, layers2 = frame2.shape
fps = 2

# Define the GStreamer pipeline for RGB camera for hardware encoding
gst_pipeline = (
    f"appsrc ! "
    f"video/x-raw,format=BGR,width={width},height={height},framerate={fps}/1 ! " 
    "videoconvert ! video/x-raw,format=I420 ! nvvidconv ! "
    "omxh264enc bitrate=8000000 ! "
    "h264parse ! qtmux ! "
    f"filesink location={output_path} sync=false"
)
# Define the GStreamer pipeline for FLIR camera for hardware encoding
gst_pipeline2 = (
    f"appsrc ! "
    f"video/x-raw,format=BGR,width={width2},height={height2},framerate={fps}/1 ! " 
    "videoconvert ! video/x-raw,format=I420 ! nvvidconv ! "
    "omxh264enc bitrate=8000000 ! "
    "h264parse ! qtmux ! "
    f"filesink location={output_path2} sync=false"
)


video = cv2.VideoWriter(
    gst_pipeline, 
    cv2.CAP_GSTREAMER, 
    0, 
    fps, 
    (width, height)
)

video2 = cv2.VideoWriter(
    gst_pipeline2, 
    cv2.CAP_GSTREAMER, 
    0, 
    fps, 
    (width2, height2)
)

if not video.isOpened():
    print("Failed to open VideoWriter pipeline")
    exit(1)

if not video2.isOpened():
    print("Failed to open VideoWriter pipeline")
    exit(1)


while True:  

    ret, frame = cap.read()
    if not ret:
        print("Cannot read a frame from the webcam")
        break

    ret2, frame2 = cap2.read()
    if not ret2:
        print("Cannot read a frame from the FLIR")
        break
    
    
    video.write(frame)
    print("wrote RGB frame")
    video2.write(frame2)
    print("wrote FLIR frame")

    #small_frame = cv2.resize(frame, (640, 480))
    #small_frame2 = cv2.resize(frame2, (640, 480))
    
    # cv2.imshow("RGB", small_frame)
    # cv2.imshow("FLIR", small_frame2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
video2.release()
cap.release()
cv2.destroyAllWindows()
