import os

# Only look at .tja files specified in valid_charts.txt

main_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
valid_charts_file = os.path.join(main_dir, "src", "analysis", "valid_charts.txt")
songs_path = os.path.join(main_dir, "songs")
raw_data_path = os.path.join(main_dir, "raw_data")

os.path.exists(valid_charts_file)
os.makedirs(songs_path, exist_ok=True)
os.makedirs(raw_data_path, exist_ok=True)

# Logic to get by difficulty stars
edit_difficulty_map = {}
oni_difficulty_map = {}

valid_filenames = set()
with open(valid_charts_file, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("#"):
            continue
        valid_filenames.add(line.strip())

# Walk through songs folder recursively
for root, _, files in os.walk(songs_path):
    for filename in files:
        if filename.endswith(".tja"):  # Ensure we're only processing .tja files
            src_path = os.path.join(root, filename)

            # if filename in valid_filenames:
            with open(src_path, "r", encoding="utf-8") as file:
                next_line_edit = False
                next_line_oni = False

                for line in file:
                    line = line.strip()

                    if line.startswith("COURSE:Edit"):
                        next_line_edit = True
                        continue
                    elif line.startswith("COURSE:Oni"):
                        next_line_oni = True
                        continue

                    if next_line_edit:
                        next_line_edit = False
                        level_number = line.split(":")[1].strip()
                        edit_difficulty_map.setdefault(level_number, []).append(filename)
                        continue

                    if next_line_oni:
                        next_line_oni = False
                        level_number = line.split(":")[1].strip()
                        oni_difficulty_map.setdefault(level_number, []).append(filename)
                        continue

print("\nEdit Difficulty Map:")
for level in range(1, 11):
    level_str = str(level)
    if level_str in edit_difficulty_map:
        print(f"Level {level}: {', '.join(edit_difficulty_map[level_str])}")
    else:
        print(f"Level {level}: No songs")

print("\nOni Difficulty Map:")
for level in range(1, 11):
    level_str = str(level)
    if level_str in oni_difficulty_map:
        print(f"Level {level}: {', '.join(oni_difficulty_map[level_str])}")
    else:
        print(f"Level {level}: No songs")
