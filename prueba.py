
import random
import xml.etree.ElementTree as ET

tree = ET.parse('cosa.musicxml')
root = tree.getroot()

# scale = list(range(21, 108))
# scale = [60, 61, 62, 63, 64, 65] #60 = C chromatic2
# scale = [72, 74, 75, 68, 67, 65, 63, 63] #60 = C phrase3
# scale = [75, 74, 72, 71, 71] #60 = C phrase2
# scale = [72, 70, 68, 67, 67] #60 = C phrase1

scale = [69, 71, 72, 73, 74, 70, 75]

notes = {0: "C", 1: "C", 2: "D", 3: "E", 4: "E", 5: "F", 6: "F", 7: "G", 8: "A", 9: "A", 10: "B", 11: "B"}
alterations = {0: 0, 1: 1, 2: 0, 3: -1, 4: 0, 5: 0, 6: 1, 7: 0, 8: -1, 9: 0, 10: -1, 11: 0}

rhythmic_values = [
    #('quarter', True, 0.1),
    #('quarter', False, 0.1),
    #('16th', True, 0.1),
    #('16th', False, 0.1),
    #('32nd', False, 0.1),
    #('eighth', False, 0.1),
    #('eighth', True, 0.1),
    ('half', False, 0.1),
    #('half', True, 0.1),
    ('whole', False, 0.01),
    #('whole', True, 0.1)
]

rest_values = [
    #('eighth', False, 0.1),
    #('eighth', True, 0.1),
    #('quarter', True, 0.1),
    ('quarter', False, 0.1),
    #('half', False, 0.1),
    #('half', True, 0.1),
    #('whole', False, 0.1),
    #('whole', True, 0.1)
]

is_retrograded = False
is_inverted = False
offset = 0

def read_patterns_from_file(file_path):
    rhythmic_patterns = []
    with open(file_path, 'r') as file:
        current_pattern = []
        in_pattern = False
        
        for line in file:
            stripped_line = line.strip()
            if stripped_line == '**begin**':
                in_pattern = True
                current_pattern = []
            elif stripped_line == '**end**':
                in_pattern = False
                if current_pattern:
                    rhythmic_patterns.append(current_pattern)
            elif in_pattern:
                elements = stripped_line.split(', ')
                rhythmic_value = elements[0].strip("'")
                has_dot = elements[1] == 'True'
                
                time_modification = None
                if len(elements) > 2 and elements[2] != 'None':
                    time_modification = eval(elements[2])
                
                tie_type = None
                if len(elements) > 3 and elements[3] != 'None':
                    tie_type = int(elements[3])
                
                is_rest = False
                if len(elements) > 4 and elements[4] == 'True':
                    is_rest = True
                
                current_pattern.append((rhythmic_value, has_dot, time_modification, tie_type, is_rest))
    return rhythmic_patterns

rhythmic_patterns = read_patterns_from_file('patterns/generated_patterns.txt')

def invert_series(series):
    inverted_series = []
    inverted_series.append(series[0])
    for i in range(1, len(series)):
        inverted_series.append(inverted_series[i - 1] - (series[i] - series[i - 1]))
    return inverted_series

def transpose_series(series, offset):
    return [(note + offset) for note in series]

def next_note_serial(series, note_counter, mode, is_retrograde=False, is_inverted=False, offset=0):
    if is_inverted:
        series = invert_series(series)
    
    series = transpose_series(series, offset)
        
    if is_retrograde:
        series = series[::-1]
        
    return series[note_counter % len(series)]

