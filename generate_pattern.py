import numpy as np
import sympy.utilities.iterables as sp

# blocks = [
#     [
#         ["quarter", False, None],
#         ["eighth", True, [7,4], 1],
#         ["eighth", False, [7,4], 2],
#         ["eighth", False, [7,4], 1],
#         ["quarter", False, [3,2], 2],
#         ["eighth", False, [3,2]]
#     ],
#     
#     [
#         ["half", False, None, 1],
#         ["eighth", True, [5,4], 2],
#         ["eighth", False, [5,4], 1],
#         ["quarter", False, [3,2], 2],
#         ["eighth", False, [3,2]]
#     ],
#     
#     [
#         ["half", True, None],
#         ["eighth", True, [7,4], 1],
#         ["eighth", False, [7,4], 2],
#         ["eighth", False, [7,4], 1],
#         ["eighth", True, [5,4], 2],
#         ["eighth", False, [5,4]]
#     ]
# ]

blocks = []
            

def variant_generation(pattern):
    rhythm = [[]]
    for p in pattern:
        if isinstance(p, int):
            for r in rhythm:
                r.append(p)
        
        if isinstance(p, list):
            new_r = []
            while 1:
                if rhythm == []: break
                aux_r = rhythm.pop()
                for sub_p in p:
                    aux_r.append(sub_p)
                    new_r.append(aux_r.copy())
                    aux_r.pop()
            rhythm = new_r.copy()
    
    return rhythm

def print_rhythm_from_variant(variant, slur):
    
    size = len(variant)
    if slur:
        rand_beat = int(np.random.random() * (size - 1))


    value_map = {(5, 3): ['eighth', True, [5, 4]],
                 (5, 2): ['eighth', False, [5, 4]],
                 (5, 1): ['16th', False, [5, 4]],
                 (7, 5): [['eighth', True, [7, 4], 1],
                          ['eighth', False, [7, 4], 2]],
                 (7, 4): ['quarter', False, [7, 4]],
                 (7, 3): ['eighth', True, [7, 4]],
                 (7, 2): ['eighth', False, [7, 4]],
                 (7, 1): ['16th', False, [7, 4]],
                 (3, 2): ['quarter', False, [3, 2]],
                 (3, 1): ['eighth', False, [3, 2]]}
    
    block = []

    for index, x in enumerate(variant):
        
        if isinstance(x, list):
            count = sum(e.count(0) for e in x)
            for i in x:
                map_result = value_map[(count, i.count(0))]
                if isinstance(map_result[0], list):
                    for m in map_result:
                        block.append(m)
                else:
                    block.append(map_result.copy())
        else:
            if x == 1:
                block.append(["quarter", False])
            if x == 2:
                block.append(["eighth", False])
                block.append(["eighth", False])
            if x == 3:
                block.append(["eighth", False, [3,2]])
                block.append(["eighth", False, [3,2]])
                block.append(["eighth", False, [3,2]])
            if x == 4:
                block.append(["16th", False])
                block.append(["16th", False])
                block.append(["16th", False])
                block.append(["16th", False])

        if slur and (rand_beat == index) and (block[-1][-1] != 2) and (block[-1][-1] != 1):
            if len(block[-1]) == 3:
                block[-1].append(4)
            elif len(block[-1]) == 2:
                block[-1].append(None)
                block[-1].append(4)

    for i, b in enumerate(block):
        if b[-1] == 4:
            if block[i+1][-1] == 1:
                b.pop()
            else:
                b[-1] = 1
                if len(block[i+1]) == 3:
                    block[i+1].append(2)
                elif len(block[i+1]) == 2:
                    block[i+1].append(None)
                    block[i+1].append(2)


    return block

def create_blocks_from_rhythm(rhythm_array, note_min_size, slur):
    rhythm_extended = []

    for r in rhythm_array:

        if r < 5:
            rhythm_extended.append(int(r))
        else:
            partitions_list = list(sp.multiset_partitions([0]*r, 2)) + list(sp.multiset_partitions([0]*r, 3))

            partitions_list = [p for p in partitions_list if not any(len(sublist) == 1 for sublist in p)]

            perm_part = []

            for i in partitions_list:
                for j in sp.multiset_permutations(i):
                    perm_part.append(j)

            rhythm_extended.append(perm_part)
        

    variants = variant_generation(rhythm_extended)
    for v in variants:
        blocks.append(print_rhythm_from_variant(v, slur))


def create_blocks(b_size, i_range, slur, note_min_size, rest):
    
    combinations = sp.multiset_combinations(np.array(i_range), b_size)
    for c in combinations:
        for p in sp.multiset_permutations(c):
            create_blocks_from_rhythm(p, note_min_size, slur)

    for b in blocks:
        rest_p = int (np.random.random() * (len(b) - 1))
        for i, p in enumerate(b):
            if i == rest_p:
                if len(p) > 3:
                    if p[3] > 0:
                        continue
                if len(p) == 2:
                    p.append(None)
                    p.append(None)
                    p.append(True)
                elif len(p) == 3:
                    p.append(None)
                    p.append(True)
                elif len(p) == 4:
                    p.append(True)

create_blocks(5, [2, 3, 4, 5, 7], True, 2, True)


file_name = "patterns/generated_patterns.txt"

def format_row(row):
    formatted_row = []
    for item in row:
        if isinstance(item, list):
            formatted_row.append(f"[{','.join(map(str, item))}]")
        else:
            formatted_row.append(str(item))
    return ", ".join(formatted_row)

with open(file_name, 'w') as file:
    for block in blocks:
        file.write("**begin**\n")
        for row in block:
            row_str = format_row(row)
            file.write(f"{row_str}\n")
        file.write("**end**\n\n")

print(f"Data written to {file_name}")