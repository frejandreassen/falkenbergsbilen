import streamlit as st
from pyzbar.pyzbar import decode
import cv2
from PIL import Image
import numpy as np

st.title('Barcode Scanner')

uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    st.write("")

    # Convert the image to grayscale
    img_array = np.array(image)
    gray_img = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # Decode the barcode
    decoded_objects = decode(gray_img)

    if len(decoded_objects) == 0:
        st.write("No barcode detected!")
    else:
        for obj in decoded_objects:
            st.write("Type:", obj.type)
            st.write("Data:", obj.data.decode('utf-8'))
