
FunctionMap = {
    'time.time': 'epochTime',
    'time.gmtime': 'getGmTime',
    'time.localtime': 'getLocalTime',
    'time.mktime': 'localTimeToEpochTime',
    'time.asctime': 'asctime',
    'time.ctime': 'ctime',
    'time.sleep': 'sleep',
    'time.strftime': 'formatTime',
}


def fix_time_modules(filepath: str):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    modified_lines = []

    for line in lines:
        modified_line = line
        
        for name, value in FunctionMap.items():
            modified_line = modified_line.replace(name, value)
        
        modified_lines.append(modified_line)
  
    with open(filepath, "w") as wfile:
        wfile.writelines(modified_lines)
    