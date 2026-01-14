import json

with open('ideas.json', 'r') as f:
    ideas = json.load(f)

print(f"Total ideas: {len(ideas)}")
for i, idea in enumerate(ideas[-5:]):
    print(f"--- Idea {len(ideas)-5+i+1} ---")
    print(f"Number: {idea.get('number')}")
    print(f"CorrectNumber: {idea.get('CorrectNumber')}")
    print(f"Author: {idea.get('Author')}")
    print(f"Title: {idea.get('Title')}")
    # Print start of description to check if it captured bio
    desc = idea.get('Description', '')
    if desc:
        print(f"Description (first 100 chars): {desc[:100]}...")
    else:
        print("Description: [EMPTY]")
        
    # Check Role/Institution for bio
    print(f"Role: {idea.get('Role')}")
