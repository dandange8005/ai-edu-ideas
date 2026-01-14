import json

with open('ideas.json', 'r') as f:
    ideas = json.load(f)

numbers = set()
for idea in ideas:
    # Use 'CorrectNumber' if available, otherwise 'number'
    num = idea.get('CorrectNumber')
    if num is None:
        num = idea.get('number')
    if num is None:
        num = idea.get('Number')
    
    if num is not None:
        try:
            numbers.add(int(num))
        except:
            pass

expected = set(range(1, 102)) # 1 to 101
missing = sorted(list(expected - numbers))

print(f"Total extracted: {len(ideas)}")
print(f"Extracted numbers count: {len(numbers)}")
print(f"Missing numbers: {missing}")

# Also check for duplicates
seen = set()
duplicates = []
for n in numbers:
    if n in seen:
        duplicates.append(n)
    seen.add(n)
if duplicates:
    print(f"Duplicate numbers: {duplicates}")
