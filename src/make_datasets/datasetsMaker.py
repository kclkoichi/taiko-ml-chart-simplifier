import os
import numpy as np

class DatasetsMaker:
    """
    Only processes the following 4 difficulties (ignores any other):
    Oni, Hard, Normal, Easy
    """

    def __init__(self, preprocessed_data_dir, datasets_dir):
        """
        Initialise DatasetsMaker with specified directories
        """
        self.preprocessed_data_dir = preprocessed_data_dir
        self.datasets_dir = datasets_dir

        # Ensure directory exist
        os.makedirs(self.preprocessed_data_dir, exist_ok=True)
        os.makedirs(self.datasets_dir, exist_ok=True)

    def extract_lines_from_file(self, filepath):
        """
        Extracts lines from a given chart file.
        """
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read().strip().split('\n')

    def process_lines(self, lines):
        """
        Filters out metadata, comments, and commands (starting with #)
        Only includes lines between #START and #END (so the notes)
        """
        processed_lines = []
        inside_chart = False  # Flag to track when we are inside #START and #END

        for line in lines:
            line = line.strip()

            if line == "#START":
                inside_chart = True
                continue
            
            if line == "#END":
                inside_chart = False
                continue

            if inside_chart:
                if not line or line.startswith('#'):
                    continue
                if "//" in line:
                    line = line.split("//")[0].strip()
                line = line.replace(',', '')
                line = line.replace(' ', '')
                processed_lines.append(line)

        return processed_lines

    def process_songs(self):
        """
        Processes all songs and saves the chart lines into datasets.

        """
        difficulty_lines = {'Easy': [], 'Normal': [], 'Hard': [], 'Oni': []}

        for song_folder in os.listdir(self.preprocessed_data_dir):
            song_folder_path = os.path.join(self.preprocessed_data_dir, song_folder)

            if os.path.isdir(song_folder_path):
                # Skip songs lacking a difficulty
                missing_difficulties = [d for d in difficulty_lines if not os.path.exists(os.path.join(song_folder_path, f"{d}.txt"))]
                if missing_difficulties:
                    print(f"Skipping {song_folder} (missing difficulties: {', '.join(missing_difficulties)})")
                    continue

                # Skip songs which doens't have same line count for every difficulty
                # Note: This is due to oni charts having different 2nd player chart,
                # and some more BPMCHANGE (e.g: FUJIN RUMBLE)
                # TODO (maybe?): Process these files. Have enough data to skip them though...
                processed_song_lines = {}
                for difficulty in difficulty_lines.keys():
                    lines = self.extract_lines_from_file(os.path.join(song_folder_path, f"{difficulty}.txt"))
                    processed_song_lines[difficulty] = self.process_lines(lines)
                difficulty_lengths = {d: len(lines) for d, lines in processed_song_lines.items()}
                if len(set(difficulty_lengths.values())) > 1:
                    print(f"Skipping {song_folder} (line count mismatch): {difficulty_lengths}")
                    continue
                
                # Have all 4 difficulties and all have same number of lines, so add data
                for difficulty, lines in processed_song_lines.items():
                    difficulty_lines[difficulty].extend(lines)
                print(f"Added {song_folder}")

        # Save each dataset
        for difficulty, lines in difficulty_lines.items():
            np.save(os.path.join(self.datasets_dir, f"{difficulty}.npy"), np.array(lines))
            print(f"Saved {difficulty}.npy with {len(lines)} lines.")

        # Extra validation to make sure every difficulty dataset has same line count
        expected_length = len(difficulty_lines["Easy"])
        for difficulty, lines in difficulty_lines.items():
            if len(lines) != expected_length:
                print(f"Warning: {difficulty} has length mismatch (Expected: {expected_length}, Found: {len(lines)})")
                break
