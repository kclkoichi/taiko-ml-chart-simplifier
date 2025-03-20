import os
from src.make_datasets.tjaFileSlicer import TjaFileSlicer
from src.make_datasets.datasetsMaker import DatasetsMaker

# Prepares datasets to train Taiko ML Chart Simplifier models
# .tja files in raw_data can be nested inside directories
# TODO: Extract .tja files inside .zip files

# Change directory to script file location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

raw_data_path = os.path.join("raw_data")
if os.path.exists(raw_data_path) and not os.listdir(raw_data_path):
    print("raw_data_path directory is empty.")
    print("raw_data_path: " + str(raw_data_path))
    exit()

preprocessed_data_path = os.path.join("preprocessed_data")

# Preprocess .tja files
slicer = TjaFileSlicer(raw_data_path, preprocessed_data_path)
slicer.process_files()

print("\nPreprocessing done.\n")

datasets_path = os.path.join("datasets")

# Prepare dataset for each difficulty (.npy files)
maker = DatasetsMaker(preprocessed_data_path, datasets_path)
maker.process_songs()

print("\nMaking datasets done.\n")
