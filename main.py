"""Run for results"""
import cv2
import numpy as np
import csv
import os
# import serial
# import time

#CONFIGURATION
VIDEO_INPUT="low_input.mp4"
VIDEO_OUTPUT="processed_output.mp4"
CSV_OUTPUT="ball_events.csv"
CORNERS_FILE="table_corners.npy"

DISPLAY_SCALE=1.5
GAME_OVER_FRAME=290

TABLE_WIDTH=1.525   #meters
TABLE_LENGTH=2.74    #meters

#Serial / ESP32 settings
# ESP_PORT="COM7"   #<-- change to match your Device Manager / ls /dev/tty*
# ESP_BAUD=115200

#SERIAL SETUP
# ser=None
# try:
#     ser=serial.Serial(ESP_PORT,ESP_BAUD,timeout=1)
#     time.sleep(2)          #wait for ESP32 reset
#     print(f"[SERIAL] Connected to ESP32 on {ESP_PORT}")
# except Exception as e:
#     print(f"[SERIAL] Could not open port {ESP_PORT}: {e}")
#     print("[SERIAL] Continuing without serial output.")

# def send_to_esp(x: float,y: float,frame_id: int):
#     """Send bounce coordinates to ESP32 as a CSV line: frame,x,y\n"""
#     if ser and ser.is_open:
#         msg=f"{frame_id},{x:.3f},{y:.3f}\n"
#         ser.write(msg.encode())
#         print(f"[SERIAL] Sent->{msg.strip()}")
#         time.sleep(0.02)
#         if ser.in_waiting:
#             ack=ser.readline().decode(errors="ignore").strip()
#             if ack:
#                 print(f"[SERIAL] ESP32 ACK: {ack}")

#TABLE CALIBRATION
if not os.path.exists(CORNERS_FILE):
    print(f"ERROR: {CORNERS_FILE} not found. Run calibrate_table.py first.")
#     if ser:
#         ser.close()
#     exit()

table_corners=np.load(CORNERS_FILE).astype(np.float32)
print("Loaded table corners:",table_corners)

table_pts=np.array([
    [0.0,0.0],  #bottom-left
    [TABLE_LENGTH,0.0],  #bottom-right
    [TABLE_LENGTH,TABLE_WIDTH],  #top-right
    [0.0,TABLE_WIDTH],  #top-left
],dtype=np.float32)

H,_=cv2.findHomography(table_corners,table_pts)

corner_labels={0: "(0,0)",1: "(W,0)",2: "(W,L)",3: "(0,L)"}

#VIDEO I/O
cap=cv2.VideoCapture(VIDEO_INPUT)
fps=cap.get(cv2.CAP_PROP_FPS) or 30.0

ret,frame=cap.read()
if not ret:
    print("ERROR: Cannot read video.")
    # if ser: ser.close()
    exit()

fourcc=cv2.VideoWriter_fourcc(*"mp4v")
out=cv2.VideoWriter(VIDEO_OUTPUT,fourcc,fps,(frame.shape[1],frame.shape[0]))

#CSV OUTPUT
csv_file=open(CSV_OUTPUT,"w",newline="")
writer=csv.writer(csv_file)
writer.writerow(["frame","x_table","y_table"])

#TRACKING STATE (from code 1)
prev_y =None
prev_vy=None

frame_id  =0
game_over =False

#MORPHOLOGY KERNEL
kernel=np.ones((5,5),np.uint8)

#MAIN LOOP
while True:
    #game-over flag
    if frame_id >= GAME_OVER_FRAME: game_over=True

    #HSV+masks
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    #Ball: yellow-orange
    lower_ball=np.array([15,150,150])
    upper_ball=np.array([35,255,255])
    mask=cv2.inRange(hsv,lower_ball,upper_ball)

    #Remove green table
    green_lower=np.array([35, 80, 80])
    green_upper=np.array([85,255,255])
    green_mask =cv2.inRange(hsv,green_lower,green_upper)
    mask=cv2.bitwise_and(mask,cv2.bitwise_not(green_mask))

    #Clean
    mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel)
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel)

    #Contours->ball centre
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cx=cy=None

    for c in contours:
        area=cv2.contourArea(c)
        if 50 < area < 500:
            x,y,w,h_box=cv2.boundingRect(c)
            if 0.7 < w / float(h_box) < 1.3:
                cx=x+w//2
                cy=y+h_box//2
                break

    #Bounce detection+coordinate mapping (code 1 logic)
    bounce_detected=False

    if cx is not None:
        cv2.circle(frame,(cx,cy),5,(0,255,0),-1)   #tracking dot (green)

        if prev_y is not None:
            vy=cy-prev_y   #+ve->moving down,-ve->moving up
            if prev_vy is not None:
                #DOWN->UP transition=table bounce
                if prev_vy > 2 and vy < -2:
                    bounce_detected=True
            prev_vy=vy
        prev_y=cy

        #On bounce: map->table coords,save,send
        if bounce_detected:
            pt=np.array([[[cx,cy]]],dtype=np.float32)
            table_pt=cv2.perspectiveTransform(pt,H)
            xt,yt  =table_pt[0][0]

            print(f"BOUNCE at frame {frame_id}: x={xt:.3f} m,y={yt:.3f} m")
            #CSV
            writer.writerow([frame_id,xt,yt])
            #ESP32
            # send_to_esp(xt,yt,frame_id)
            #Visual: blue ring at bounce point
            cv2.circle(frame,(cx,cy),14,(255,0,0),3)
            #Label
            cv2.putText(frame,f"BOUNCE ({xt:.2f},{yt:.2f})",(cx+16,cy-16),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2,cv2.LINE_AA)

    #Table corner markers
    for idx,(px,py) in enumerate(table_corners.astype(int)):
        cv2.circle(frame,(px,py),6,(0,0,0),-1)
        cv2.putText(frame,corner_labels[idx],(px+8,py-8),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2,cv2.LINE_AA)

    #HUD
    h_fr,w_fr,_=frame.shape

    cv2.putText(frame,f"Frame: {frame_id}",(20,50),cv2.FONT_HERSHEY_SIMPLEX,1.1,(0,0,255),3)

    # esp_status="ESP32: CONNECTED" if (ser and ser.is_open) else "ESP32: NO CONNECTION"
    # esp_color =(0,200,0) if (ser and ser.is_open) else (0,0,255)
    # cv2.putText(frame,esp_status,(20,90),cv2.FONT_HERSHEY_SIMPLEX,0.8,esp_color,2,cv2.LINE_AA)

    if game_over: cv2.putText(frame,"GAME OVER",(w_fr//2-220,h_fr//2),cv2.FONT_HERSHEY_SIMPLEX,2.5,(0,0,255),6,cv2.LINE_AA)

    #Write processed frame
    out.write(frame)

    #Display
    frame_disp=cv2.resize(frame,None,fx=DISPLAY_SCALE,fy=DISPLAY_SCALE)
    cv2.imshow("Ball Tracking+ESP32",frame_disp)
    cv2.setWindowProperty("Ball Tracking+ESP32",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    if cv2.waitKey(int(1000 / fps)) & 0xFF == 27:  break

    #Next frame
    ret,frame=cap.read()
    if not ret: break
    frame_id += 1

#CLEANUP
cap.release()
out.release()
csv_file.close()
cv2.destroyAllWindows()

# if ser and ser.is_open:
#     ser.close()
#     print("[SERIAL] Port closed.")

print(f"Done. Processed {frame_id} frames.")
print(f"  Video saved ->{VIDEO_OUTPUT}")
print(f"  CSV saved   ->{CSV_OUTPUT}")