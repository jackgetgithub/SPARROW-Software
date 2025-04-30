import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import tempfile
import os
import time
import cv2
import numpy as np
from pymavlink import mavutil

# --- Config ---
connection = mavutil.mavlink_connection('udpin:127.0.0.1:14552')
#ser = serial.Serial(None)
received_chunks = {}
expected_packets = None
img_type = 0  # 0 = RGB, 1 = Thermal

# --- GUI Setup ---
print("[GUI] Starting GUI...")

THEME_BG = "#2d3e50"  # Or whatever color you're using


root = tk.Tk()
root.title("SPARROW - Drone Ground Station")
root.configure(bg=THEME_BG)  # Light bluish-gray


# --- Top Bar ---
top_frame = tk.Frame(root, bg=THEME_BG)
top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
default_font = ("Segoe UI", 10)

image_frame = tk.Frame(root, bg=THEME_BG)
image_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

image_frame.grid_columnconfigure(0, weight=1)
image_frame.grid_columnconfigure(1, weight=1)

rgb_label = tk.Label(image_frame, text="RGB Feed", bg="gray", fg="white")
thermal_label = tk.Label(image_frame, text="Thermal Feed", bg="gray", fg="white")

# Make sure they expand
rgb_label.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
thermal_label.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

rgb_label.config(anchor="center")
thermal_label.config(anchor="center")

#set them to temporary size
#rgb_label.config(width=50, height=15)
#thermal_label.config(width=50, height=15)

gps_label = tk.Label(root, text="GPS: --, --", font=default_font, bg=THEME_BG, fg="white")
gps_label.grid(row=2, column=0, sticky="w", padx=10)

base_gps_label = tk.Label(top_frame, text="Base GPS: --, --", font=default_font, bg=THEME_BG, fg="white")
base_gps_label.pack(side="left")

log_text = tk.Text(root, height=8, width=100, bg="black", fg="green", wrap="word", font=default_font, insertbackground="white")
log_text.grid(row=3, column=0,columnspan=2, padx=10, pady=10, sticky="nsew")
log_text.config(state="disabled")


battery_canvas = tk.Canvas(top_frame, width=80, height=30, highlightthickness=0, bg=THEME_BG,)
battery_canvas.pack(side="right", padx=10)

battery_canvas.create_rectangle(5, 5, 65, 25, outline="black", width=2)  # main battery body
battery_canvas.create_rectangle(65, 10, 70, 20, fill="black")            # battery cap

# Draw initial tiers (example with 3 out of 5 filled)
battery_tiers = []
for i in range(5):
    x0 = 7 + i * 11
    x1 = x0 + 9
    tier = battery_canvas.create_rectangle(x0, 7, x1, 23, fill="gray", outline="")  # empty initially
    battery_tiers.append(tier)

#Toggle Buttons
def show_rgb_only():
    for widget in image_frame.winfo_children():
        widget.grid_forget()
    rgb_label.grid(row=0, column=0, padx=10)

def show_thermal_only():
    for widget in image_frame.winfo_children():
        widget.grid_forget()
    thermal_label.grid(row=0, column=0, padx=10)


def show_both():
    for widget in image_frame.winfo_children():
        widget.grid_forget()
    rgb_label.grid(row=0, column=0, padx=10)
    thermal_label.grid(row=0, column=1, padx=10)


button_frame = tk.Frame(top_frame, bg=THEME_BG)
button_frame.pack(side="left", expand=True)
tk.Button(button_frame, text="RGB Only", command=show_rgb_only, font=default_font, bg="white", fg="black").pack(side="left", padx=5)
tk.Button(button_frame, text="Thermal Only", command=show_thermal_only,font=default_font, bg="white", fg="black").pack(side="left", padx=5)
tk.Button(button_frame, text="Show Both", command=show_both, font=default_font, bg="white", fg="black").pack(side="left", padx=5)

#Log panel
def log_message(msg):
    def _log():
        log_text.config(state="normal")      # Temporarily enable editing
        log_text.insert(tk.END, f"{msg}\n")
        log_text.see(tk.END)
        log_text.config(state="disabled")    # Disable editing again
    log_text.after(0,_log)

