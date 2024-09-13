import os
import csv

def create_new_log_file():
    log_folder = './logs'
    
    # Check if the logs folder exists, create it if not
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # Find the next available filename in the format chatlog0001.csv
    i = 1
    while os.path.exists(f"{log_folder}/chatlog{i:04d}.csv"):
        i += 1
    
    # Create the new log file
    log_file = f"{log_folder}/chatlog{i:04d}.csv"
    
    # Write the header for the new CSV file
    with open(log_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Conversation", "Message"])  # Header row
    
    return log_file
