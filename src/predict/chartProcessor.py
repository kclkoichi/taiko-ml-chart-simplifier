import re
import sys
from src.analysis.star_rating import oni_to_hard_map, hard_to_normal_map, normal_to_easy_map

# Can do many processing for one difficulty of a .tja file
# (a pre-processed file for one difficulty of a song)
class ChartProcessor():

    # get all balloon (7) and kusudama (9) in a line
    def get_balloons_and_kusudama(self, line):
        res = []
        for c in line:
            if c == '7':
                res.append('7')
            elif c == '9':
                res.append('9')
        return res

    # Chart preprocessing
    def preprocess(self, chart_lines):
        balloons_list = []
        level_metadata = [] # Lines before #START
        offset = 0
        for line in chart_lines:
            if line.startswith("BALLOON"):
                balloons_list = list(map(int, line.split(":")[1].split(",")))
            if line.startswith("#START"):
                break
            else:
                level_metadata.append(line)
                offset += 1

        lines = [] # All lines, but with "INSERT" or "INSERT_WITH_COMMA" instead of lines with notes
        notes = [] # Only lines with notes to hit (CANNOT be empty, "," are treated as commands, even if they aren't)
        for i in range(offset, len(chart_lines)):
            line = chart_lines[i].strip()
            if re.match(r'^[0-9]', line):
                if ',' in line:
                    lines.append("INSERT_WITH_COMMA")
                else:
                    lines.append("INSERT")
                # Could remove comments logic but... Will leave it to be sure
                line = line.split("//")[0].strip()
                line = line.replace(',', '')
                line = line.replace(' ', '')
                
                notes.append(line)
            else:
                # Also keep lines with just comma "," as it is. (even though it's a line note)
                lines.append(line)
      
        balloon_index = 0
        balloons = {} # index(line) -> [(type(7or9), number of hits)] # list because there might be many balloons in 1 line
        # Balloon logic, only applied to notes
        for i in range(len(notes)):
            line = notes[i].strip()
            balloons_and_kusudama = self.get_balloons_and_kusudama(line)
            for b in balloons_and_kusudama:
                balloons[i] = []
                balloons[i].append((b, balloons_list[balloon_index]))
                balloon_index += 1

        # should never happen
        if balloon_index != len(balloons_list):
            print(f"Couldn't find all balloons in the chart.\nFound: {balloon_index+1}\nExpected: {len(balloons_list)}")
            sys.exit(0)

        return level_metadata, lines, notes, balloons
    
    # Brute-force prime factorisation
    # Source: https://stackoverflow.com/questions/15347174/python-finding-prime-factors
    def prime_factors(self, n):
        i = 2
        factors = []
        while i * i <= n:
            if n % i:
                i += 1
            else:
                n //= i
                factors.append(i)
        if n > 1:
            factors.append(n)
        return factors

    # Correct character count in a line of note(s)
    def simple_correct(self, line, old_line, beat):
        for f in self.prime_factors(beat):
            if(len(line) % f == 0):
                return line
        if(len(line) == 0 or len(line) == 1):
            return line
        if(len(line) == len(old_line)):
            return line
        if(len(line) % beat == 1 or len(line) % len(old_line)):
            return line[:-1]
        
        print(f"{line} is not matching {beat}")
        return line
    
    # Only balloon (7) and kusudama (9) need a hitcount in BALLOON:
    def add_hitcount_79(
        self, 
        line_i, # line of notes in which 7/9 occurs
        index_of_79, # Index among 7/9 in that line
        char, # Char (7/9)
        old_balloons, # Balloons from old, harder chart
        new_balloons # Balloons for new chart
    ):
        hit_count = 5 # TODO: Maybe make more intelligent default hit_count

        if line_i in old_balloons:
            if index_of_79 < len(old_balloons[line_i]):
                if(old_balloons[line_i][index_of_79][0] == char):
                    old_hit_count = old_balloons[line_i][index_of_79][1]
                    # Remove 1/4 for every difficulty down
                    hit_count = max(1, old_hit_count - (old_hit_count//4))
                # TODO: Maybe deal with the else case, take another balloon hit count in same line?

        new_balloons.append(hit_count)
    
    # Modifies chart_lines in a way that balloons (7), kusudama (9), and long notes (5/6) are valid
    def fix_5679(
        self, 
        line_i, # line of notes in which 5/6/7/9 occurs
        char, # Char (5/6/7/9)
        char_i, # Index of char 5/6/7/9 in line
        chart_lines, # Lines of new chart
    ):
        found = False
        # Find corresponding 8.
        # Start from current index (char_i) in the first line (line_i), then check all char in all next lines
        for i in range(line_i, len(chart_lines)):
            if found: 
                break
            for j in range(char_i+1 if i == line_i else 0, len(chart_lines[i])):
                if chart_lines[i][j] == '0':
                    continue
                if chart_lines[i][j] == '8':
                    # Everything is alright
                    return
                # Error: Found a note (1/2/3/4/5/6/7/9) before end of balloon/long note (5/6/7)
                found = True
                error_line_i = i
                error_char_i = j
                break
        
        if not found:
            print("couldn't find 8")
            # It means that there is a non-ending 5/6/7 till end of chart
            chart_lines[len(chart_lines)-1] = chart_lines[len(chart_lines)-1][:-1] + '8'
            return

        # Need to fix no 8 after 5/6/7
        if(line_i == error_line_i):
            fixed_line = []
            # Expand: append 0 after each char
            for char in chart_lines[line_i]:
                fixed_line.append(char)
                fixed_line.append('0')
            # Adjust after expansion
            char_i *= 2
            error_char_i *= 2
            # Insert 8 at midpoint between 5/6/7 and next note
            mid_index = (char_i + error_char_i) // 2
            fixed_line[mid_index] = '8'
            chart_lines[line_i] = "".join(fixed_line)  # Convert to string
            return
        
        # Found next 1/2/3/4 in future lines
        if(error_char_i == 0):
            if(line_i == error_line_i-1):
                # If last char is 0, replace with 8
                if chart_lines[line_i][len(chart_lines[line_i]) - 1] == '0':
                    chart_lines[line_i] = chart_lines[line_i][:-1] + '8'
                    return
                # It means 100% sure last char is 5/6/7
                print(f"Rare add 8 CASE_1: \nline: {chart_lines[line_i]}")
                fixed_line = []
                for char in chart_lines[line_i]:
                    fixed_line.append(char)
                    for c in "000":
                        fixed_line.append(c)# Expand more than usual
                fixed_line[-1] = '8'
                chart_lines[line_i] = "".join(fixed_line)
                return
            else:
                # A line in between the line with 567 and future 1234. Simplified fix! 
                # (Otherwise need to set to "0" if empty line, expand to find middle etc...?)
                chart_lines[error_line_i] = "8"
                return
        else:
            fixed_line = []
            for char in chart_lines[error_line_i]:
                fixed_line.append(char)
                fixed_line.append('0')
            # Adjust after expansion
            error_char_i *= 2
            # Insert 8
            mid_index = (error_char_i) // 2  # Find midpoint index (index 0 to error_char_i)
            fixed_line[mid_index] = '8'
            chart_lines[line_i] = "".join(fixed_line)
            return
        
    difficulties = ['Easy', 'Normal', 'Hard', 'Oni']
    map_to_use = {
        "Oni": oni_to_hard_map,
        "Hard": hard_to_normal_map,
        "Normal": normal_to_easy_map
        # We never simplify easy charts
    }

    # Note: doesn't change SCOREINIT and SCOREDIFF because it's not what matters to me
    def fix_level_metadata(self, level_metadata, new_balloons):
        balloon_i = -1 

        for i in range(len(level_metadata)):
            line = level_metadata[i]
            if line.startswith("COURSE"):
                course_i = i
                cur_difficulty = line.split(":")[1]
            if line.startswith("LEVEL"):
                level_i = i
                level = line.split(":")[1]
            if line.startswith("BALLOON"):
                balloon_i = i
        
        level_metadata[course_i] = "COURSE:" + self.difficulties[self.difficulties.index(cur_difficulty) - 1]
        level_metadata[level_i] = "LEVEL:" + self.map_to_use[cur_difficulty][level]
        # A chart might not have balloons/kusudama
        if(balloon_i != -1):
            level_metadata[balloon_i] = "BALLOON:" + ",".join(map(str, new_balloons))
    
    def postprocess(self, level_metadata, lines, old_notes, new_notes, old_balloons):
        fixed_notes = [] # Only has lines with notes (and not "," lines)

        ## Note char count correction
        cur_beat = 4 # default is 4/4
        note_index = 0
        found_start = False
        for i in range(len(lines)):
            line = lines[i]

            if not found_start:
                if line.startswith("#START"):
                    found_start = True
                else:
                    continue # Skip level_metadata

            if line == "INSERT" or line == "INSERT_WITH_COMMA":
                line = self.simple_correct(new_notes[note_index], old_notes[note_index], cur_beat)
                note_index += 1
                fixed_notes.append(line)
            else:
                if line.startswith("#MEASURE"):
                    measure = line.split(' ')[1]
                    a, b = map(int, measure.split('/'))
                    cur_beat = a

        ## Balloons (7), long notes (5/6) and kusudama (9) fixes
        new_balloons = []
        count_5679 = 0
        for i in range(len(fixed_notes)):
            index_in_line_79 = 0
            for index, char in enumerate(fixed_notes[i]):
                if char in "5679":
                    count_5679 += 1
                if char in "56":
                    self.fix_5679(i, char, index, fixed_notes)
                if char in "79":
                    self.add_hitcount_79(i, index_in_line_79, char, old_balloons, new_balloons)
                    index_in_line_79 += 1
                if char == "8":
                    count_5679 -= 1
                    if count_5679 < 0:
                        # Fix error '8' on its own
                        fixed_notes[i] = fixed_notes[i][:index] + "0" + fixed_notes[i][index + 1:]
                    count_5679 += 1

        ## Chart lines
        chart_lines = []
        predicted_index = 0
        for line in lines:
            if line == "INSERT":
                chart_lines.append(fixed_notes[predicted_index])
                predicted_index += 1
            elif line == "INSERT_WITH_COMMA":
                chart_lines.append(fixed_notes[predicted_index] + ",")
                predicted_index += 1
            else:
                chart_lines.append(line)

        ## Prepend level metadata (COURSE, LEVEL, BALLOON etc)
        self.fix_level_metadata(level_metadata, new_balloons)

        return level_metadata + chart_lines
