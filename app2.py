# Importing Streamlit for the web app interface
import streamlit as st
from google.cloud import datastore
from google.oauth2 import service_account
from datetime import datetime

# Create a credentials object using the service account info from the secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# Initialize the Datastore client
client = datastore.Client(credentials=credentials)

def add_receipt(rnr):
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

def get_receipt_by_rnr(rnr):
    query = client.query(kind='Receipts')
    query.add_filter('rnr', '=', rnr)
    results = list(query.fetch())
    return results


# Function to simulate the main layout and sidebar
def main():
    st.title("Truck Receipt Validator")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    selected_option = st.sidebar.selectbox("Choose a page", ["Home", "Receipt Registration", "Upload Summary", "Validation Summary"])
    
    st.sidebar.title("User Actions")
    st.sidebar.button("Login")
    st.sidebar.button("Logout")

    # Dummy function to simulate Receipt Registration
    def receipt_registration():
        st.header("Receipt Registration")
        st.write("Here you can register new receipts by scanning or manually entering the RNR and metadata.")

        # Input fields for RNR and metadata
        rnr = st.text_input("Enter the Registration Number (RNR)")

        # Submit button to save data
        if st.button("Submit"):
            # Save to Firestore Datastore
            add_receipt(rnr)
            st.success("Receipt successfully registered.")

    # Dummy function to simulate Upload Summary
    def upload_summary():
        st.header("Upload Summary")
        st.write("Here you can upload the PDF summary to validate against registered receipts.")
    
    # Dummy function to simulate Validation Summary
    def validation_summary():
        st.header("Validation Summary")
        st.write("Here you can see the summary of all validated and unvalidated receipts.")
    
    # Main area based on sidebar selection
    if selected_option == "Home":
        st.header("Home")
        st.write("Welcome to the Truck Receipt Validator app. Please navigate using the sidebar.")
    elif selected_option == "Receipt Registration":
        receipt_registration()
    elif selected_option == "Upload Summary":
        upload_summary()
    elif selected_option == "Validation Summary":
        validation_summary()

# Call the main function to run the Streamlit app
main()
