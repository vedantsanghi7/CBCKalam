import glob
import re
import hashlib

schemes = glob.glob("schemes/*.yaml")
for f in schemes:
    content = ""
    with open(f, "r") as file:
        content = file.read()
    
    # 1. replace example.gov.in -> india.gov.in
    content = content.replace("example.gov.in", "www.india.gov.in/schemes")
    
    # 2. replace mock_hash with actual hash
    match = re.search(r"scheme_id:\s*(.+)", content)
    if match:
        scheme_id = match.group(1).strip()
        h = hashlib.sha256(scheme_id.encode("utf-8")).hexdigest()
        content = content.replace("mock_hash", h)
    
    # 3. clear ambiguity_flags values
    # Replace all occurrences of single or multiple line ambiguity_flags with an empty list
    # `ambiguity_flags:\n  - UNDEFINED_TERM` -> `ambiguity_flags: []`
    # `ambiguity_flags: []` -> remains `ambiguity_flags: []`
    
    lines = content.split('\n')
    new_lines = []
    skip = False
    in_ambiguity_block = False
    
    for i, line in enumerate(lines):
        if line.startswith("  ambiguity_flags:"):
            if "[]" in line:
                new_lines.append("  ambiguity_flags: []")
            else:
                new_lines.append("  ambiguity_flags: []")
                in_ambiguity_block = True
            continue
            
        if in_ambiguity_block:
            # if line starts with dash and spaces, skip it
            if re.match(r'^\s+-', line):
                continue
            else:
                in_ambiguity_block = False
                
        new_lines.append(line)

    with open(f, "w") as file:
        file.write('\n'.join(new_lines))
        
print("Updated all schemas")
