import re
import os

project_code_dir = os.path.dirname(__file__)

def extract_metadata(file_content):
    metadata_lines = []
    for line in file_content.strip().split('\n'):
        if line.startswith('COURSE'):
            break
        metadata_lines.append(line)
    return '\n'.join(metadata_lines)

def split_difficulties(file_content):
    difficulties = re.split(r'COURSE:', file_content)[1:]
    difficulty_dict = {}
    
    for difficulty in difficulties:
        lines = difficulty.strip().split('\n')
        name = lines[0].strip()
        difficulty_dict[name] = '\n'.join(lines)
    
    return difficulty_dict

def save_file(filename, content):
    filepath = os.path.join(project_code_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {filepath}")

# Read the input file
filename = os.path.join(project_code_dir, '千本桜.tja')
with open(filename, "r", encoding="utf-8") as file:
    file_content = file.read()

# Extract and save metadata
metadata_content = extract_metadata(file_content)
save_file("metadata.txt", metadata_content)

# Extract and save difficulties
difficulty_dict = split_difficulties(file_content)
for difficulty_name, content in difficulty_dict.items():
    save_file(f"{difficulty_name}.txt", content)
