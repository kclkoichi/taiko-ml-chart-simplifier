import os

# Script to help craft your own dataset
# Writes .tja file names to valid_charts.txt if .tja file meets conditions specified here

# Conditions: 
# - specific beat (time signature)
# - not too many bpm, scrolls, measures change
# - not 2-player song

cur_dir = os.path.dirname(os.path.abspath(__file__))
two_up_dir = os.path.dirname(os.path.dirname(cur_dir))
songs_path = os.path.join(two_up_dir, "songs", "09 Namco Original") # Extra argument to specify folder

# The type of beat I want
beat = 4

# Threshold of count of a command per (entire) .tja file, not per difficulty
# #BPMCHANGE
bpm_change_count_threshold = 25 # Basically limiting to 5-6 bpm change per difficulty
# #SCROLL
scroll_count_threshold = 25
# #MEASURE
measure_count_threshold = 25

output_filenames = []

def process_lines(lines, filename):
    bpm_change_count = 0
    scroll_count = 0
    measure_count = 0
    valid_measure = True
    branching = False
    two_player = False

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
            if line.strip().startswith('STYLE:Double'):
                two_player = True
                break
            if line.strip().startswith('#BRANCH'):
                branching = True
                break
            elif line.startswith('#BPMCHANGE'):
                bpm_change_count += 1
            elif line.startswith('#SCROLL'):
                scroll_count += 1
            elif line.startswith('#MEASURE'):
                measure_count += 1
                measure = line.split(' ')[1]
                a, b = map(int, measure.split('/'))

                if (not (a == 1 or a == 2 or (int(a) % beat == 0)) 
                    and int(b) % beat == 0):
                        # If beat == 4
                        # 1/4, 2/4, 4/4, 8/4, 4/8, 4/12, ... are valid
                        # 3/4, 5/4, 6/4, 7/4, 7/8, ... are invalid 
                        # (most likely not a 4 beats song, or contains some peculiar note lines)
                        valid_measure = False
                        break
        
    if valid_measure and not two_player and not branching:
        if (bpm_change_count <= bpm_change_count_threshold 
            and scroll_count <= scroll_count_threshold 
            and measure_count <= measure_count_threshold):
                output_filenames.append(filename)

for foldername, subfolders, filenames in os.walk(songs_path):
    for filename in filenames:
        if filename.endswith(".tja"):
            file_path = os.path.join(foldername, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                process_lines(lines, filename)

with open(os.path.join(cur_dir, "valid_charts.txt"), "w", encoding="utf-8") as f:
    for filename in output_filenames:
        print(filename)
        f.write(filename + "\n")

print("Total charts:", len(output_filenames))
print("Filenames saved to valid_charts.txt")
