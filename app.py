from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import json

app = Flask(__name__)

# Define your Google Sheet ID
SPREADSHEET_ID = '1oqfsCsFxC2MOUAVxoErtMdwbM7UgP10IkBw78fL7FIc'  # Replace with your actual spreadsheet ID
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Path to your local Excel file containing store codes
EXCEL_FILE_PATH = 'C:\\Users\\yassine\\Desktop\\flask_gps_tracker\\scratch\\storecodes.xlsx'

# Function to read store codes from the local Excel file and filter based on employee code
def get_store_codes(employee_code=None):
    df = pd.read_excel(EXCEL_FILE_PATH)
    df.columns = df.columns.str.strip()  # Clean up any spaces in column names
    if employee_code:
        # Filter the data by employee code if provided
        filtered_df = df[df['Employee Code'] == employee_code]
        store_codes = filtered_df['Store Code'].tolist()  # Get store codes as a list
    else:
        # Return all store codes if no employee code is specified
        store_codes = df['Store Code'].tolist()
    return store_codes

# Function to initialize Google Sheets client using environment variable
def init_google_sheets():
    # Load the JSON from the environment variable
    service_account_json = os.getenv("SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        raise ValueError("SERVICE_ACCOUNT_JSON environment variable not found")

    # Parse the JSON string
    service_account_data = json.loads(service_account_json)

    # Use the parsed JSON to create credentials
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_data, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # Access the first sheet
    return sheet

@app.route('/')
def index():
    # Initially, show all store codes in the dropdown
    store_codes = get_store_codes()
    return render_template('3awdas_waha.html', store_codes=store_codes)

@app.route('/get_stores', methods=['GET'])
def get_stores():
    # Get the employee code from the request
    employee_code = request.args.get('empCode')
    if employee_code:
        store_codes = get_store_codes(employee_code)
        return jsonify(store_codes)
    else:
        return jsonify({"error": "Employee code not provided"}), 400

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Extract form data
        emp_code = request.form['empCode']
        store_code = request.form['storeCode']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        # Initialize Google Sheets and append the data to the sheet
        sheet = init_google_sheets()
        sheet.append_row([emp_code, store_code, latitude, longitude])
        return 'donnes enregistre'
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Failed to save data."}), 500

if __name__ == '__main__':
    app.run(debug=True)
