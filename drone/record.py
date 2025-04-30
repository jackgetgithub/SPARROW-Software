# This script was used for recording footage while on the drone, this script was used for recording with both cameras

import cv2
import os

#cap = cv2.VideoCapture(3)
cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)
output_video_path = 'Webcam.mp4'
output2_video_path = 'FLIR.mp4'

if not cap.isOpened():
    print("Cannot open the webcam")
    exit()

if not cap2.isOpened():
    print("Cannot open the FLIR")
    exit()

ret, frame = cap.read()
if not ret:
    print("Cannot read a frame from the webcam")
    exit

ret2, frame2 = cap2.read()
if not ret2:
    print("Cannot read a frame from the FLIR")
    exit

height, width, layers = frame.shape
height2, width2, layers2 = frame2.shape
fps = 30
video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
video2 = cv2.VideoWriter(output2_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width2, height2))

while True:
    ret, frame = cap.read()
    if not ret:
        print("Cannot read a frame from the webcam")
        break

    ret2, frame2 = cap2.read()
    if not ret2:
        print("Cannot read a frame from the FLIR")
        break
    cv2.imshow("Webcam", cv2.resize(frame,(640,480)))
    cv2.imshow("FLIR", frame2)
    video.write(frame)
    video2.write(frame2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        video.release()
        video2.release()
        cv2.destroyAllWindows()
        break
