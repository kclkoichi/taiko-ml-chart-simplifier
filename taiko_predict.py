import numpy as np
import tensorflow as tf
import os
import sys
import re
from src.make_datasets.tjaFileSlicer import TjaFileSlicer

### From an input file, predicts an easified version of the chart

target_difficulty = "Easy"

# Change directory to script file location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

prediction_input_path = os.path.join("prediction", "in")
preprocessed_path = os.path.join("prediction", "in", "preprocessed_data")
models_path = os.path.join("models", "E_model_only_4_beats_charts")
predictions_path = os.path.join("prediction", "out")
tokenizer_path = os.path.join("models", "tokenizer.json")

### Preprocess input file
tja_file_slicer = TjaFileSlicer(prediction_input_path, preprocessed_path)
tja_file_slicer.process_files()

### Find closest difficulty

difficulties = ['Easy', 'Normal', 'Hard', 'Oni']

for f in os.listdir(prediction_input_path):
    print(f)

song_name = None
# Assumes only one song in folder!!
tja_files = [f for f in os.listdir(prediction_input_path) if f.endswith(".tja")]
if tja_files:  
    # Get the first file ending with .tja
    song_name = os.path.splitext(tja_files[0])[0]  # Remove the .tja extension  
else:  
    print("No .tja files found.")
    print(song_name)
    exit()

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

# Load every line of the text file of input_difficulty
cur_difficulty_path = os.path.join(preprocessed_path, song_name, f"{cur_difficulty}.txt")
try:
    with open(cur_difficulty_path, 'r', encoding='utf-8') as file:
        cur_difficulty_lines = file.readlines()
    print(f"Loaded {len(cur_difficulty_lines)} lines from {cur_difficulty_path}")
except IOError as e:
    print(f"Failed to read {cur_difficulty_path}: {e}")
    sys.exit(1)

### Preprocess chart
lines = []
notes = []

for i in range(len(cur_difficulty_lines)):
    line = cur_difficulty_lines[i].strip()
    # Check if the line starts with any digit 0-9, meaning line with notes
    if re.match(r'^[0-9]', line):
        lines.append("INSERT")
        line = line.split("//")[0].strip()
        line = line.replace(',', '')
        line = line.replace(' ', '')
        notes.append(line)
    else:
        lines.append(line)

### Load model and chain predictions

difficulty_to_model_map = {
    'Normal': 'normal_to_easy_model.h5',
    'Hard': 'hard_to_normal_model.h5',
    'Oni': 'oni_to_hard_model.h5'
}

while cur_difficulty is not target_difficulty:
    # Load the saved model
    model_path = os.path.join(models_path, difficulty_to_model_map[cur_difficulty])
    model = tf.keras.models.load_model(model_path)

    # Load the tokenizer from a JSON file
    with open(tokenizer_path, 'r') as f:
        tokenizer_json = f.read()  # Read as string
    tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(tokenizer_json)

    # Convert new input to sequence
    new_sequence = tokenizer.texts_to_sequences(notes)

    # Pad new sequence to match training input length
    max_len = model.input_shape[1]
    new_sequence = tf.keras.utils.pad_sequences(new_sequence, maxlen=max_len, padding='post')

    # Predict (get predicted output)
    predicted = model.predict(np.array(new_sequence))

    # Get the predicted indices (class with the highest probability)
    predicted_indices = np.argmax(predicted, axis=-1)

    # Convert indices back to text
    predicted_sequence = tokenizer.sequences_to_texts(predicted_indices)

    notes = predicted_sequence

    # Remove spaces from notes (TODO: why are they here btw?)
    notes = [note.replace(' ', '') for note in notes]

    # Update cur_difficulty to the next easier difficulty
    cur_difficulty = difficulties[difficulties.index(cur_difficulty) - 1]

### Postprocess chart
# add logic chart? OR class

# Ensure predictions directory exists
os.makedirs(predictions_path, exist_ok=True)

output_file_path = os.path.join(predictions_path, f"{song_name}.tja")

predicted_index = 0
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for line in lines:
        if line == "INSERT":
            if predicted_index < len(notes):
                output_file.write(notes[predicted_index] + ",\n")
                predicted_index += 1
            else:
                print("wtf")
                output_file.write("\n")  # Handle missing predictions safely
        else:
            output_file.write(line + "\n")


print(f"Predicted chart saved to: {output_file_path}")

# TODO: More postprocessing to make the chart better
# Strange line with 9 chars... for example
# deal with ballons7 and 9
# Also fix impossible notes
