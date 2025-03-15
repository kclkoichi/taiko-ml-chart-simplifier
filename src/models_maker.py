import numpy as np
import tensorflow as tf
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import Input, LSTM, Dense, Embedding
import os

# To print fully ndarray
import sys
np.set_printoptions(threshold=sys.maxsize)

# Change to the directory of the script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
max_len = max(len(line) for line in all_lines) # Always 64 I think

# Tokenize the data by characters
tokenizer = tf.keras.preprocessing.text.Tokenizer(char_level=True)
tokenizer.fit_on_texts(all_lines)

# Vocabulary size (including padding)
vocab_size = len(tokenizer.word_index) + 1

# Pad sequences to the same length
# Note: In a sequence 0 is used for padding
easy_sequences = tf.keras.utils.pad_sequences(tokenizer.texts_to_sequences(easy_lines), maxlen=max_len, padding='post')
normal_sequences = tf.keras.utils.pad_sequences(tokenizer.texts_to_sequences(normal_lines), maxlen=max_len, padding='post')
hard_sequences = tf.keras.utils.pad_sequences(tokenizer.texts_to_sequences(hard_lines), maxlen=max_len, padding='post')
oni_sequences = tf.keras.utils.pad_sequences(tokenizer.texts_to_sequences(oni_lines), maxlen=max_len, padding='post')

# Function to create and train the model
def create_and_train_model(X_train, y_train, model_filename):
    # Define the model architecture
    inputs = Input(shape=(max_len,))
    embedding = Embedding(input_dim=vocab_size, output_dim=64)(inputs)
    lstm = LSTM(128, return_sequences=True)(embedding)
    output = Dense(vocab_size, activation='softmax')(lstm)

    # Build the model
    model = Model(inputs, output)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Fit the model
    model.fit(X_train, y_train, epochs=1000, batch_size=16)

    # Save the model in the models directory
    model.save(os.path.join(models_dir, model_filename))  # Save in models directory
    print(f"Saved {model_filename} in {models_dir}")

    return model

# Training:
# Oni to Hard Model
# create_and_train_model(oni_sequences, hard_sequences, 'oni_to_hard_model.h5')
# # Hard to Normal Model
# create_and_train_model(hard_sequences, normal_sequences, 'hard_to_normal_model.h5')
# # Normal to Easy Model
# create_and_train_model(normal_sequences, easy_sequences, 'normal_to_easy_model.h5')
