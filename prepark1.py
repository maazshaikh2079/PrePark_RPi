# prepark1.py

# Import necessary libraries
import RPi.GPIO as GPIO
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import AngularServo

import cv2
import pytesseract

import firebase_admin
from firebase_admin import credentials, firestore

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

# Path to the Haar Cascade XML file for Russian license plates
harcascade = "model/haarcascade_russian_plate_number.xml"

# Minimum area for a detected region to be considered a license plate
min_area = 500

# Flag to control image processing loop
process_image = True

# Access firebase firestore cloud database credentials
cred = credentials.Certificate("firebase-config/prepark-sap-firebase-adminsdk-bft4o-4aead8250d.json")

# Initialize app by giving firestore database credentials as parameter
firebase_admin.initialize_app(cred)

# Set up firestore client
db = firestore.client()

# Specify a collection name from database
collection_name = "License_Plates"

# Get documents from specific collection in database with help firestore client
docs = db.collection(collection_name).get()

# Setting a flag for plate checking
plate_present = False

print("[Script started...]")

# Main loop
while True:

    # Wait to minimize CPU consumption
    sleep(0.01)

    # Read the current state of the infrared sensor
    sensor1_state = GPIO.input(ir1_pin)
    sensor2_state = GPIO.input(ir2_pin)
    sensor3_state = GPIO.input(ir3_pin)

    # Check for a change in 1st sensor's state
    if sensor1_state != previous_sensor1_state:
        previous_sensor1_state = sensor1_state

        # If the sensor state is LOW (vehicle detected)
        if sensor1_state == 0:
            print("\n-----------------------------------------------------")
            print("[Barricade down]")
            print()

            # Lower the barrier (set servo angle to 0)
            servo1.angle = 0
            sleep(1)

            # Capture an image
            file_name = folder_name + "/scanned_img_" + str(counter) + ".jpg"

            # Image processing loop
            while process_image:

                # Wait to minimize CPU consumption
                sleep(0.01)

                # Create a VideoCapture object to access the camera (camera index 0)
                cap = cv2.VideoCapture(0)

                # sleep(0.5)

                # Set camera width and height
                cap.set(3, 640)  # width
                cap.set(4, 480)  # height

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
                        print()

                        # print("Characters in license plate no.:")
                        # for char_ in license_plate_no:
                        #    print(f"{char_}", end="| ")
                        # print()

                        print(f"Checking `{license_plate_no}` in Database...")
                        print()

                        # Check if the license plate number matches with a plate in database
                        if docs:
                            for doc in docs:
                                plate = doc.to_dict()
                                plate_number = list(plate.values())
                                plate_number = plate_number[0]

                                if plate_number == license_plate_no or plate_number in license_plate_no:
                                    # Setting flag "True" as plate is present in DB
                                    plate_present = True
                                    break

                            if plate_present == True:
                                # Lift the barrier (set servo angle to 90)
                                print("[Registered vehicle; Barricade is lifted]")
                                servo1.angle = 90
                                sleep(5)

                                # Lower the barrier (set servo angle to 0)
                                print("[Barricade down]")
                                servo1.angle = 0
                                sleep(1)
                                plate_present = False
                            else:
                                print("[Unregistered vehicle; Barricade remains closed]")
                                # Lower the barrier (set servo angle to 0)
                                servo1.angle = 0
                                sleep(1)

                        # Increment the counter
                        counter += 1

                        # Release the camera and close all OpenCV windows
                        cap.release()
                        cv2.destroyAllWindows()

                        # Set the flag to end the image processing loop
                        process_image = False  # Line to break image processing `while` loop

                        # Break out of the loop
                        break  # Line to break plates detection `for` loop

            # Set the flag to again start the image processing `while` loop
            process_image = True

    # Check for a change in 2nd sensor's state
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

    # Check for a change in 3rd sensor's state
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
# Clean up GPIO resources
# GPIO.cleanup()

# End of the script
# print("[Ending of script...]")
