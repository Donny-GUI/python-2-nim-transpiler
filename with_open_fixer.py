import re

def find_with_open_blocks(file_strings):
    with_open_pattern = re.compile(r'with\s+open\([^)]+\)\s+as\s+\w+:')
    
    matching_blocks = []

    for file_string in file_strings:
        matches = with_open_pattern.findall(file_string)
        matching_blocks.extend(matches)

    return matching_blocks

def count_leading_spaces(input_string):
    return len(input_string) - len(input_string.lstrip(' '))

def collect_till_end_of_block(strings: list[str]) -> list[str]:

    retv = [strings[0], ]
    original_indent = count_leading_spaces(strings[0])
    for line in strings[1:]:
        nextindent = count_leading_spaces(line)
        if nextindent > original_indent:
            retv.append(line)
        else:
            break
    return retv

def extract_file_info(input_string: str):
    
    stripped = input_string.strip("  ").split("with open(")[1].split(', "')
    fn = stripped[0]
    filemode, reference = stripped[1].split(")")
    filemode = filemode.split('"')[0]
    reference = reference.split("as ")[1].replace(":\n", "")
    return {"filename": fn, "reference": reference, "filemode": filemode}

def extract_first_quoted_string(input_string):
    match = re.search(r'"([^"]*)"', input_string)
    return match.group(1) if match else None

def replace_read(input_string):
    pattern = re.compile(r'(\w+)\s*=\s*(\w+)\.read\(\)')
    replacement = r'\1 = read_file(\2)'
    result = re.sub(pattern, replacement, input_string)
    return result

def replace_readlines(input_string):
    pattern = re.compile(r'(\w+)\s*=\s*(\w+)\.readlines\(\)')
    replacement = r'\1 = readLines(\2)'

    result = re.sub(pattern, replacement, input_string)
    return result

def replace_writelines(input_string):
    pattern = re.compile(r'(\w+)\s*=\s*(\w+)\.writelines\(\)')
    replacement = r'\1 = writeLines(\2)'

    result = re.sub(pattern, replacement, input_string)
    return result

def fix_nim_open_with(filepath: str):

    with open(filepath, "r") as r:
        lines = r.readlines()
    
    newlines = []
    lineiter = iter(lines)
    count = -1

    fullbreak = False
    
    while True:
        try:
            line = next(lineiter)
            count += 1
        except StopIteration:
            break

        newline = line
        linestripped = newline.strip(" ")

        # if it is an open block
        if linestripped.startswith("with open("):
            # get the entire block for the open with
            searchlines = lines[count:]
            block = collect_till_end_of_block(searchlines)
            print("[py2nim]: fixing ", "\n".join(block))
            
            block_line_count = len(block) - 1
            # get the file information, ie filemode, filename, reference
            fileinfo = extract_file_info(block[0])    

            if fileinfo["filemode"].startswith("r"):
                for index, blockline in enumerate(block[1:]):
                    newblockline = replace_readlines(blockline)
                    newblockline2 = replace_read(newblockline)
                    newlines.append(newblockline2[2:])

            elif fileinfo["filemode"].startswith("w"):
                for index, blockline in enumerate(block[1:]):
                    newblockline = replace_writelines(blockline)
                    newlines.append(newblockline[2:])
            
            # move the iterator
            fullbreak = False
            for i in range(0, block_line_count):
                try:
                    line = next(lineiter)
                    count += 1
                except StopIteration:
                    fullbreak = True
                    break
            
            continue

        newlines.append(line)

        if fullbreak == True:
            break
    
    with open(filepath, "w") as wfile:
        wfile.writelines(newlines) 