def next_note(allow_repeated_note, previous_pitch, scale, note_counter, mode, total_notes, segments=None):
    global is_retrograded
    global is_inverted
    global offset
    if mode == 1:
        if allow_repeated_note:
            return random.choice(scale)
        else:
            if previous_pitch is not None:
                scale_copy = scale.copy()
                if previous_pitch in scale_copy:
                    scale_copy.remove(previous_pitch)
                return random.choice(scale_copy)
            else:
                return random.choice(scale)
    elif mode == 2:
        return scale[note_counter % len(scale)]
    elif mode == 3:
        return random.choices(scale, weights=[1 for _ in scale])[0]
    elif mode == 4:
        mid_point = len(scale) // 2
        progress_ratio = note_counter / total_notes
        range_extent = int(progress_ratio * (len(scale) - 1))
        if range_extent == 0:
            return scale[mid_point]
        lower_bound = max(0, mid_point - range_extent)
        upper_bound = min(len(scale) - 1, mid_point + range_extent)
        dynamic_range = scale[lower_bound:upper_bound + 1]
        if (len(dynamic_range) > 1) and not allow_repeated_note:
            dynamic_range.remove(previous_pitch)
        return random.choice(dynamic_range)
    elif mode == 5:
        if (note_counter % len(scale)) == 0:
            is_retrograded = random.choice([True, False])
            is_inverted = random.choice([True, False])
            offset = random.choice(range(0, 12))
        return next_note_serial(scale, note_counter, mode, is_retrograded, is_inverted, offset)
    elif mode == 6:
        if segments is None:
            raise ValueError("Segments must be provided for mode 6")

        segment_index = note_counter // (total_notes // len(segments))
        if segment_index >= len(segments):
            segment_index = len(segments) - 1
        current_segment = segments[segment_index]

        dynamic_range = scale[current_segment[0]:current_segment[1] + 1]
        segment_mode = current_segment[2]
        
        return next_note(allow_repeated_note, previous_pitch, dynamic_range, note_counter, segment_mode, total_notes)

