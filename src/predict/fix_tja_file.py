import os

def fix_tja_file(file_path):
    """
    Fix .tja file with disorganised metadata and level metadata
    Occurs only when .tja file has only 1 difficulty, and has no COURSE:
    Will default to set it as Oni
    Example: Grievous Lady from Luigi. https://ux.getuploader.com/Luigi/download/71
    """
    try:
        level_value = None
        balloon_value = None
        scoreinit_value = None
        scorediff_value = None
        fixed_lines = []

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Process the lines to rearrange and add missing lines
        for line in lines:
            line = line.strip()
            if line.startswith("LEVEL:"):
                fixed_lines.append("\nCOURSE:Oni")
                level_value = line
                continue
            if line.startswith("BALLOON:"):
                balloon_value = line
                continue
            if line.startswith("SCOREINIT:"):
                scoreinit_value = line
                continue
            if line.startswith("SCOREDIFF:"):
                scorediff_value = line
                continue
            if (not line.startswith("LEVEL:") 
                and not line.startswith("BALLOON:")
                and not line.startswith("SCOREINIT:")
                and not line.startswith("SCOREDIFF:")):
                fixed_lines.append(line)

        # Inserting level metadata at the right place
        course_index = -1
        for i, line in enumerate(fixed_lines):
            if line.strip().startswith("COURSE:"):
                course_index = i
                break

        offset = 1
        fixed_lines.insert(course_index + offset, level_value)
        offset += 1
        if balloon_value:
            fixed_lines.insert(course_index + offset, balloon_value)
            offset += 1
        if scoreinit_value:
            fixed_lines.insert(course_index + offset, scoreinit_value)
            offset += 1
        if scorediff_value:
            fixed_lines.insert(course_index + offset, scorediff_value)
            offset += 1

        # Write the fixed content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in fixed_lines:
                file.write(line + '\n')

        print(f"Fixed file: {file_path}")

    except Exception as e:
        print(f"Error fixing file {file_path}: {e}")
