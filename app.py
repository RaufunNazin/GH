import streamlit as st
import pandas as pd
import json
import os
import time

# --- Configuration ---
EXCEL_FILE = "Emails Latest (1).xlsx"
STATUS_FILE = 'contact_status.json'
RECORDS_PER_PAGE = 25 # Number of records to display per page

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

# Custom CSS to enforce a clean, white-based theme
st.markdown("""
<style>
    /* Force white background on the main app container */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
    }

    /* Ensure all text is black for readability */
    body, .stApp, h1, h2, h3, h4, h5, h6, .stMarkdown, p, .st-emotion-cache-16txtl3, .st-emotion-cache-1jicfl2, .st-emotion-cache-1d9230i {
        color: #000000 !important;
    }
    
    /* Style input fields for the light theme */
    .stTextInput input {
        background-color: #F0F2F6 !important;
        color: #000000 !important;
        border: 1px solid #D0D0D0 !important;
    }
    
    /* Style placeholder text for the light theme */
    .stTextInput input::placeholder {
        color: #000000 !important;
        opacity: 0.7 !important;
    }
    
    /* Style buttons for the light theme */
    .stButton>button {
        background-color: #F0F2F6;
        color: #000000;
        border: 1px solid #D0D0D0;
    }
    .stButton>button:hover {
        background-color: #E0E0E0;
        border: 1px solid #C0C0C0;
    }

    /* Style separator lines */
    hr {
        background-color: #E0E0E0 !important;
    }
    
    /* Center and enlarge checkboxes */
    [data-testid="stCheckbox"] {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        margin-top: -10px; /* Adjust vertical alignment */
    }
    [data-testid="stCheckbox"] input {
        transform: scale(1.5);
        accent-color: #000000; /* Make the checkmark black */
    }
</style>
""", unsafe_allow_html=True)


st.title("Girls' Hall Contact Manager")
st.markdown("Search, view, and update contact information for the Girls' Hall directory.")

# Initialize session state variables
if 'hall_data' not in st.session_state:
    st.session_state.hall_data = load_excel_data()
    load_contact_status()
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# Main app logic starts here
if st.session_state.hall_data:
    # --- Search UI ---
    search_col1, search_col2 = st.columns([4, 1])
    with search_col1:
        search_input = st.text_input(
            "Search Directory",
            value=st.session_state.search_query,
            placeholder="Search by name, department, hall, etc.",
            key="search_box",
            label_visibility="collapsed"
        )
    with search_col2:
        search_button = st.button("Search", use_container_width=True)
    
    # Check for search changes from button or Enter key
    if search_button or (search_input != st.session_state.search_query):
        st.session_state.search_query = search_input
        st.session_state.page_number = 0 # Reset page number on new search
        st.toast("Applying search...")
        time.sleep(0.5) # Give user time to see the toast
        st.rerun()

    # --- Data Filtering Logic ---
    filtered_data = st.session_state.hall_data
    
    # Filter by search query
    if st.session_state.search_query:
        query = st.session_state.search_query.strip().lower()
        filtered_data = [
            record for record in filtered_data
            if any(query in str(value).lower() for value in record.values())
        ]

    # --- Pagination Logic ---
    total_records = len(filtered_data)
    total_pages = (total_records // RECORDS_PER_PAGE) + (1 if total_records % RECORDS_PER_PAGE > 0 else 0)
    start_idx = st.session_state.page_number * RECORDS_PER_PAGE
    end_idx = min(start_idx + RECORDS_PER_PAGE, total_records)
    
    paginated_data = filtered_data[start_idx:end_idx]

    # --- Display Results ---
    st.write(f"Displaying records {start_idx + 1}-{end_idx} of {total_records}.")

    if not paginated_data:
        st.warning("No records found matching your criteria.")
    else:
        # Create fixed header columns
        cols = st.columns([2, 2, 2, 1])
        headers = ['Name', 'Department / Hall', 'Contact Info', 'Contacted']
        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")
        st.markdown("---")

        # Create a scrollable container for the data rows
        with st.container(height=600):
            # Display each record
            for i, record in enumerate(paginated_data, start=start_idx):
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
                    is_contacted = st.session_state.contact_status.get(record_id, False)
                    unique_key = f"checkbox_{record_id}_{i}"
                    new_status = st.checkbox(" ", value=is_contacted, key=unique_key, label_visibility="collapsed")
                    
                    if new_status != is_contacted:
                        st.session_state.contact_status[record_id] = new_status
                        save_contact_status()
                        st.rerun()
                
                st.markdown("---")

    # --- Pagination Controls ---
    if total_pages > 1:
        st.markdown("---")
        nav_cols = st.columns([1, 1, 1])
        
        with nav_cols[0]:
            if st.session_state.page_number > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.page_number -= 1
                    st.rerun()
        
        with nav_cols[1]:
            st.write(f"Page {st.session_state.page_number + 1} of {total_pages}")
            
        with nav_cols[2]:
            if st.session_state.page_number < total_pages - 1:
                if st.button("Next ➡️"):
                    st.session_state.page_number += 1
                    st.rerun()

else:
    st.info("Waiting for data to be loaded. If this message persists, please check the application logs.")
