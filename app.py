import streamlit as st
import pandas as pd
import json
import os

# --- Configuration ---
EXCEL_FILE = "Emails Latest (1).xlsx"
STATUS_FILE = 'contact_status.json'

# --- Helper Functions ---

def get_record_id(record):
    """Generate a unique ID for a record based on key fields to prevent collisions."""
    # Using a tuple of sorted items makes the ID independent of column order
    key_items = sorted([str(v) for k, v in record.items() if k in ['Name', 'Contact', 'Email']])
    return "_".join(key_items)

# --- Data Loading and Caching ---

@st.cache_data
def load_excel_data():
    """Load data from Excel file, clean it, and return as a list of dictionaries."""
    try:
        if not os.path.exists(EXCEL_FILE):
            st.error(f"Error: The data file '{EXCEL_FILE}' was not found.")
            return None

        df = pd.read_excel(EXCEL_FILE)
        
        # Define the fields to keep for a clean dataset
        fields_to_keep = ['Contact', 'Department', 'Email', 'Hall Name', 'Name', 'Year']
        
        # Filter columns to only what's needed
        available_fields = [col for col in fields_to_keep if col in df.columns]
        df = df[available_fields]

        # Convert all columns to string to avoid serialization issues with JSON/Streamlit
        for col in df.columns:
            df[col] = df[col].astype(str).replace('nan', 'N/A')
        
        # Convert to list of dictionaries
        return df.to_dict('records')

    except Exception as e:
        st.error(f"An error occurred while loading the Excel file: {e}")
        return None

def load_contact_status():
    """Load contact status from the JSON file into the session state."""
    if 'contact_status' not in st.session_state:
        try:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                    st.session_state.contact_status = json.load(f)
            else:
                st.session_state.contact_status = {}
        except Exception as e:
            st.warning(f"Could not load contact status file: {e}")
            st.session_state.contact_status = {}

def save_contact_status():
    """Save the current contact status from the session state to the JSON file."""
    try:
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.contact_status, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Failed to save contact status: {e}")

# --- Streamlit App UI ---

# Set page configuration for a better layout
st.set_page_config(page_title="Girls' Hall Contact List", layout="wide")

st.title("Girls' Hall Contact Directory")
st.markdown("A simple app to search and manage contacts.")

# Load data into session state once to persist across reruns
if 'hall_data' not in st.session_state:
    st.session_state.hall_data = load_excel_data()
    load_contact_status()

# Main app logic starts here
if st.session_state.hall_data:
    # Create a search bar
    search_query = st.text_input("Search by any field (Name, Department, Hall, etc.)", placeholder="Type here to search...")

    # Filter data based on the search query
    if search_query:
        query = search_query.strip().lower()
        filtered_data = [
            record for record in st.session_state.hall_data
            if any(query in str(value).lower() for value in record.values())
        ]
    else:
        filtered_data = st.session_state.hall_data

    # Display the count of results
    st.write(f"Displaying {len(filtered_data)} of {len(st.session_state.hall_data)} records.")

    if not filtered_data:
        st.warning("No records found matching your search criteria.")
    else:
        # Create header columns for a clean layout
        cols = st.columns([2, 2, 2, 1]) # Adjust column widths as needed
        headers = ['Name', 'Department / Hall', 'Contact Info', 'Contacted']
        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")

        # Display each record in its own row
        for i, record in enumerate(filtered_data):
            record_id = get_record_id(record)
            
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

            with col1:
                st.markdown(f"**{record.get('Name', 'N/A')}**")
                st.caption(f"Year: {record.get('Year', 'N/A')}")
            
            with col2:
                st.markdown(f"**{record.get('Department', 'N/A')}**")
                st.caption(f"Hall: {record.get('Hall Name', 'N/A')}")
            
            with col3:
                st.markdown(f"**Email:** {record.get('Email', 'N/A')}")
                st.caption(f"Phone: {record.get('Contact', 'N/A')}")

            with col4:
                # Get the current status from session state
                is_contacted = st.session_state.contact_status.get(record_id, False)
                
                # Create a checkbox with a guaranteed unique key by including the index
                unique_key = f"checkbox_{record_id}_{i}"
                new_status = st.checkbox(" ", value=is_contacted, key=unique_key, label_visibility="collapsed")
                
                # If the checkbox state is changed by the user, update the session state and save
                if new_status != is_contacted:
                    st.session_state.contact_status[record_id] = new_status
                    save_contact_status()
                    st.rerun() # Rerun the script to immediately reflect the change
            
            st.markdown("---") # Add a visual separator between records
else:
    st.info("Waiting for data to be loaded. If this message persists, please check the application logs.")