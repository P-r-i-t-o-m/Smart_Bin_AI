import joblib
import serial
import csv
import time
import numpy as np
import os
import pandas as pd  # Import pandas for CSV file operations

# Load pre-trained ML model (replace with your model file path)
model, trained_moisture_levels = joblib.load('waste_classifier_model.pkl')

# Set up the serial connection (ensure the correct COM port is used)
arduino = serial.Serial('COM3', 9600)  # Change COM3 to the correct port for your Arduino

# File path for the CSV file
csv_file_path = 'waste_data.csv'

# Load existing CSV data into a pandas DataFrame, if the file exists
if os.path.exists(csv_file_path):
    data = pd.read_csv(csv_file_path)
else:
    # Create an empty DataFrame with the necessary columns if the file does not exist
    data = pd.DataFrame(columns=['Date', 'Time', 'Predicted Waste Type', 'Moisture Level', 'Moisture Match Status'])

# Function to check if a moisture level matches any previous entries
def check_moisture_status(moisture_level, data):
    if moisture_level == 0:  # No moisture detected
        return "No Moisture Detected"
    elif moisture_level in data['Moisture Level'].values:
        return "Moisture Level Matched"
    else:
        return "New Moisture Level"

# Open or create the CSV file to log the data
with open(csv_file_path, 'a', newline='') as csvfile:  # Open in append mode ('a') to avoid overwriting
    csvwriter = csv.writer(csvfile)

    # Write the header if the file is new (i.e., doesn't already exist)
    if data.empty:  # If the DataFrame is empty, it means the file is new
        csvwriter.writerow(['Date', 'Time', 'Predicted Waste Type', 'Moisture Level', 'Moisture Match Status'])
        csvfile.flush()  # Ensure the header is written immediately

    while True:
        try:
            # Read a line from the serial input
            line = arduino.readline().decode('utf-8').strip()
            print(f"Received: {line}")  # Debugging print to see what is received

            # Check if the line contains the expected comma-separated values
            if ',' in line:
                try:
                    # Split the line into organic, inorganic, and moisture values
                    organic, inorganic, moisture_level = line.split(',')

                    # Ensure that moisture level is properly converted to an integer
                    moisture_level = int(moisture_level)

                    # Use the ML model to predict waste type (organic/inorganic)
                    features = np.array([[moisture_level]])
                    predicted_waste_type = model.predict(features)[0]  # 'Organic' or 'Inorganic'

                    # Get the current date and time
                    current_date = time.strftime('%Y-%m-%d')  # Extract date
                    current_time = time.strftime('%H:%M:%S')  # Extract time

                    # Determine the moisture match status using pandas DataFrame
                    moisture_status = check_moisture_status(moisture_level, data)

                    # Log the new data entry in the CSV file
                    csvwriter.writerow([current_date, current_time, predicted_waste_type, moisture_level, moisture_status])

                    # Update the DataFrame with the new entry
                    new_row = {
                        'Date': current_date,
                        'Time': current_time,
                        'Predicted Waste Type': predicted_waste_type,
                        'Moisture Level': moisture_level,
                        'Moisture Match Status': moisture_status
                    }
                    data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

                    # Flush the file to ensure data is written immediately
                    csvfile.flush()

                    # Display the logged information in the console
                    print(f"Logged: {current_date} {current_time}, Predicted Waste Type: {predicted_waste_type}, "
                          f"Moisture Level: {moisture_level}, Status: {moisture_status}")

                except ValueError:
                    # Handle cases where the data cannot be split or converted correctly
                    print(f"Error: Unable to process the line: {line}")
            else:
                print(f"Unexpected data format: {line}")

        except Exception as e:
            print(f"Error: {e}")