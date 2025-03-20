import numpy as np
import tensorflow as tf
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import Input, LSTM, Dense, Embedding
import os
import json
import sys

# To print full numpy arrays
np.set_printoptions(threshold=sys.maxsize)

epochs = 5 # 100, 500...
batch_size = 32
lstm_units = 128

class ChartSimplificationModel:
    def __init__(self, datasets_dir, models_dir, tokenizer_path):
        self.datasets_dir = datasets_dir
        self.models_dir = models_dir
        self.tokenizer = tf.keras.preprocessing.text.Tokenizer(char_level=True)
        self.max_len = 64  # Assuming max length of sequence is always 64

        # Ensure directories exist
        os.makedirs(self.datasets_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)

        # Load datasets
        self.easy_lines = self.load_dataset('Easy.npy')
        self.normal_lines = self.load_dataset('Normal.npy')
        self.hard_lines = self.load_dataset('Hard.npy')
        self.oni_lines = self.load_dataset('Oni.npy')

        # Prepare data for tokenization
        self.prepare_tokenizer()

        # Save the tokenizer as a JSON file
        self.save_tokenizer(tokenizer_path)

    def load_dataset(self, filename):
        filepath = os.path.join(self.datasets_dir, filename)
        if os.path.exists(filepath):
            return np.load(filepath)
        print(f"Fatal: {filename} not found in {self.datasets_dir}")
        exit()

    def prepare_tokenizer(self):
        """Tokenize all loaded datasets and prepares padded sequences"""
        all_lines = np.concatenate((self.easy_lines, self.normal_lines, self.hard_lines, self.oni_lines))
        
        # Fit tokenizer
        self.tokenizer.fit_on_texts(all_lines)
        self.vocab_size = len(self.tokenizer.word_index) + 1 # Include padding index
        
        # Convert datasets into sequences
        self.easy_sequences = self.convert_to_sequences(self.easy_lines)
        self.normal_sequences = self.convert_to_sequences(self.normal_lines)
        self.hard_sequences = self.convert_to_sequences(self.hard_lines)
        self.oni_sequences = self.convert_to_sequences(self.oni_lines)
    
    def save_tokenizer(self, tokenizer_path):
        """Save the tokenizer as a JSON file for prediction"""
        tokenizer_json = self.tokenizer.to_json()
        with open(tokenizer_path, 'w') as f:
            f.write(tokenizer_json)
        print(f"Saved tokenizer to {tokenizer_path}")

    def convert_to_sequences(self, lines):
        """Convert text lines to tokenized sequences with padding"""
        return tf.keras.utils.pad_sequences(self.tokenizer.texts_to_sequences(lines), maxlen=self.max_len, padding='post')

    def create_and_train_model(self, X_train, y_train, model_filename, epochs=epochs, batch_size=batch_size):
        """Create, train, and save an LSTM-based model."""
        # Apparently helps avoid crashes due to memory issues :thinking:
        tf.keras.backend.clear_session()

        # Define model architecture
        inputs = Input(shape=(self.max_len,))
        embedding = Embedding(input_dim=self.vocab_size, output_dim=64)(inputs)
        lstm = LSTM(lstm_units, return_sequences=True)(embedding)
        output = Dense(self.vocab_size, activation='softmax')(lstm)

        model = Model(inputs, output)
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # Train model
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size)

        # Save model
        model_path = os.path.join(self.models_dir, model_filename)
        model.save(model_path)
        print(f"Saved {model_filename} in {self.models_dir}")

    # TODO: Write better check than just empty size maybe
    def create_and_train_oni_to_hard(self):
        if self.oni_sequences.size and self.hard_sequences.size:
            self.create_and_train_model(self.oni_sequences, self.hard_sequences, 'oni_to_hard_model.h5')

    def create_and_train_hard_to_normal(self):
        if self.hard_sequences.size and self.normal_sequences.size:
            self.create_and_train_model(self.hard_sequences, self.normal_sequences, 'hard_to_normal_model.h5')

    def create_and_train_normal_to_easy(self):
        if self.normal_sequences.size and self.easy_sequences.size:
            self.create_and_train_model(self.normal_sequences, self.easy_sequences, 'normal_to_easy_model.h5')

    def train_all_models(self):
        """Trains all models for chart simplification."""
        self.create_and_train_oni_to_hard()
        self.create_and_train_hard_to_normal()
        self.create_and_train_normal_to_easy()

# Btw for some reason it can't make the models in a row, it crashes when trying to move to next one
# Only on gf's machine, not mine... :thinking:
# TODO: Check setup when writing setup instructions
