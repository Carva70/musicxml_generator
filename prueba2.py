import xml.etree.ElementTree as ET
import random

# Assuming you have the necessary data structures like rest_values, rhythmic_values, scale, notes, alterations, and root defined already

# Load the previously generated MusicXML file
tree = ET.parse('cosa2.musicxml')
root = tree.getroot()

# Function to add expression slurs based on the positions of rests
def add_slurs_to_part(part_element):
    measure_number = 1
    slur_start = None

    for measure in part_element.iter('measure'):
        count_ele1 = 0
        flag_start_slur = True
        for ele in measure.iter('note'):
            if ele is not None:
                flag_stop_slur = False
                if ele.find('rest') == None:
                    count_ele2 = 0
                    for ele2 in measure.iter('note'):
                        if (count_ele1 + 1) == count_ele2 and ele2.find('rest') is not None:
                            flag_stop_slur = True
                        count_ele2 += 1
                    if flag_stop_slur and not flag_start_slur:
                        notations_elem = ele.find('notations')
                        if notations_elem is None:
                            notations_elem = ET.SubElement(ele, 'notations')
                        slur_elem = ET.SubElement(notations_elem, 'slur', {'type': 'stop', 'number': '1'})
                    if flag_start_slur and not flag_stop_slur:
                        notations_elem = ele.find('notations')
                        if notations_elem is None:
                            notations_elem = ET.SubElement(ele, 'notations')
                        slur_elem = ET.SubElement(notations_elem, 'slur', {'type': 'start', 'number': '1'})
                    flag_start_slur = False
                else:
                    flag_start_slur = True

            prev_ele = ele
            count_ele1 += 1

def add_beams_to_part(part_element):
    measure_number = 1
    slur_start = None

    for measure in part_element.iter('measure'):
        count_ele1 = 0
        flag_start_slur = True
        for ele in measure.iter('note'):
            if ele is not None:
                flag_stop_slur = False
                if ele.find('rest') == None:
                    count_ele2 = 0
                    for ele2 in measure.iter('note'):
                        if (count_ele1 + 1) == count_ele2 and ele2.find('rest') is not None:
                            flag_stop_slur = True
                        count_ele2 += 1
                    if flag_stop_slur and not flag_start_slur:
                        beam_elem1 = ET.SubElement(ele, 'beam', {'number': '1'})
                        beam_elem2 = ET.SubElement(ele, 'beam', {'number': '2'})
                        beam_elem1.text = "end"
                        beam_elem2.text = "end"
                    elif flag_start_slur and not flag_stop_slur:
                        beam_elem1 = ET.SubElement(ele, 'beam', {'number': '1'})
                        beam_elem2 = ET.SubElement(ele, 'beam', {'number': '2'})
                        beam_elem1.text = "begin"
                        beam_elem2.text = "begin"
                    else:
                        beam_elem1 = ET.SubElement(ele, 'beam', {'number': '1'})
                        beam_elem2 = ET.SubElement(ele, 'beam', {'number': '2'})
                        beam_elem1.text = "continue"
                        beam_elem2.text = "continue"
                    flag_start_slur = False
                else:
                    flag_start_slur = True

            prev_ele = ele
            count_ele1 += 1


# Add slurs to each part
for part in root.findall('.//part'):
    add_slurs_to_part(part)
    add_beams_to_part(part)

# Write the modified MusicXML to a new file
tree.write('cosa3.musicxml', encoding='UTF-8', xml_declaration=True)
