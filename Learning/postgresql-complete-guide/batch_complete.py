#!/usr/bin/env python3
import glob

# Get list of files needing content
files = glob.glob("*.md")
files = [f for f in files if f not in ['README.md', 'STATUS.md']]
files.sort()

placeholder_files = []
for file in files:
    with open(file, 'r') as f:
        content = f.read()
        if 'This section covers advanced PostgreSQL concepts' in content or len(content) < 500:
            placeholder_files.append(file)

print(f"Files needing content: {len(placeholder_files)}")
for f in placeholder_files:
    print(f)
