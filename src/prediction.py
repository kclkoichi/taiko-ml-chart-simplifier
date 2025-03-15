import numpy as np
import tensorflow as tf
import os

# Define directories
datasets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")
models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

# Load the dataset for each difficulty level
# Discovered some vulnerability with allow_pickle: True
easy_lines = np.load(os.path.join(datasets_dir, 'Easy.npy'))
normal_lines = np.load(os.path.join(datasets_dir, 'Normal.npy'))
hard_lines = np.load(os.path.join(datasets_dir, 'Hard.npy'))
oni_lines = np.load(os.path.join(datasets_dir, 'Oni.npy'))

# Combine all data for the tokenizer
all_lines = np.concatenate((easy_lines, normal_lines, hard_lines, oni_lines))

# Tokenize the data by characters
tokenizer = tf.keras.preprocessing.text.Tokenizer(char_level=True)
tokenizer.fit_on_texts(all_lines)



# Load the saved model
model_path = os.path.join(models_dir, "oni_to_hard_model.h5")
model = tf.keras.models.load_model(model_path)

# Example new input (new song)
new_line = ["1102011020003000", "1001201001020110", "100010002000100000200100000100000100200100000000", "1001201001020210", "11003000110030003000300000000000", "", "0"]

# Convert new input to sequence
new_sequence = tokenizer.texts_to_sequences(new_line)

# Pad new sequence to match training input length
max_len = model.input_shape[1]  # Get max_len from the model input shape
new_sequence = tf.keras.utils.pad_sequences(new_sequence, maxlen=max_len, padding='post')

# Predict (get predicted output)
predicted = model.predict(np.array(new_sequence))

# Get the predicted indices (class with the highest probability)
predicted_indices = np.argmax(predicted, axis=-1)

# Convert indices back to text sequences
predicted_sequence = tokenizer.sequences_to_texts(predicted_indices)

# Print predicted output
print("Predicted Output:", predicted_sequence)
