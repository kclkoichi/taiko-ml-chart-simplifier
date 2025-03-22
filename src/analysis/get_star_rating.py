import os
import re

# Analysis of star rating

cur_dir = os.path.dirname(os.path.abspath(__file__))
two_up_dir = os.path.dirname(os.path.dirname(cur_dir))
songs_path = os.path.join(two_up_dir, "songs")

# Star rating -> (average, count)
# (Oni includes Edit)
average_difficulty_down_map = {
    "Oni_Hard": {
        10: (0, 0),
        9: (0, 0),
        8: (0, 0),
        7: (0, 0),
        6: (0, 0),
        5: (0, 0),
        4: (0, 0),
        3: (0, 0),
        2: (0, 0),
        1: (0, 0)
    },
    "Hard_Normal": {
        8: (0, 0),
        7: (0, 0),
        6: (0, 0),
        5: (0, 0),
        4: (0, 0),
        3: (0, 0),
        2: (0, 0),
        1: (0, 0)
    },
    "Normal_Easy": {
        7: (0, 0),
        6: (0, 0),
        5: (0, 0),
        4: (0, 0),
        3: (0, 0),
        2: (0, 0),
        1: (0, 0)
    }
}

def extract_difficulty_map(lines):
    difficulty_map = {}
    difficulty = None 

    for line in lines:
        difficulty_match = re.search(r"COURSE:\s*(\w+)", line)
        level_match = re.search(r"LEVEL:\s*(\d+)", line)

        if difficulty_match:
            difficulty = difficulty_match.group(1)
        if level_match and difficulty:
            difficulty_map[difficulty] = int(level_match.group(1))

    return difficulty_map

for foldername, subfolders, filenames in os.walk(songs_path):
    for filename in filenames:
        if filename.endswith(".tja"):
            file_path = os.path.join(foldername, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                difficulty_map = extract_difficulty_map(lines)

                if difficulty_map.get("Edit") and difficulty_map.get("Hard"):
                    old_star_rating = average_difficulty_down_map["Oni_Hard"][difficulty_map.get("Edit")][0]
                    old_count = average_difficulty_down_map["Oni_Hard"][difficulty_map.get("Edit")][1]

                    count = old_count + 1
                    star_rating = (old_star_rating * old_count + difficulty_map.get("Hard")) / count

                    average_difficulty_down_map["Oni_Hard"][difficulty_map.get("Edit")] = (star_rating, count)

                if difficulty_map.get("Oni") and difficulty_map.get("Hard"):
                    old_star_rating = average_difficulty_down_map["Oni_Hard"][difficulty_map.get("Oni")][0]
                    old_count = average_difficulty_down_map["Oni_Hard"][difficulty_map.get("Oni")][1]

                    count = old_count + 1
                    star_rating = (old_star_rating * old_count + difficulty_map.get("Hard")) / count

                    average_difficulty_down_map["Oni_Hard"][difficulty_map.get("Oni")] = (star_rating, count)

                if difficulty_map.get("Hard") and difficulty_map.get("Normal"):
                    old_star_rating = average_difficulty_down_map["Hard_Normal"][difficulty_map.get("Hard")][0]
                    old_count = average_difficulty_down_map["Hard_Normal"][difficulty_map.get("Hard")][1]

                    count = old_count + 1
                    star_rating = (old_star_rating * old_count + difficulty_map.get("Normal")) / count

                    average_difficulty_down_map["Hard_Normal"][difficulty_map.get("Hard")] = (star_rating, count)

                if difficulty_map.get("Normal") and difficulty_map.get("Easy"):
                    old_star_rating = average_difficulty_down_map["Normal_Easy"][difficulty_map.get("Normal")][0]
                    old_count = average_difficulty_down_map["Normal_Easy"][difficulty_map.get("Normal")][1]

                    count = old_count + 1
                    star_rating = (old_star_rating * old_count + difficulty_map.get("Easy")) / count

                    average_difficulty_down_map["Normal_Easy"][difficulty_map.get("Normal")] = (star_rating, count)

print(average_difficulty_down_map)
