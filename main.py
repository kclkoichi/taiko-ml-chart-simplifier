import os

### STILL HAVE TO WORK ON THIS

# Change directory to the script file location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

datasets_path = os.path.join("datasets")
preprocessed_data_path = os.path.join("preprocessed_data")
raw_data_path = os.path.join("raw_data")

# Check if the folder exists and is empty
if os.path.exists(datasets_path) and not os.listdir(datasets_path):
    print("Dataset folder is empty.")
else:
    print("Dataset folder has files.")