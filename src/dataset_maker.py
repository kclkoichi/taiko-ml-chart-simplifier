import os
import numpy as np

# Define directories
project_code_dir = os.path.dirname(os.path.dirname(__file__))  # Go back one level to the root of the project
preprocessed_data_dir = os.path.join(project_code_dir, "preprocessed_data")
datasets_dir = os.path.join(project_code_dir, "datasets")  # Define the datasets folder

# Ensure the datasets directory exists
os.makedirs(datasets_dir, exist_ok=True)

# Define a function to read a song file and extract the chart lines
def extract_lines_from_file(filepath):
    """
        Extract lines from a given chart file
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read().strip().split('\n')
    
def process_lines(lines):
    """
        Only keep lines with notes, removing comments and unwanted lines.
    """
    processed_lines = []
    
    # Patterns to ignore (metadata specific to each difficulty)
    ignore_patterns = ["Easy", "Normal", "Hard", "Oni", "Edit", "LEVEL", "BALLOON", "SCOREINIT", "SCOREDIFF"]
    
    for line in lines:
        # Skip empty lines and commands
        if not line or line.startswith('#'):
            continue
        # Skip difficulty specific metadata
        if any(line.startswith(pattern) for pattern in ignore_patterns):
            continue
        # If we are here, then it's a line with notes
        line = line.replace(',', '')  # Remove commas
        # Remove any comments at the end of the line (if exists)
        if "//" in line:
            line = line.split("//")[0].strip()

        processed_lines.append(line)
    
    return processed_lines

# Define a function to process all songs and save the chart lines
def process_songs():
    # Dictionary to store the lines for each difficulty
    # Note: We skip Edit even if it exists
    difficulty_lines = {
        'Easy': [],
        'Normal': [],
        'Hard': [],
        'Oni': []
    }
    
    # Iterate through all songs in the preprocessed_data directory
    for song_folder in os.listdir(preprocessed_data_dir):
        song_folder_path = os.path.join(preprocessed_data_dir, song_folder)
        
        if os.path.isdir(song_folder_path):
            # For each difficulty, load the corresponding chart file and extract the lines
            for difficulty in difficulty_lines.keys():
                difficulty_file = os.path.join(song_folder_path, f"{difficulty}.txt")
                
                if os.path.exists(difficulty_file):
                    lines = extract_lines_from_file(difficulty_file)
                    processed_lines = process_lines(lines)
                    difficulty_lines[difficulty].extend(processed_lines)

    # Convert the lists of lines for each difficulty into numpy arrays and save them
    for difficulty, lines in difficulty_lines.items():
        # print(lines) # Seems to be working
        # Save the data in the datasets directory
        np.save(os.path.join(datasets_dir, f"{difficulty}.npy"), np.array(lines))
        print(f"Saved {difficulty}.npy with {len(lines)} lines.")

    # Final verification to check each difficulty has same number of lines
    # Maybe useless cause anyway we print number of lines before
    expected_length = len(difficulty_lines["Easy"])
    for difficulty, lines in difficulty_lines.items():
        if len(lines) != expected_length:
                print(f"Warning: {difficulty} has length mismatch")
                print(f"Expected length: {expected_length}, Found length: {len(lines)}")
                break

# Run the function to process the songs and save the datasets
process_songs()
