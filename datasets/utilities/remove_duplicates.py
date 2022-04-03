import re
import json
import os
import sys
from pathlib import Path


def replace_in_asm (asm):
    # Given the asm, return a string
    # in which every address/offset is replaced with a string

    pattern = r'\b0x\w+'
    replacement = 'XXXXXXX'

    returned_string =''
  
    for block in asm:
        current_block = asm[block]
        for instruction in current_block:
            instruction_code = current_block[instruction]['code']       
            if re.findall(pattern, instruction_code):
                    new_instruction = re.sub(pattern, replacement, instruction_code)
                    returned_string += ' '+new_instruction
            else:
                returned_string += ' '+instruction_code
    return returned_string


def find_duplicates(functions, unique_fnct_file, duplicate_fnct_file):
    unique_funct_ids = []
    duplicate_funct_ids = []
    checked_functions = set()
    for function in functions:
        with open(function) as jsonFile:
                loaded_funct = json.load(jsonFile)
                jsonFile.close()             
                asm_function = replace_in_asm(loaded_funct['asm'])
                id_function = function.split('/')[-1].split('.json')[0]
        if asm_function not in checked_functions:
            checked_functions.add(asm_function)
            unique_funct_ids.append(id_function)
        else:
            duplicate_funct_ids.append(id_function)
    f = open(duplicate_fnct_file,'w+')
    f.write('\n'.join(str(id) for id in duplicate_funct_ids))
    f.close()
    f = open(unique_fnct_file,'w+')
    f.write('\n'.join(str(id) for id in unique_funct_ids))
    f.close()

def move_duplicates(duplicates, functions_folder, duplicates_output_folder):
    Path(duplicates_output_folder).mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(functions_folder, topdown=False):      
        for file in files:
            id = file.split('\n')[0].split('.json')[0]
            current_path = os.path.join(root, file)
            if os.path.isfile(current_path) and id in duplicates:
                new_path = os.path.join(duplicates_output_folder, file)
                Path(current_path).rename(new_path)

if __name__ == '__main__':
    
    functions = []
    # sys.argv[1]: path of json files to be analyzed

    for root, dirs, files in os.walk(sys.argv[1], topdown=False):
        for file in files:
            current_path = os.path.join(root, file)
            if os.path.isfile(current_path) and current_path.endswith('.json'):
                functions.append(current_path)
    unique_funct_file = 'unique_functions.txt'
    duplicate_funct_file = 'duplicate_functions.txt'

    find_duplicates(functions, unique_funct_file, duplicate_funct_file)


    f = open(duplicate_funct_file, 'r')
    duplicates = f.readlines()
    f.close()
    duplicates = [duplicate.split('\n')[0] for duplicate in duplicates]
    move_duplicates(duplicates, sys.argv[1], f'{sys.argv[1]}/duplicates') # move duplicates to another folder, to be removed