def add_notes_to_part(part_element, allow_repeated_note=False, rest_probability=0.3, rest_init=True, infinite_loop=True, total_notes=200, segments=None, use_patterns=False, rhythm_pattern_segments=None):
    measure = ET.SubElement(part_element, 'measure', {'number': '1'})
    previous_pitch = None
    prev_rest_index = 0
    note_counter = 0

    pattern_index_counter = 0
    pattern_number = 0
    tie_type = None
    is_rest = None

    for i in range(total_notes):
        if (note_counter == total_notes and not infinite_loop) or (note_counter == len(scale) and not infinite_loop):
            break
        if use_patterns and ((pattern_index_counter % len(rhythmic_patterns[pattern_number])) == 0):
            if ((random.random() < rest_probability) and (prev_rest_index != (i - 1))) or (rest_init and (i < 3)):
                rest_value, has_dot = random.choices([rest[0:2] for rest in rest_values], weights=[rest[2] for rest in rest_values])[0]
                rest = ET.SubElement(measure, 'note')
                ET.SubElement(rest, 'rest')
                if rest_value == 'whole':
                    ET.SubElement(rest, 'duration').text = '16'
                else:
                    ET.SubElement(rest, 'duration').text = '3'
                ET.SubElement(rest, 'voice').text = '1'
                ET.SubElement(rest, 'type').text = rest_value
                if has_dot:
                    ET.SubElement(rest, 'dot')
                prev_rest_index = i
                continue

        if use_patterns:

            if (rhythm_pattern_segments):
                if (pattern_index_counter % len(rhythmic_patterns[pattern_number])) == 0:
                    segment_index = (i * len(rhythm_pattern_segments)) // total_notes
                    current_segment = rhythm_pattern_segments[segment_index]
                    pattern_number = random.choice(current_segment)
                    pattern_index_counter = 0

            else:
                if (pattern_index_counter % len(rhythmic_patterns[pattern_number])) == 0:
                    pattern_index_counter = 0
                    pattern_number = random.choice(range(len(rhythmic_patterns)))

            
            current_pattern = rhythmic_patterns[pattern_number][pattern_index_counter]
            next_pattern = rhythmic_patterns[pattern_number][pattern_index_counter + 1] if len(rhythmic_patterns[pattern_number]) > (pattern_index_counter + 1) else None
            rhythmic_value = current_pattern[0]
            has_dot = current_pattern[1]
            
            time_modification = current_pattern[2] if len(current_pattern) > 2 else None
            tie_type = current_pattern[3] if len(current_pattern) > 3 else None
            is_rest = current_pattern[4] if len(current_pattern) > 4 else None
            
            pattern_index_counter += 1
        else:
            rhythmic_value, has_dot = random.choices([rhythm[0:2] for rhythm in rhythmic_values], weights=[rhythm[2] for rhythm in rhythmic_values])[0]

        mode = 6  # mode

        if is_rest:
            rest = ET.SubElement(measure, 'note')
            ET.SubElement(rest, 'rest')
            ET.SubElement(rest, 'duration').text = '3'
            ET.SubElement(rest, 'voice').text = '1'
            ET.SubElement(rest, 'type').text = rhythmic_value
            if has_dot:
                ET.SubElement(rest, 'dot')
            if time_modification:
                actual_notes, normal_notes = time_modification
                time_mod = ET.SubElement(rest, 'time-modification')
                ET.SubElement(time_mod, 'actual-notes').text = str(actual_notes)
                ET.SubElement(time_mod, 'normal-notes').text = str(normal_notes)
            # Do not increase the note_counter and skip the rest of the loop
            continue

        if tie_type == 2:
            pitch = previous_pitch
        else:
            pitch = next_note(allow_repeated_note, previous_pitch, scale, note_counter, mode, total_notes, segments)

        previous_pitch = pitch

        note = ET.SubElement(measure, 'note')
        pitch_elem = ET.SubElement(note, 'pitch')
        step = notes[pitch % 12]
        alt = alterations[pitch % 12]
        ET.SubElement(pitch_elem, 'step').text = step
        ET.SubElement(pitch_elem, 'alter').text = str(alt)
        ET.SubElement(pitch_elem, 'octave').text = str(pitch // 12 - 1)

        ET.SubElement(note, 'duration').text = '3'
        ET.SubElement(note, 'voice').text = '1'
        ET.SubElement(note, 'type').text = rhythmic_value

        if has_dot:
            ET.SubElement(note, 'dot')

        if time_modification:
            actual_notes, normal_notes = time_modification
            time_mod = ET.SubElement(note, 'time-modification')
            ET.SubElement(time_mod, 'actual-notes').text = str(actual_notes)
            ET.SubElement(time_mod, 'normal-notes').text = str(normal_notes)

        notations = ET.SubElement(note, 'notations')
        if tie_type:
            if tie_type == 1:
                ET.SubElement(notations, 'tied', type='start')
            elif tie_type == 2:
                ET.SubElement(notations, 'tied', type='stop')
            
        if time_modification:
            if next_pattern == None:
                ET.SubElement(notations, 'tuplet', type='stop')
            elif len(next_pattern) > 2:
                if next_pattern[2] != time_modification:
                    ET.SubElement(notations, 'tuplet', type='stop')

        if tie_type != 2 or is_rest:
            note_counter += 1

# Example segments input by user
user_segments = [
    [0, 0, 2],
    [0, 1, 2],
    [0, 2, 2],
    [0, 3, 2],
    [0, 4, 2],
    [0, 5, 2],
    [0, 6, 2],
    [0, 6, 2],
    [0, 6, 2],
]
total_notes = 600
segments = user_segments

user_rhythm_pattern_segments = [
    [3],
    [3, 4, 5, 6, 7],
    [0, 1, 2, 3, 4, 5, 6, 7],
]

for i in range(1, 10):
    part_id = f'P{i}'
    new_part = ET.SubElement(root, 'part', {'id': part_id})
    add_notes_to_part(new_part, total_notes=total_notes, segments=segments, use_patterns=True, rest_probability=0, rest_init=False, rhythm_pattern_segments=None)

tree.write('cosa2.musicxml', encoding='UTF-8', xml_declaration=True)