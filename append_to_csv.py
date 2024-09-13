def append_to_csv(log_file, conversation_type, message):
    with open(log_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Read the file to find the last used ID
        with open(log_file, mode='r', newline='', encoding='utf-8') as readfile:
            lines = list(csv.reader(readfile))
            last_id = int(lines[-1][0]) if len(lines) > 1 else 0
        
        # Append the new line with an incremented ID
        writer.writerow([f"{last_id + 1:04d}", conversation_type, message])
