import os
import matplotlib.pyplot as plt

# Script to see distribution of note line lengths in all .tja files

cur_dir = os.path.dirname(os.path.abspath(__file__))
two_up_dir = os.path.dirname(os.path.dirname(cur_dir))
songs_path = os.path.join(two_up_dir, "songs")

file_count = 0
total_line_count = 0
line_count_map = {}

def process_lines(lines, filename):
    # Flag to track when we are inside #START and #END
    inside_chart = False

    for line in lines:
        line = line.strip()

        if line == "#START":
            inside_chart = True
            continue
        
        if line == "#END":
            inside_chart = False
            continue

        if inside_chart:
            if not line or line.startswith('#'):
                continue
            global total_line_count
            total_line_count += 1 # Line with notes (might be 0 note) for sure now
            if "//" in line:
                line = line.split("//")[0].strip()
            line = line.replace(',', '')
            line = line.replace(' ', '')
            line_length = len(line)
            if line_length not in line_count_map:
                line_count_map[line_length] = 0
            line_count_map[line_length] += 1
            # To get a song with some peculiarity
            # if line_length == 192:
            #     print(line)
            #     print(filename)
            #     exit()

for foldername, subfolders, filenames in os.walk(songs_path):
    for filename in filenames:
        if filename.endswith(".tja"):
            file_count += 1
            file_path = os.path.join(foldername, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                process_lines(lines, filename)

print(f"Total .tja files found: {file_count}")
print(f"Total lines with notes found: {total_line_count}")
sorted_line_count_map = sorted(line_count_map.items(), key=lambda item: item[1], reverse=True)
print(sorted_line_count_map)

# Maybe matplotlib to come up with nice chart? Not sure useful though
