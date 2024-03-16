# Import necessary libraries
import cv2
import pytesseract
import RPi.GPIO as GPIO
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import AngularServo
from time import sleep

# Set up GPIO (General Purpose Input/Output) for sensor and servo
GPIO.setmode(GPIO.BCM)

# Define the pin for the infrared sensor
ir1_pin = 2
GPIO.setup(ir1_pin, GPIO.IN)
ir2_pin = 4
GPIO.setup(ir2_pin, GPIO.IN)
ir3_pin = 14
GPIO.setup(ir3_pin, GPIO.IN)

# Set up GPIO factory for servo motor
factory = PiGPIOFactory()

# Define the pin for the servo motor
servo1_pin = 3
servo2_pin = 17

# Configure the servo motor with specific pulse widths and pin factory
servo1 = AngularServo(servo1_pin, min_pulse_width=0.0006, max_pulse_width=0.0023, pin_factory=factory)
servo2 = AngularServo(servo2_pin, min_pulse_width=0.0006, max_pulse_width=0.0023, pin_factory=factory)

# Folder to store captured images
folder_name = "images"

# Variable to store the previous state of the infrared sensor
previous_sensor1_state = GPIO.input(ir1_pin)
previous_sensor2_state = GPIO.input(ir2_pin)
previous_sensor3_state = GPIO.input(ir3_pin)

# Counter for naming captured images
counter = 1

# Initial position of the servo (barrier lowered)
servo1.angle = 0  # [Lowered Barrier]
servo2.angle = 0

# Initial position of the servo (barrier lifted)
# servo1.angle = 90  # [Lifted Barrier]
# servo2.angle = 90

# Path to the Haar Cascade XML file for Russian license plates
harcascade = "model/haarcascade_russian_plate_number.xml"

# Create a VideoCapture object to access the camera (camera index 0)
cap = cv2.VideoCapture(0)

# Set camera width and height
cap.set(3, 640)  # width
cap.set(4, 480)  # height

# Minimum area for a detected region to be considered a license plate
min_area = 500

# Flag to control image processing loop
process_image = True

# Wait for 3 seconds before starting the main loop
sleep(3)

print("[Script started...]")

# Main loop
while True:

    sleep(0.01)

    # Read the current state of the infrared sensor
    sensor1_state = GPIO.input(ir1_pin)
    sensor2_state = GPIO.input(ir2_pin)
    sensor3_state = GPIO.input(ir3_pin)

    # Check for a change in sensor state
    if sensor1_state != previous_sensor1_state:
        previous_sensor1_state = sensor1_state

        # If the sensor state is LOW (vehicle detected)
        if sensor1_state == 0:
            print("\n-----------------------------------------------------")
            print("[Baricade down]")
            print()

            # Lower the barrier (set servo angle to 0)
            servo1.angle = 0
            sleep(1)

            # Capture an image
            file_name = folder_name + "/scanned_img_" + str(counter) + ".jpg"

            # Image processing loop
            while process_image:

                sleep(0.01)

                # Read a frame from the camera
                success, img = cap.read()

                # Uncomment the next line if the captured frame needs to be rotated by 180 degrees
                img = cv2.rotate(img, cv2.ROTATE_180)

                # Create a Haar Cascade classifier for license plates
                plate_cascade = cv2.CascadeClassifier(harcascade)

                # Convert the captured frame to grayscale
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # Detect license plates in the grayscale frame
                plates = plate_cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=4)

                # Loop through the detected plates and process each one
                for (x, y, w, h) in plates:
                    area = w * h

                    # Check if the detected region has a sufficient area to be considered a license plate
                    if area > min_area:
                        # Extract the region of interest (ROI) corresponding to the license plate
                        img_roi = img[y: y + h, x: x + w]

                        # Save the scanned image with a unique file name
                        cv2.imwrite(file_name, img_roi)

                        print("Saved:", file_name)

                        # Extract text using Tesseract
                        license_plate_no = pytesseract.image_to_string(file_name)
                        print("License Plate Number:", license_plate_no)

                        print("Characters ")

                        for char_ in license_plate_no:
                            print(f"{char_}", end="| ")
                        print()

                        print(f"Checking `{license_plate_no}` in Database...")
                        print()

                        # Check if the license plate number matches a predefined value
                        if license_plate_no == "GJ03AU45" or "GJ03AU45" in license_plate_no or "GJO3AU45" in license_plate_no:
                            print("[Registered vehicle. Barrier is lifted]")
                            # Lift the barrier (set servo angle to 90)
                            servo1.angle = 90
                            sleep(5)
                            # Lower the barrier (set servo angle to 0)
                            servo1.angle = 0
                            sleep(1)

                        else:
                            print("[Barrier remains closed]")
                            # Lower the barrier (set servo angle to 0)
                            servo1.angle = 0
                            sleep(1)

                        # Increment the counter
                        counter += 1

                        # Set the flag to end the image processing loop
                        process_image = False  # Line to break image processing `while` loop

                        # Break out of the loop
                        break  # Line to break plates detection `for` loop

            process_image = True

    if sensor2_state != previous_sensor2_state:
        previous_sensor2_state = sensor2_state

        # If the sensor state is LOW (vehicle detected)
        if sensor2_state == 0:
            # Lift the barrier (set servo angle to 90)
            servo2.angle = 90
            sleep(5)
            # Lower the barrier (set servo angle to 0)
            servo2.angle = 0
            sleep(1)

    if sensor3_state != previous_sensor3_state:
        previous_sensor3_state = sensor3_state

        # If the sensor state is LOW (vehicle detected)
        if sensor3_state == 0:
            # Lift the barrier (set servo angle to 90)
            servo2.angle = 90
            sleep(5)
            # Lower the barrier (set servo angle to 0)
            servo2.angle = 0
            sleep(1)

# Lines important but out of reach of execution:
# Release the camera and close all OpenCV windows
# cap.release()
# cv2.destroyAllWindows()

# Clean up GPIO resources
# GPIO.cleanup()

# End of the script
# print("[Ending of script...]")