# --- Helper to update images ---
def update_image_on_label(label, img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    height, width = img.shape[:2]
    # Calculate new dimensions while maintaining aspect ratio
    max_width = 320  # Increased from 320
    max_height = 240  # Increased from 240
    scale = min(max_width/width, max_height/height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    img = cv2.resize(img, (new_width, new_height))
    pil_image = Image.fromarray(img)
    tk_img = ImageTk.PhotoImage(pil_image)
    label.imgtk = tk_img
    label.config(image=tk_img, width=new_width, height=new_height)

# --- Image Decoder ---
def process_image():
    global img_type, received_chunks, expected_packets
    try:
        sorted_data = b''.join(received_chunks[k] for k in sorted(received_chunks.keys()))
        received_chunks = {}
        #np_arr = np.frombuffer(sorted_data, np.uint8)
        #img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # WORKAROUND: Use NamedTemporaryFile to avoid disk I/O bottlenecks
        # This uses memory mapping when possible, which is much faster than normal file I/O
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_name = temp_file.name
            temp_file.write(sorted_data)
        try:
            img = cv2.imread(temp_name)
            if img is not None:
                if img_type == 0:
                    update_image_on_label(rgb_label, img)
                elif img_type == 1:
                    update_image_on_label(thermal_label, img)
        except Exception as e:
            print(f"Error reading image: {e}")
        finally:
            # Clean up the temporary file
            received_chunks = {}
            print("Cleaned up chunks array")
            try:
                os.unlink(temp_name)
            except:
                pass
    except Exception as e1:
        print(f"Error in processing images: {e1}")


def serial_thread():
    global base_gps_label
    while True:
        try:
            received_data = ser.readline().decode('utf-8').strip()
            if "Latitude" in received_data and "Longitude" in received_data:
                parts = received_data.split()
                lat = float(parts[1])
                lon = float(parts[3])
                base_gps_label.config(text=f"Base GPS: {lat:.6f}, {lon:.6f}")
            if "Battery" in received_data:
                part = received_data.split()
                life = float(part[1])
                
                
                
        except Exception as e:
            print(f"[UART] Error parsing base GPS: {e}")
            
# --- MAVLink Thread ---
def mavlink_thread():
    global expected_packets, img_type, received_chunks
    t = ""
    while True:
        msg = connection.recv_match(blocking=False)
        if not msg:
            continue

        if msg.get_type() == 'DATA_TRANSMISSION_HANDSHAKE':
            expected_packets = msg.packets
            img_type = msg.height
            t = "Regular Image" if msg.height == 0 else "Thermal Image" # img_height used to tag image type
            received_chunks = {}
            info = f"[HANDSHAKE] Expecting {expected_packets} packets. Type: {t}"
            print(info)
            log_message(info)

        elif msg.get_type() == 'ENCAPSULATED_DATA':
            print(f"got chunky {msg.seqnr}")
            if msg.seqnr in received_chunks:
                continue
            received_chunks[msg.seqnr] = bytes(msg.data)
            if len(received_chunks) == expected_packets:
                info = f"[IMAGE] Received complete image of type {t}"
                print(info)
                log_message(info)
                process_image()

        elif msg.get_type() == 'HEARTBEAT':
            log_message("[HEARTBEAT] Received from drone.")

        elif msg.get_type() == 'GLOBAL_POSITION_INT':
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            gps_label.config(text=f"GPS: {lat:.6f}, {lon:.6f}")
            log_message(f"[GPS] Drone: {lat:.6f}, {lon:.6f}")

        elif msg.get_type() == "DATA_TRANSMISSON_HANDSHAKE":
            expected_packets = msg.packets
            img_type = msg.height
            received_chunks = {}
            info = f"[HANDSHAKE] Packets: {expected_packets}, Type: {t}"
            print(info)
            log_message(info)
            

# --- Start Thread ---
threading.Thread(target=mavlink_thread, daemon=True).start()
#threading.Thread(target=serial_thread, daemon=True).start()
# --- GUI Loop ---
show_both()
root.mainloop()
