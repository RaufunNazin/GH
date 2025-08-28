from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
import json
import os

app = Flask(__name__)
CORS(app)

# Global variable to store the data
hall_data = None
contact_status = {}  # Dictionary to track contact status

def load_excel_data():
    """Load data from Excel file and convert to JSON format"""
    global hall_data
    try:
        excel_file = "Emails Latest (1).xlsx"
        if os.path.exists(excel_file):
            # Read Excel file
            df = pd.read_excel(excel_file)
            
            # Define the fields to keep
            fields_to_keep = [
                'Contact', 'Department', 'Email', 'Hall Name', 'Name', 'Year'
            ]
            
            # Filter columns to only keep the specified fields
            available_fields = [col for col in fields_to_keep if col in df.columns]
            if available_fields:
                df = df[available_fields]
                print(f"Filtered to keep only these fields: {available_fields}")
            else:
                print("Warning: None of the specified fields found in the Excel file")
                print(f"Available columns: {list(df.columns)}")
            
            # Convert all datetime/timestamp columns to strings
            for col in df.columns:
                if df[col].dtype == 'datetime64[ns]' or 'datetime' in str(df[col].dtype):
                    df[col] = df[col].astype(str)
                # Also handle any other non-serializable types
                df[col] = df[col].apply(lambda x: str(x) if pd.isna(x) == False else None)
            
            # Convert to list of dictionaries
            hall_data = df.to_dict('records')
            
            # Save as JSON for easier access
            with open('hall_data.json', 'w', encoding='utf-8') as f:
                json.dump(hall_data, f, ensure_ascii=False, indent=2)
            
            # Load existing contact status if available
            load_contact_status()
            
            print(f"Loaded {len(hall_data)} records from Excel file")
            return True
        else:
            print(f"Excel file '{excel_file}' not found")
            return False
    except Exception as e:
        print(f"Error loading Excel file: {str(e)}")
        return False

def load_contact_status():
    """Load contact status from file"""
    global contact_status
    try:
        if os.path.exists('contact_status.json'):
            with open('contact_status.json', 'r', encoding='utf-8') as f:
                contact_status = json.load(f)
            print(f"Loaded contact status for {len(contact_status)} records")
        else:
            contact_status = {}
    except Exception as e:
        print(f"Error loading contact status: {str(e)}")
        contact_status = {}

def save_contact_status():
    """Save contact status to file"""
    try:
        with open('contact_status.json', 'w', encoding='utf-8') as f:
            json.dump(contact_status, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving contact status: {str(e)}")

def get_record_id(record):
    """Generate a unique ID for a record based on key fields"""
    return f"{record.get('Name', '')}_{record.get('Contact', '')}_{record.get('Email', '')}"

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """Get all hall data"""
    if hall_data is None:
        return jsonify({'error': 'Data not loaded'}), 500
    return jsonify(hall_data)

@app.route('/api/search')
def search_data():
    """Search hall data by hall name or department name"""
    if hall_data is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify(hall_data)
    
    # Search in all string fields (case-insensitive)
    results = []
    for record in hall_data:
        for key, value in record.items():
            if isinstance(value, str) and query in str(value).lower():
                results.append(record)
                break
    
    return jsonify(results)

@app.route('/api/columns')
def get_columns():
    """Get column names from the data"""
    if hall_data is None or len(hall_data) == 0:
        return jsonify({'error': 'Data not loaded'}), 500
    
    columns = list(hall_data[0].keys())
    return jsonify(columns)

@app.route('/api/contact-status', methods=['POST'])
def update_contact_status():
    """Update contact status for a record"""
    try:
        data = request.get_json()
        record_id = data.get('record_id')
        status = data.get('status')  # 'contacted' or 'not_contacted'
        
        if not record_id or status not in ['contacted', 'not_contacted']:
            return jsonify({'error': 'Invalid data'}), 400
        
        contact_status[record_id] = status
        save_contact_status()
        
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact-status/<record_id>')
def get_contact_status(record_id):
    """Get contact status for a specific record"""
    status = contact_status.get(record_id, 'not_contacted')
    return jsonify({'status': status})

if __name__ == '__main__':
    # Load data on startup
    if load_excel_data():
        print("Data loaded successfully!")
    else:
        print("Failed to load data!")
    
    # Use environment variable for port (required for deployment platforms)
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
