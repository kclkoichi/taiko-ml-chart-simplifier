import re
import os
import chardet

# Define base directories
project_code_dir = os.path.dirname(os.path.dirname(__file__))  # Go back one level to the root of the project
raw_data_dir = os.path.join(project_code_dir, "raw_data")
preprocessed_data_dir = os.path.join(project_code_dir, "preprocessed_data")

def detect_encoding(filepath):
    """
        Detects the file encoding using chardet
    """
    with open(filepath, 'rb') as file:
        raw_data = file.read(50)  # Read the first 50 bytes is enough cause title is what gives indication of encoding 
        result = chardet.detect(raw_data)
        return result['encoding']

def extract_metadata(file_content):
    """
        Extract metadata lines before the first 'COURSE' line
        Note: Metadata applies for all difficulties
    """
    metadata_lines = []
    for line in file_content.strip().split('\n'):
        if line.startswith('COURSE'):
            break
        metadata_lines.append(line)
    return '\n'.join(metadata_lines)

def split_difficulties(file_content):
    """
        Split the file content into a file for each difficulty
    """
    difficulties = re.split(r'COURSE:', file_content)[1:]
    difficulty_dict = {}
    
    for difficulty in difficulties:
        lines = difficulty.strip().split('\n')
        name = lines[0].strip()
        difficulty_dict[name] = '\n'.join(lines)
    
    return difficulty_dict

def save_file(filepath, content):
    """
        Saves content to a file with UTF-8 encoding, ensuring directories exist
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {filepath}")

# Process all .tja files in raw_data
for filename in os.listdir(raw_data_dir):
    if filename.endswith(".tja"):
        song_name = os.path.splitext(filename)[0]  # Remove .tja extension
        input_filepath = os.path.join(raw_data_dir, filename)
        song_output_dir = os.path.join(preprocessed_data_dir, song_name)
        
        # Detect the file encoding and read the file
        encoding = detect_encoding(input_filepath)
        print(f"Detected encoding for {filename}: {encoding}")
        
        with open(input_filepath, 'r', encoding=encoding) as file:
            file_content = file.read()

        # Extract and save metadata
        metadata_content = extract_metadata(file_content)
        save_file(os.path.join(song_output_dir, "metadata.txt"), metadata_content)

        # Extract and save difficulties
        difficulty_dict = split_difficulties(file_content)
        for difficulty_name, content in difficulty_dict.items():
            save_file(os.path.join(song_output_dir, f"{difficulty_name}.txt"), content)
