import re
import os
import chardet

class TjaFileSlicer:
    def __init__(self, raw_data_dir, preprocessed_data_dir):
        self.raw_data_dir = raw_data_dir
        self.preprocessed_data_dir = preprocessed_data_dir

        # Ensure directory exist
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.preprocessed_data_dir, exist_ok=True)

    def detect_encoding(self, filepath):
        """Detect file encoding using chardet"""
        with open(filepath, 'rb') as file:
            # Read first 200 bytes, enough for reading title which is indicative of encoding (also needed subtitle so increased from 50 to 100)
            raw_data = file.read(200)
            result = chardet.detect(raw_data)
            return result['encoding']
        
    # For some reason, some people (luigi.) put level with the metadata.
    # So I need a way to still be able to preprocess
    keep_level = -1

    def extract_metadata(self, file_content):
        """Extract metadata lines before first 'COURSE' line"""
        metadata_lines = []
        for line in file_content.strip().split('\n'):
            if line.startswith('COURSE'):
                break
            if line.startswith('LEVEL'):
                self.keep_level = line.split(":")[1]
            else:
                metadata_lines.append(line)
        return '\n'.join(metadata_lines)

    def split_difficulties(self, file_content):
        """Split file content into a file for each difficulty"""
        difficulties = re.split(r'COURSE:', file_content)[1:]
        difficulty_dict = {}

        for difficulty in difficulties:
            lines = difficulty.strip().split('\n')
            name = lines[0].strip()
            lines[0] = "COURSE:" + name # Keep COURSE: in COURSE:Easy etc
            if name == "Oni" and self.keep_level != -1:
                lines.insert(1, f"LEVEL:{self.keep_level}")
            difficulty_dict[name] = '\n'.join(lines)

        return difficulty_dict

    def save_file(self, foldername, filename, content):
        """Saves content inside song's folder with UTF-8 encoding"""
        song_folder = os.path.join(self.preprocessed_data_dir, foldername)
        os.makedirs(song_folder, exist_ok=True)  # Ensure the song's folder exists
        filepath = os.path.join(song_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {filepath}")

    def process_files(self):
        count = 0

        """Recursively process all .tja files in raw_data_dir and subdirectories"""
        for root, _, files in os.walk(self.raw_data_dir):  # Recursively search files
            for filename in files:
                if filename.endswith(".tja"):
                    input_filepath = os.path.join(root, filename)

                    # Create song folder inside preprocessed_data_dir
                    song_name = os.path.splitext(filename)[0]  # Remove .tja extension

                    # Detect encoding and read the file
                    encoding = self.detect_encoding(input_filepath)
                    print(f"Detected encoding for {filename}: {encoding}")

                    with open(input_filepath, 'r', encoding=encoding) as file:
                        file_content = file.read()

                    # Extract and save metadata
                    self.save_file(song_name, "metadata.txt", self.extract_metadata(file_content))

                    # Extract and save difficulties
                    difficulty_dict = self.split_difficulties(file_content)
                    for difficulty_name, content in difficulty_dict.items():
                        self.save_file(song_name, f"{difficulty_name}.txt", content)
                    count += 1
                else:
                    print(f"{filename} ignored")
        print(f"Processed {count} .tja files")
