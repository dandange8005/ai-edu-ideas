import re

file_path = "2023_06_22_101 101 creative ideas on using AI in Education.md"
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_regex = r'^##\s*(Author|Editor):'
print(f"Testing regex: {new_regex}")

matches = []
for i, line in enumerate(lines):
    if re.match(new_regex, line, re.IGNORECASE):
        matches.append(i)

print(f"Total matches: {len(matches)}")
print(f"Last 10 indices: {matches[-10:]}")

# Check specifically around 6180
print(f"Line 6180: {repr(lines[6179])}") # 0-indexed is 6179
print(f"Match 6180: {bool(re.match(new_regex, lines[6179], re.IGNORECASE))}")
