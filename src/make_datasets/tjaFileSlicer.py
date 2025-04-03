import re
import os
import sys
import chardet

class TjaFileSlicer:
    def __init__(self, preprocessed_data_dir):
        self.preprocessed_data_dir = preprocessed_data_dir

        # Ensure directory exist
        os.makedirs(self.preprocessed_data_dir, exist_ok=True)

    def detect_encoding(self, filepath):
        """Detect file encoding using chardet"""
        with open(filepath, 'rb') as file:
            # Read first 200 bytes, enough for reading title which is indicative of encoding 
            # (also needed subtitle so increased from 50 to 100, to 200)
            raw_data = file.read(200)
            result = chardet.detect(raw_data)
            return result['encoding']

    def extract_metadata(self, file_content):
        """Extract metadata lines before first COURSE line"""
        metadata_lines = []
        for line in file_content.strip().split('\n'):
            if line.startswith('COURSE'):
                break
            if line.startswith('LEVEL'):
                self.keep_level = line.split(":")[1]
            else:
                metadata_lines.append(line)
        return '\n'.join(metadata_lines)
    
    # For some reason, some people (luigi.) put level with the metadata.
    # So I need a way to still be able to preprocess...
    # Note: This only deals with the case of Oni in metadata, while Edit also exists later
    # Like designant. by Luigi. https://www.youtube.com/watch?v=3pCEbT5ryy0
    # TODO: Also place this fix in fix_tja_file.py
    keep_level = -1

    def split_difficulties(self, file_content):
        """Split file content into a file for each difficulty"""
        difficulties = re.split(r'COURSE:', file_content)[1:]
        difficulty_dict = {}

        for difficulty in difficulties:
            lines = difficulty.strip().split('\n')
            # Keep difficulty name (Easy) in COURSE:Easy etc
            name = lines[0].strip()
            lines[0] = "COURSE:" + name
            if name == "Oni" and self.keep_level != -1:
                # The processed chart has LEVEL inside metadata for the 1st chart
                # Insert it after lines[0] (which is COURSE:Oni)
                lines.insert(1, f"LEVEL:{self.keep_level}")
            difficulty_dict[name] = '\n'.join(lines)

        return difficulty_dict

    def save_file(self, foldername, filename, content):
        """Saves content inside song's folder with UTF-8 encoding"""
        song_folder = os.path.join(self.preprocessed_data_dir, foldername)
        os.makedirs(song_folder, exist_ok=True)  # Ensure song_folder exists
        filepath = os.path.join(song_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def process_files(self, raw_data_dir):
        # Ensure directory exist
        os.makedirs(raw_data_dir, exist_ok=True)

        for root, _, files in os.walk(raw_data_dir):
            for filename in files:
                if filename.endswith(".tja"):
                    input_file_path = os.path.join(root, filename)
                    self.process_unique_file(input_file_path)

    def process_unique_file(self, input_file_path):
        filename = os.path.basename(input_file_path)
        if filename.endswith(".tja"):
            song_name = os.path.splitext(filename)[0] # Remove .tja extension

            # Detect encoding and read the file
            encoding = self.detect_encoding(input_file_path)
            with open(input_file_path, 'r', encoding=encoding) as file:
                file_content = file.read()

            # Extract and save metadata
            self.save_file(song_name, "metadata.txt", self.extract_metadata(file_content))

            # Extract and save difficulties
            difficulty_dict = self.split_difficulties(file_content)
            for difficulty_name, content in difficulty_dict.items():
                self.save_file(song_name, f"{difficulty_name}.txt", content)
        else:
            print(f"Not a .tja file: {filename}")
            sys.exit(0)
