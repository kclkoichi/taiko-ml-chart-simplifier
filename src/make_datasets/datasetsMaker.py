import os
import numpy as np

class DatasetsMaker:
    """
    Processes the following 5 difficulties (ignores any other, even if exist):
    Edit, Oni, Hard, Normal, Easy

    Creates the following datasets:
    Easy.npy
    Normal.npy
    Hard.npy
    Oni.npy or EditOni.npy

    Ignores files with STYLE:DOUBLE (2 player charts)
    Ignores files with #BRANCHSTART (branching charts)
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
        Extract non-empty lines from a given chart file, ignoring lines with only spaces.
        """
        with open(filepath, 'r', encoding='utf-8') as file:
            return [line for line in file.read().split('\n') if line.strip()]

    def process_lines(self, lines):
        """
        Filter out metadata, comments, and commands (starting with #)
        Only includes notes lines between #START and #END
        """
        processed_lines = []
        # Flag to track when we are inside #START and #END
        inside_chart = False

        for line in lines:
            line = line.strip()

            if line == "#START":
                inside_chart = True
                continue
            
            if line == "#END":
                inside_chart = False
                continue

            # Correctly only goes through note lines
            # (Empty non-note lines are ignored)
            if inside_chart:
                if not line or line.startswith('#'):
                    continue
                if "//" in line:
                    line = line.split("//")[0].strip()
                line = line.replace(',', '')
                line = line.replace(' ', '')
                processed_lines.append(line)

        return processed_lines

    def process_songs(self, hardest_difficulty = "Oni", selected_songs_file_path = None):
        """
        Note: Doesn't process 2P charts and branching charts.
        """
        difficulty_lines = {'Easy': [], 'Normal': [], 'Hard': [], hardest_difficulty: []}

        if selected_songs_file_path is not None and os.path.exists(selected_songs_file_path):
            with open(selected_songs_file_path, "r", encoding="utf-8") as f:
                selected_songs = set(
                    line.strip().removesuffix(".tja")
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                )

        for song_folder in os.listdir(self.preprocessed_data_dir):
            if selected_songs_file_path is not None and song_folder not in selected_songs:
                continue

            song_folder_path = os.path.join(self.preprocessed_data_dir, song_folder)

            if os.path.isdir(song_folder_path):
                # Skip songs lacking a difficulty
                missing_difficulties = [d for d in difficulty_lines if not os.path.exists(os.path.join(song_folder_path, f"{d}.txt"))]
                if missing_difficulties:
                    print(f"Skipping {song_folder} (missing difficulties: {', '.join(missing_difficulties)})")
                    continue

                processed_song_lines = {}

                skip_chart = False
                for difficulty in difficulty_lines.keys():
                    lines = self.extract_lines_from_file(os.path.join(song_folder_path, f"{difficulty}.txt"))
                    if "STYLE:DOUBLE" in lines:
                        print(f"Skipping {song_folder} (2 player chart)")
                        skip_chart = True
                        break
                    if any("#BRANCHSTART" in line for line in lines):
                        print(f"Skipping {song_folder} (branching chart)")
                        skip_chart = True
                        break

                    # Only keep notes lines
                    processed_song_lines[difficulty] = self.process_lines(lines)

                if skip_chart:
                    continue

                difficulty_lengths = {d: len(lines) for d, lines in processed_song_lines.items()}

                # TODO (maybe?): Process these files. Have enough data to skip them though...
                if len(set(difficulty_lengths.values())) > 1:
                    # Might happen when edit/oni had a lot of #SCROLL for faster effect...
                    # Example: FUJIN Rumble
                    # Won't do effort to collapse many lines into 1
                    print(f"Skipping {song_folder} (line count mismatch): {difficulty_lengths}")
                    continue
                
                # Have all 4 difficulties and all have same number of lines, so add data
                for difficulty, lines in processed_song_lines.items():
                    difficulty_lines[difficulty].extend(lines)
                print(f"Added {song_folder} ({hardest_difficulty})")

        return difficulty_lines
    
    def make_datasets(self):
        """
        Process all songs and save the chart lines into datasets.
        Note: Edit difficulty excluded
        """
        difficulty_lines = self.process_songs()

        # Extra validation to make sure every difficulty dataset has same line count
        expected_length = len(difficulty_lines["Oni"])
        for difficulty, lines in difficulty_lines.items():
            if len(lines) != expected_length:
                print(f"Warning: {difficulty} has length mismatch (Expected: {expected_length}, Found: {len(lines)})")
            else:
                print(f"{difficulty} has {len(lines)} lines (OK).")

        # Save each dataset
        for difficulty, lines in difficulty_lines.items():
            np.save(os.path.join(self.datasets_dir, f"{difficulty}.npy"), np.array(lines))
            print(f"Saved {difficulty}.npy with {len(lines)} lines.")

    def make_datasets_with_oni_and_edit(self, selected_edit_songs_file = None, selected_oni_songs_file = None):
        """
        Process all songs and save the chart lines into datasets.
        Note: Edit difficulty included
        """
        difficulty_lines = {
            "Easy": [],
            "Normal": [],
            "Hard": [],
            "EditOni": []
        }

        edit_difficulty_lines = self.process_songs("Edit", selected_edit_songs_file)
        oni_difficulty_lines = self.process_songs("Oni", selected_oni_songs_file)

        difficulty_lines["Easy"] = edit_difficulty_lines.get("Easy", []) + oni_difficulty_lines.get("Easy", [])
        difficulty_lines["Normal"] = edit_difficulty_lines.get("Normal", []) + oni_difficulty_lines.get("Normal", [])
        difficulty_lines["Hard"] = edit_difficulty_lines.get("Hard", []) + oni_difficulty_lines.get("Hard", [])
        difficulty_lines["EditOni"] = edit_difficulty_lines.get("Edit", []) + oni_difficulty_lines.get("Oni", [])

        # Extra validation to make sure every difficulty dataset has same line count
        expected_length = len(difficulty_lines["EditOni"])
        for difficulty, lines in difficulty_lines.items():
            if len(lines) != expected_length:
                print(f"Warning: {difficulty} has length mismatch (Expected: {expected_length}, Found: {len(lines)})")
            else:
                print(f"{difficulty} has {len(lines)} lines (OK).")

        # Save each dataset
        for difficulty, lines in difficulty_lines.items():
            np.save(os.path.join(self.datasets_dir, f"{difficulty}.npy"), np.array(lines))
            print(f"Saved {difficulty}.npy with {len(lines)} lines.")
