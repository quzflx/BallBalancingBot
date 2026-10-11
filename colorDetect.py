import cv2 as cv
import numpy as np
import serial
import time
import math

# Defining arduinoooooooooo
arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(1)

#gausian filtering
#not used
# opposite direction 

def vector_info_and_draw(frame, origin_x, origin_y, dx, dy):
    # Magnitude of vector
    magnitude = math.sqrt(dx**2 + dy**2)

    # Angle in degrees (atan2 handles all quadrants)
    angle = math.degrees(math.atan2(dy, dx))

    # Opposite direction vector
    opp_dx = -dx
    opp_dy = -dy

    # End point of opposite arrow
    end_x = int(origin_x + opp_dx)
    end_y = int(origin_y + opp_dy)

    # Draw arrow (opposite direction)
    cv.arrowedLine(
        frame,
        (origin_x, origin_y),
        (end_x, end_y),
        (0, 255, 0),  # green arrow
        2,
        tipLength=0.2
    )

    return magnitude, angle

    


# Start webcam (0 = default camera)
cap = cv.VideoCapture(1)
cap.set(cv.CAP_PROP_ZOOM, 10)

# Define HSV range for detecting ORANGE color
lower_orange = np.array([10,100,100])   # lower bound (Hue, Saturation, Value)
upper_orange = np.array([35,255,255])  # upper bound

# Kernel used for removing noise (5x5 matrix of 1s)
kernel = np.ones((5,5), np.uint8)

while True:




    # Capture frame from webcam
    ret, frame = cap.read()

    # If frame not captured properly, exit loop
    if not ret:
        break

    # Get frame dimensions
    height, width, _ = frame.shape

    # Define center of the frame (origin)
    origin_x = width // 2
    origin_y = height // 2

    # Draw vertical line (Y-axis)
    cv.line(frame, (origin_x,0), (origin_x,height), (0), 1)

    # Draw horizontal line (X-axis)
    cv.line(frame, (0,origin_y), (width,origin_y), (0,0,0), 1)

    # Convert image from BGR to HSV color space
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # Create mask: only keep pixels in orange range
    # white = detected color, black = everything else
    mask = cv.inRange(hsv, lower_orange, upper_orange)

    # Remove small noise (tiny white dots)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)

    # Fill small holes inside detected object
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)

    # Find contours (edges of white regions in mask)
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # draw the aligning circle 
    # Circle properties
    radius = 220
    color = (0, 0, 20)
    thickness = 2    

    cv.circle(frame, (origin_x, origin_y), radius, color, thickness)         # main
    cv.circle(frame, (width-160, origin_y), 22, color, thickness)


    # If any object is detected
    if contours:

        # Get the largest contour (biggest orange object)
        largest = max(contours, key=cv.contourArea)

        # Ignore very small objects (noise)
        if cv.contourArea(largest) > 500:

            # Get bounding rectangle around object
            x, y, w, h = cv.boundingRect(largest)

            # Draw rectangle around object
            cv.rectangle(frame,(x,y),(x+w,y+h),(0,140,255),3)

            # Calculate center of the object
            cx = x + w//2
            cy = y + h//2

            # Draw center point
            cv.circle(frame,(cx,cy),3,(255,255,255),-1)

            # Calculate distance from center of screen
            dx = cx - origin_x
            dy = cy - origin_y

            # Draw line from center to object
            cv.line(frame, (origin_x,origin_y), (cx,cy), (255,232,14), 1)

            # Create text showing coordinates
            text = f"x: {dx}  y: {dy}"
            send = f"{int(dx/30)} {int(dy/30)}\n"

            # Write it out to the arduino ide serial port
            arduino.write(send.encode())
            if arduino.in_waiting:
                response = arduino.readline().decode().strip()
                print("Arduino says:", response)

            # Print coordinates in terminal
            print(text)

            # Show coordinates on screen
            cv.putText(frame, text, (20,40),
                       cv.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (251,116,255), 2)
            
            # Get magnitude and angle + draw opposite arrow
            magnitude, angle = vector_info_and_draw(frame, origin_x, origin_y, dx, dy)

            # Add to display text
            text = f"x: {dx}  y: {dy}  mag: {magnitude:.1f}  ang: {angle:.1f}"
            send = f"{dx} {dy}"

            

    # Show original frame with drawings
    cv.imshow("Frame", frame)

    # Show mask (what the algorithm "sees")
    # cv.imshow("Mask", mask)

    # Exit when 'q' is pressed
    if cv.waitKey(1) & 0xFF == ord('q'):
        arduino.close()
        break
        

# Release camera and close windows
cap.release()
cv.destroyAllWindows()