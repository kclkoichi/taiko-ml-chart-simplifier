import os
import shutil

# Get .tja files specified in valid_charts.txt and copy them to raw_data

cur_dir = os.path.dirname(os.path.abspath(__file__))
valid_charts_file = os.path.join(cur_dir, "src", "analysis", "valid_charts.txt")
songs_path = os.path.join(cur_dir, "songs")
raw_data_path = os.path.join(cur_dir, "raw_data")

os.path.exists(valid_charts_file)
os.makedirs(songs_path, exist_ok=True)
os.makedirs(raw_data_path, exist_ok=True)

valid_filenames = set()
with open(valid_charts_file, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("#"):
            continue
        valid_filenames.add(line.strip())

for root, _, files in os.walk(songs_path):
    for filename in files:
        if filename.endswith(".tja"):
            src_path = os.path.join(root, filename)

            if filename in valid_filenames:
                dst_path = os.path.join(raw_data_path, filename)
                shutil.copy2(src_path, dst_path)  # Copy/paste
                print(f"Copied: {src_path} -> {dst_path}")
