
FunctionMap = {
    'datetime.datetime.now': 'now()',
    'datetime.datetime.utcnow': 'utcNow()',
    'datetime.datetime.combine': 'discard',  # Nim doesn't have a direct equivalent; consider creating a new datetime object manually
    'datetime.datetime.fromtimestamp': 'epochTimeToLocalTime',
    'datetime.datetime.utcfromtimestamp': 'epochTimeToUtcTime',
    'datetime.datetime.fromisoformat': 'parseDateTimeIso8601',
    'datetime.datetime.strptime': 'parseDateTime',
    'datetime.timedelta': 'Duration',
    'datetime.timedelta.total_seconds': 'toSeconds',
    'datetime.timedelta.days': 'days',
    'datetime.timedelta.seconds': 'seconds',
    'datetime.timedelta.microseconds': 'microseconds',
    'datetime.date.today': 'getLocalTime().year, getLocalTime().month, getLocalTime().day',
    'datetime.date.fromtimestamp': 'epochTimeToDate',
    'datetime.date.fromisoformat': 'discard',  # Nim doesn't have a direct equivalent; consider parsing manually
    'datetime.date.strftime': 'formatTime',
    'datetime.time': 'Time',
    'datetime.time.replace': 'discard',  # Nim doesn't have a direct equivalent; consider creating a new time object manually
    'datetime.time.isoformat': 'formatTime',
    'datetime.time.strftime': 'formatTime',
}

def fix_datetime_modules(filepath: str):
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
    
