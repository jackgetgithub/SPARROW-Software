# This script was used for testing purposes and does not involve in the final product/demo purposes
# This script was used to record footage of a camera while being in the air on the drone so footage can be gathered to train the human detection model

import cv2
import os

output_path = 'Webcam.mp4'
#output2_video_path = 'FLIR.mp4'

cap = cv2.VideoCapture(0)
#cap2 = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Cannot open the webcam")
    exit()

#if not cap2.isOpened():
    #print("Cannot open the FLIR")
    #exit()

ret, frame = cap.read()
if not ret:
    print("Cannot read a frame from the webcam")
    exit()
    
#ret2, frame2 = cap2.read()
#if not ret2:
    #print("Cannot read a frame from the FLIR")
    #exit()

height, width, layers = frame.shape
#height2, width2, layers2 = frame2.shape
fps = 2

gst_pipeline = (
    f"appsrc ! "
    f"video/x-raw,format=BGR,width={width},height={height},framerate={fps}/1 ! " 
    "videoconvert ! video/x-raw,format=I420 ! nvvidconv ! "
    "omxh264enc bitrate=8000000 ! "
    "h264parse ! qtmux ! "
    f"filesink location={output_path} sync=false"
)
#f"nvv4l2h264enc preset-level=4 insert-sps-pps=true bitrate=8000000 ! "
video = cv2.VideoWriter(
    gst_pipeline, 
    cv2.CAP_GSTREAMER, 
    0, 
    fps, 
    (width, height)
)
#video = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
#video2 = cv2.VideoWriter(output2_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width2, height2))

if not video.isOpened():
    print("Failed to open VideoWriter pipeline")
    exit(1)

while True:  

    ret, frame = cap.read()
    if not ret:
        print("Cannot read a frame from the webcam")
        break

    #ret2, frame2 = cap2.read()
    #if not ret2:
        #print("Cannot read a frame from the FLIR")
        #break
    
    #small_frame = cv2.resize(frame, (640, 480))
    #cv2.imshow("Webcam", small_frame)
    # cv2.imshow("FLIR", frame2)

    video.write(frame)
    print("wrote frame")
    #video2.write(frame2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
#video2.release()
cap.release()
cv2.destroyAllWindows()
