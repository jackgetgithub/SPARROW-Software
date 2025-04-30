# NOTE: This is the exact same as the send.py except now we are adding the Human detection model which will start its set up before running the image transmission
# Please follow the comments in the send.py script for what should be changed accordingly for image transmission

import cv2
import time
from pymavlink import mavutil
from ultralytics import YOLO

# 1 for RGB cam and 2 for FLIR
camera = 0
camera2 = 1

udp_port ='udpout:127.0.0.1:14550'
connection = mavutil.mavlink_connection(udp_port, source_system=1)

def send_handshake(img_size, img_width, img_height, cycle):
    """Send MAVLink handshake before transmitting the image."""
    try:
        connection.mav.data_transmission_handshake_send(
            mavutil.mavlink.MAVLINK_DATA_STREAM_IMG_JPEG,  # Image type
            img_size,  # Image size in bytes
            cycle,  # Image width
            cycle,  # Image height
            (img_size // 253) + 1,  # Number of packets
            253,  # Payload per packet
            60  # JPEG quality
        )
        print(img_size // 253 + 1)
        print("Sent a transmission handshake")
    except Exception as e:
        print("Error in sending handshake")

def send_image(image, cycle):
    """Breaks image into MAVLink packets and sends them."""
    ret, encoded_img = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 75])
    img_bytes = encoded_img.tobytes()
    img_size = len(img_bytes)

    print(f"Total image size: {img_size} bytes")

    # Send handshake
    send_handshake(img_size, image.shape[1], image.shape[0], cycle)

    # Send image in chunks
    chunk_size = 253  # MAVLink encapsulated data chunk size
    for s in range(4):
        for seq in range(0, img_size, chunk_size):
            chunk = img_bytes[seq:seq + chunk_size]

            # Pad last chunk if necessary
            if len(chunk) < chunk_size:
                chunk += bytes(chunk_size - len(chunk))

            chunk = bytearray(chunk)
            num = int(seq // chunk_size)
            try:
                connection.mav.encapsulated_data_send(num, chunk)
            except Exception as e:
                print(f"Error sending chunk {seq // chunk_size}: {e}")

        time.sleep(0.15)  # Prevent buffer overflows
    time.sleep(0.6)
    

# Load the YOLOv8n model
model = YOLO('yolov8n.engine')
cap = cv2.VideoCapture(camera)  # Open camera
cap2 = cv2.VideoCapture(camera2) #Open the other camera
cycle = 0

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()
    
while True:
    try:
        if cycle == 0:
            ret, frame = cap.read()
            cycle = 1
        elif cycle == 1:
            ret, frame = cap2.read()
            cycle = 0 
            
        # Resize the frame to the desired dimensions (e.g., 640x480)
        resized_frame = cv2.resize(frame, (640, 480))

        # Perform inference on the resized frame
        results = model(resized_frame, device='cuda')  # Ensure 'cuda' is used for GPU inference

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the resulting frame
        #cv2.imshow('YOLOv8 Inference', annotated_frame)

        resized_frame = cv2.resize(annotated_frame, (160, 128))
        send_image(resized_frame, cycle)
        time.sleep(5)  # Adjust based on transmission speed
        
        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except KeyboardInterrupt:
        break
cap.release()
cap2.release()
# cv2.destroyAllWindows()
