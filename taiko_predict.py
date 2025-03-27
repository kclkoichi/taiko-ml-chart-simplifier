import numpy as np
import tensorflow as tf
import os
import sys
from src.make_datasets.tjaFileSlicer import TjaFileSlicer
from src.predict.chartProcessor import ChartProcessor

# Logic to predict an easier version of a chart from a harder version

# Notes: 
# Can't predict Edit to Oni because they are too similar, and one isn't necessarily harder than the other.
# Will predict from Oni to Hard, from Hard to Normal, and from Normal to Easy.
# Because Edit without Oni is not possible, it is never used.

target_difficulty = "Easy"

# Change directory to script file location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

prediction_input_path = os.path.join("prediction", "in")
preprocessed_path = os.path.join("prediction", "in", "preprocessed_data")
models_path = os.path.join("models", "best_models")
predictions_path = os.path.join("prediction", "out")
tokenizer_path = os.path.join("models", "tokenizer.json")

# Preprocess input files
tja_file_slicer = TjaFileSlicer(prediction_input_path, preprocessed_path)
tja_file_slicer.process_files()

print("")


### Finding closest difficulty chart and getting its content from here

difficulties = ['Easy', 'Normal', 'Hard', 'Oni']
song_name = None

# Assumes only one song in folder!!
tja_files = [f for f in os.listdir(prediction_input_path) if f.endswith(".tja")]
if tja_files:  
    # Get the first file ending with .tja
    song_name = os.path.splitext(tja_files[0])[0]  # Remove the .tja extension  
    print(f"Using {song_name} for prediction")
else:  
    print(f"No .tja files found in {prediction_input_path}")
    sys.exit(0)

if target_difficulty not in difficulties[:-1]:
    print(f"Target difficulty must be either Easy, Normal, or Hard")
    sys.exit(0)

# Check if the target difficulty already exists
target_difficulty_path = os.path.join(preprocessed_path, song_name, f"{target_difficulty}.txt")
if os.path.exists(target_difficulty_path):
    print(f"Target difficulty '{target_difficulty}' already exists for {song_name}. Exiting.")
    sys.exit(0)

cur_difficulty = None

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
    sys.exit(0)

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
    sys.exit(1)

difficulty_to_model_map = {
    'Normal': 'normal_to_easy_model.h5',
    'Hard': 'hard_to_normal_model.h5',
    'Oni': 'oni_to_hard_model.h5'
}

chartProcessor = ChartProcessor()

to_write = []
to_write.append(cur_difficulty_lines) # To also have original difficulty in the .tja output file

### Chain predictions till getting target difficulty chart
while cur_difficulty is not target_difficulty:
    # balloons indexes are only within notes
    # lines start from #START to #END both inclusive
    level_metadata, lines, notes, balloons = chartProcessor.preprocess(cur_difficulty_lines)
    original_notes = notes

    model_path = os.path.join(models_path, difficulty_to_model_map[cur_difficulty])
    model = tf.keras.models.load_model(model_path)

    with open(tokenizer_path, 'r') as f:
        tokenizer_json = f.read()  # Read as string
    tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(tokenizer_json)

    new_sequence = tokenizer.texts_to_sequences(notes)

    # Pad new sequence to match training input length
    max_len = model.input_shape[1]
    new_sequence = tf.keras.utils.pad_sequences(new_sequence, maxlen=max_len, padding='post')

    predicted = model.predict(np.array(new_sequence))
    # Get the predicted indices (class with the highest probability)
    predicted_indices = np.argmax(predicted, axis=-1)
    # Update to new easier notes (by converting back token to char)
    notes = tokenizer.sequences_to_texts(predicted_indices)
    # Remove spaces from notes 
    # (for some reason, tokenizer puts space characters in between predicted texts)
    notes = [note.replace(' ', '') for note in notes]

    # Update cur_difficulty and cur_difficulty_lines to the next easier difficulty
    cur_difficulty = difficulties[difficulties.index(cur_difficulty) - 1]
    cur_difficulty_lines = chartProcessor.postprocess(level_metadata, lines, original_notes, notes, balloons)
    to_write.append(cur_difficulty_lines)

### Make output .tja file with predicted chart

# Ensure predictions directory exists
os.makedirs(predictions_path, exist_ok=True)

metadata_path = os.path.join(preprocessed_path, song_name, "metadata.txt")
metadata_lines = []
# Remove comments from original file because they are likely irrelevant
with open(metadata_path, "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if line.startswith("//"):
            continue
        line = line.split("//")[0].strip()
        if line:
            # Ignore empty lines
            metadata_lines.append(line)

output_file_path = os.path.join(predictions_path, f"{song_name}.tja")
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
