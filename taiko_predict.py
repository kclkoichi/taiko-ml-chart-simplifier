import argparse
import numpy as np
import tensorflow as tf
import os
import sys
import shutil
from src.make_datasets.tjaFileSlicer import TjaFileSlicer
from src.predict.chartProcessor import ChartProcessor
from src.predict.fix_tja_file import fix_tja_file

# Helper method for exiting
def exit_with_preprocessed_removed():
    try:
        shutil.rmtree(preprocessed_path)
    except Exception as e:
        print(f"Error removing folder: {e}")
    sys.exit(0)

### taiko_predict.py predicts an easier chart from a harder chart
### It can predict Oni -> Hard, Hard -> Normal, Normal -> Easy
### Chain predictions to get Oni -> Easy
### Warning: DO NOT HAVE A DIRECTORY CALLED "preprocessed_data" IN THE OUTPUT DIRECTORY. IT WILL BE REMOVED.

# Change directory to script file location
os.chdir(os.path.dirname(os.path.abspath(__file__)))
models_path = os.path.join("models")
tokenizer_path = os.path.join("models", "tokenizer.json")

# To parse command-line arguments
parser = argparse.ArgumentParser(description="Predict easier versions of Taiko charts from harder versions")
parser.add_argument('--target', '-t', default='Easy', help="Target difficulty to predict. Options: Easy, Normal, Hard")
parser.add_argument('--input', '-i', required=True, help="Path to .tja file for simplification")
parser.add_argument('--output', '-o', default='prediction/out', help="Output directory to save the simplified .tja file")
args = parser.parse_args()

# Resolve the input path to an absolute path, preserving it if already absolute
input_file_path = os.path.abspath(args.input)
output_folder_path = os.path.abspath(args.output)
os.makedirs(output_folder_path, exist_ok=True)

filename = os.path.basename(input_file_path)
if filename.endswith(".tja") and os.path.exists(input_file_path):
    song_name = os.path.splitext(filename)[0]
else:
    print("Input must be a path to an existing .tja file. Exiting.")
    sys.exit(0)

preprocessed_path = os.path.join(output_folder_path, "preprocessed_data")
os.makedirs(preprocessed_path, exist_ok=True)

# Edge case: Fix files with no 'COURSE:' and only 1 chart
have_course = False
with open(input_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        if line.strip().startswith('COURSE:'):
            have_course = True
if not have_course:
    fix_tja_file(input_file_path)

# Preprocess input file
tja_file_slicer = TjaFileSlicer(preprocessed_path)
tja_file_slicer.process_unique_file(input_file_path)

### Finding closest difficulty chart and getting its content
difficulties = ['Easy', 'Normal', 'Hard', 'Oni']

target_difficulty = args.target
if target_difficulty not in difficulties:
    print(f"Invalid target difficulty: {target_difficulty}. Options are: \"Easy\", \"Normal\" and \"Hard\". Exiting.")
    exit_with_preprocessed_removed()

# Check if the target difficulty already exists
target_difficulty_path = os.path.join(preprocessed_path, song_name, f"{target_difficulty}.txt")
if os.path.exists(target_difficulty_path):
    print(f"Target difficulty '{target_difficulty}' already exists for {song_name}. Exiting.")
    exit_with_preprocessed_removed()

# If target difficulty doesn't exist, find the closest harder difficulty
target_index = difficulties.index(target_difficulty)
for difficulty in difficulties[target_index + 1:]:
    difficulty_path = os.path.join(preprocessed_path, song_name, f"{difficulty}.txt")
    if os.path.exists(difficulty_path):
        print(f"Found the closest harder difficulty: '{difficulty}' for {song_name}.")
        cur_difficulty = difficulty
        break
else:
    print(f"No harder difficulties than {target_difficulty} found for {song_name}. Exiting.")
    exit_with_preprocessed_removed()

# Load every line of the text file of input_difficulty, WITHOUT any comment
cur_difficulty_path = os.path.join(preprocessed_path, song_name, f"{cur_difficulty}.txt")
cur_difficulty_lines = None
try:
    with open(cur_difficulty_path, 'r', encoding='utf-8') as file:
        cur_difficulty_lines = []
        for line in file:
            line = line.strip()
            if line.startswith("//"):
                continue
            line = line.split("//")[0].strip()
            cur_difficulty_lines.append(line)
    print(f"Loaded {len(cur_difficulty_lines)} lines from {cur_difficulty_path}")
except IOError as e:
    print(f"Failed to read {cur_difficulty_path}: {e}")
    exit_with_preprocessed_removed()

difficulty_to_model_map = {
    'Normal': 'normal_to_easy_model.h5',
    'Hard': 'hard_to_normal_model.h5',
    'Oni': 'oni_to_hard_model.h5'
}

chartProcessor = ChartProcessor()

with open(tokenizer_path, 'r') as f:
    tokenizer_json = f.read()  # Read as string
tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(tokenizer_json)

to_write = []
to_write.append(cur_difficulty_lines) # To also have original difficulty in the .tja output file

### Chain predictions till getting target difficulty chart
while cur_difficulty != target_difficulty:
    # balloons indexes are only within notes
    # lines start from #START to #END both inclusive
    level_metadata, lines, notes, balloons = chartProcessor.preprocess(cur_difficulty_lines)
    original_notes = notes

    model_path = os.path.join(models_path, difficulty_to_model_map[cur_difficulty])
    model = tf.keras.models.load_model(model_path)

    new_sequence = tokenizer.texts_to_sequences(notes)

    # Pad new sequence to match training input length
    max_len = model.input_shape[1]
    new_sequence = tf.keras.utils.pad_sequences(new_sequence, maxlen=max_len, padding='post')

    predicted = model.predict(np.array(new_sequence))
    # Get the predicted tokens (class with the highest probability)
    predicted_tokens = np.argmax(predicted, axis=-1)
    # Update to new easier notes (by converting back token to char)
    notes = tokenizer.sequences_to_texts(predicted_tokens)
    # Remove spaces from notes 
    # (for some reason, tokenizer puts space characters in between predicted texts)
    notes = [note.replace(' ', '') for note in notes]

    # Update cur_difficulty and cur_difficulty_lines to the next easier difficulty
    cur_difficulty = difficulties[difficulties.index(cur_difficulty) - 1]
    cur_difficulty_lines = chartProcessor.postprocess(level_metadata, lines, original_notes, notes, balloons)
    to_write.append(cur_difficulty_lines)

### Make output .tja file with predicted chart

metadata_path = os.path.join(preprocessed_path, song_name, "metadata.txt")
metadata_lines = []
# Remove comments from original file because they are likely irrelevant now
with open(metadata_path, "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if line.startswith("//"):
            continue
        line = line.split("//")[0].strip()
        if line:
            # Ignore empty lines
            metadata_lines.append(line)

output_file_path = os.path.join(output_folder_path, f"{song_name}.tja")
# Write new .tja file
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for line in metadata_lines:
        output_file.write(line + "\n")
    output_file.write("\n")
    for cur_diff_lines in to_write:
        for line in cur_diff_lines:
            output_file.write(line + "\n") # Add comma if necessary
        output_file.write("\n\n\n")

print(f"Predicted chart saved to: {output_file_path}")
exit_with_preprocessed_removed()
