from google.cloud import datastore
from google.oauth2 import service_account
from datetime import datetime
import pandas as pd
import streamlit as st
from PyPDF2 import PdfReader
from pyzbar.pyzbar import decode
import cv2
import numpy as np
from PIL import Image

# Initialize Datastore client with credentials
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
client = datastore.Client(credentials=credentials)

# Function to add new receipt to Firestore Datastore
def add_receipt(rnr):
    # Check if the rnr already exists
    query = client.query(kind='Receipts')
    query.add_filter('rnr', '=', rnr)
    results = list(query.fetch())
    
    if len(results) == 0:
        key = client.key('Receipts')
        entity = datastore.Entity(key=key)
        created_date = datetime.now()
        entity.update({
            'rnr': rnr,
            'created_date': created_date,
            'isChecked': False,
            'checkedDate': None
        })
        client.put(entity)
    else:
        pass

def check_receipt(rnr, new_isChecked_state):
    # Query to find the receipt with the given rnr
    query = client.query(kind='Receipts')
    query.add_filter('rnr', '=', rnr)
    results = list(query.fetch())
    
    # If the receipt exists, update its isChecked and checkedDate fields
    if len(results) > 0:
        receipt = results[0]
        receipt['isChecked'] = new_isChecked_state
        receipt['checkedDate'] = datetime.now() if new_isChecked_state else None
        client.put(receipt)


# Function to fetch all receipts from Firestore Datastore
def get_all_receipts():
    query = client.query(kind='Receipts')
    results = list(query.fetch())
    return pd.DataFrame(results)
    
# Streamlit UI
st.title("Reference Number and PDF Scanner")

# Manually enter RNR or upload an image to auto-populate the RNR field
uploaded_image = st.file_uploader("Or upload an image to scan for RNR", type=["jpg", "jpeg", "png"])

if uploaded_image:
    # Convert uploaded image to grayscale and scan for barcodes
    image = Image.open(uploaded_image)
    img_array = np.array(image)
    gray_img = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    decoded_objects = decode(gray_img)
    
    if len(decoded_objects) > 0:
        scanned_rnr = decoded_objects[0].data.decode('utf-8')
    else:
        scanned_rnr = "No barcode detected"

    # Auto-populate the RNR field
    dummy_number = st.text_input("Enter Reference Number", value=scanned_rnr)
else:
    dummy_number = st.text_input("Enter Reference Number")

# Add RNR
if st.button("Add Reference Number"):
    add_receipt(dummy_number)
    st.write(f"Reference Number {dummy_number} added.")

with st.sidebar:
    # Upload PDF
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf_file:
        reader = PdfReader(pdf_file)
        text = ""
        for i in range(len(reader.pages)):
            text += reader.pages[i].extract_text()
        print(text)
        # Fetch all unchecked receipts and check if any reference number is in the PDF
        df = get_all_receipts()
        unchecked_df = df[df['isChecked'] == False]
        
        for _, row in unchecked_df.iterrows():
            if str(row['rnr']) in text:
                # Mark the receipt as checked
                check_receipt(row['rnr'], True)
                st.write(f"Reference Number {row['rnr']} found in PDF and marked as checked!")


    # Dropdown to filter based on isChecked status
    filter_option = st.selectbox("Filter by:", ["Unchecked", "All", "Checked"])

# Fetch and filter data
df = get_all_receipts()

# Convert created_date to datetime format and then to yyyy-mm-dd string format
df['created_date'] = pd.to_datetime(df['created_date'])
df['created_date_str'] = df['created_date'].dt.strftime('%Y-%m-%d')


# Filter based on isChecked status
if filter_option == "Checked":
    df = df[df['isChecked'] == True]
elif filter_option == "Unchecked":
    df = df[df['isChecked'] == False]

# Sort by created_date
df = df.sort_values(by='created_date', ascending=False)

st.header("Referensnummer")
# Checklist of reference numbers along with created_date
for index, row in df.iterrows():
    checked = st.checkbox(f"{row['rnr']} | Skapad datum: {row['created_date_str']}", value=row['isChecked'])
    if checked != row['isChecked']:
        # Update Firestore Datastore
        check_receipt(row['rnr'], checked)
        st.experimental_rerun()