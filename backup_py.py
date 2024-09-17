import os
from datetime import datetime

def backup_py_files():
    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create/open the backup text file
    with open("backup_py.txt", "w") as backup_file:
        # Write the current date at the top
        backup_file.write(f"Date: {current_date}\n\n")
        
        # Iterate over all files in the current directory
        for filename in os.listdir('.'):
            # Check if the file is a Python file
            if filename.endswith(".py"):
                # Write the filename
                backup_file.write(f"{filename}:\n")
                
                # Open and write the contents of the Python file
                with open(filename, "r") as py_file:
                    code = py_file.read()
                    backup_file.write(code)
                    backup_file.write("\n\n")  # Add some spacing between files

    print("Backup complete! All Python files have been saved to backup_py.txt.")

# Run the function to create the backup
backup_py_files()
