import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR/tesseract.exe'


def return_text(img):
    text = pytesseract.image_to_string(img)
    return text
