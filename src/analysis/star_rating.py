# (Over-simplified) Level rating system for generated charts
# Solely based on the original star rating of the chart

# This correlation exists. Try running get_star_rating.py for analytics

# Had to round to integers, used my own experience to make this mapping

oni_to_hard_map = {
    # Only exists with fanmade games such as OpenTaiko or Taikosan Jirou
    "13": "8",
    "12": "8",
    "11": "8",
    # Valid difficulties in original game
    "10": "8",
    "9": "7",
    "8": "6",
    "7": "5",
    "6": "4",
    "5": "4",
    "4": "3",
    "3": "3",
    "2": "2",
    "1": "2",
}

hard_to_normal_map = {
    "8": "7",
    "7": "6",
    "6": "5",
    "5": "4",
    "4": "3",
    "3": "3",
    "2": "2",
    "1": "2",
}

normal_to_easy_map = {
    "7": "5",
    "6": "4",
    "5": "4",
    "4": "3",
    "3": "3",
    "2": "2",
    "1": "1"
}