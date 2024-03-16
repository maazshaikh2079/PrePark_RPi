import pytesseract

text = pytesseract.image_to_string("images/scanned_img_1.jpg")
print("Text extracted from the image:")
print(text)
