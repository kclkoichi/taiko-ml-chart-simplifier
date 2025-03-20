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
            # Read first 50 bytes, enough for reading title which is indicative of encoding
            raw_data = file.read(50)
            result = chardet.detect(raw_data)
            return result['encoding']

    def extract_metadata(self, file_content):
        """Extract metadata lines before first 'COURSE' line"""
        metadata_lines = []
        for line in file_content.strip().split('\n'):
            if line.startswith('COURSE'):
                break
            metadata_lines.append(line)
        return '\n'.join(metadata_lines)

    def split_difficulties(self, file_content):
        """Split file content into a file for each difficulty"""
        difficulties = re.split(r'COURSE:', file_content)[1:]
        difficulty_dict = {}

        for difficulty in difficulties:
            lines = difficulty.strip().split('\n')
            name = lines[0].strip()
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
                else:
                    print(f"{filename} ignored")
