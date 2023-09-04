import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract

# Streamlit UI
st.title("PDF OCR with Streamlit")

# Upload PDF file
pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if pdf_file:
    # Convert PDF to list of images
    images = convert_from_bytes(pdf_file.read())

    # Initialize text content variable for OCR
    ocr_text_content = ""

    # Loop through each image and use pytesseract for OCR
    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image)
        ocr_text_content += text

    # Show the first 500 characters to get an idea of the OCR output
    st.write("First 500 characters of the extracted text:")
    st.write(ocr_text_content[:500])
