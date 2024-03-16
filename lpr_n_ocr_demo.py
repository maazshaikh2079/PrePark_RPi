# Import the OpenCV library
import cv2
from time import sleep
import pytesseract

# Path to the Haar Cascade XML file for Russian license plates
harcascade = "model/haarcascade_russian_plate_number.xml"

# Create a VideoCapture object to access the camera (camera index 0)
cap = cv2.VideoCapture(0)

# Set camera width and height
cap.set(3, 640)  # width
cap.set(4, 480)  # height

# Minimum area for a detected region to be considered a license plate
min_area = 500

# Counter to keep track of saved plates
count = 0

# Flag variable to control the loop
process_image = True

# Infinite loop to continuously capture frames from the camera
while process_image:

    sleep(0.01)

    # Read a frame from the camera
    success, img = cap.read()

    # Uncomment the next line if the captured frame needs to be rotated by 180 degrees
    img = cv2.rotate(img, cv2.ROTATE_180)

    sleep(2)

    # Create a Haar Cascade classifier for license plates
    plate_cascade = cv2.CascadeClassifier(harcascade)

    # Convert the captured frame to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect license plates in the grayscale frame
    plates = plate_cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=4)

    # Loop through the detected plates and process each one
    for (x, y, w, h) in plates:
        # Calculate the area of the detected region
        area = w * h

        # Check if the detected region has a sufficient area to be considered a license plate
        if area > min_area:
            # Extract the region of interest (ROI) corresponding to the license plate
            img_roi = img[y: y + h, x: x + w]

            # Save the scanned image with a unique file name
            file_name = "images/scanned_img_" + str(count) + ".jpg"
            cv2.imwrite(file_name, img_roi)

            # Display the file name
            print("Saved:", file_name)

            # Extract text using Tesseract
            text = pytesseract.image_to_string(file_name)
            print("Text extracted from the image:")
            print(text)

            count += 1

            # Set the flag to end the loop
            process_image = False  # Line to break while loop

            break  # Line to break for loop

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()

# End
print("End of script")
