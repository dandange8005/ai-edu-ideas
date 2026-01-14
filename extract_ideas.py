import re
import json

def extract_ideas(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.readlines()

    ideas = []
    
    # helper to find fields
    def find_field(lines, field_name):
        for i, line in enumerate(lines):
            if field_name.lower() in line.lower() and (line.strip().startswith('##') or line.strip().startswith('**') or line.strip().endswith(':')):
                # Found the header, now get the content
                # Content might be on the same line or next lines
                content_start = i + 1
                content_lines = []
                for j in range(content_start, len(lines)):
                    l = lines[j].strip()
                    if l.startswith('##') or l.startswith('**Author'): # Stop at next header
                        break
                    if l and not l.startswith('!['): # Skip empty lines and images
                        content_lines.append(l)
                return " ".join(content_lines).strip()
        return None

    # Find all Author start indices
    author_indices = [i for i, line in enumerate(content) if '## Author:' in line or '**Author:**' in line]
    
    print(f"Found {len(author_indices)} potential author blocks.")

    for i, start_index in enumerate(author_indices):
        # Searching backwards from Author to find the Title
        title_index = -1
        # Look back up to 50 lines for a line starting with a number
        for j in range(start_index - 1, max(0, start_index - 100), -1): # Increased scan range
            line = content[j].strip()
            if re.match(r'^#* ?\d+\.?\s+\w+', line):
                title_index = j
                break
        
        # Block start: if Title found, use it. Else start_index - 20 
        block_start = title_index if title_index != -1 else max(0, start_index - 20)
        
        # Block end: next author index - buffer, or end of file
        if i < len(author_indices) - 1:
            next_start = author_indices[i+1]
            block_end = next_start - 10 # rough guess
        else:
            block_end = len(content)
            
        block_lines = content[block_start:block_end]
        
        # Extract fields
        author = find_field(block_lines, 'Author')
        role = find_field(block_lines, 'Role')
        institution = find_field(block_lines, 'Institution')
        context = find_field(block_lines, 'Context')
        tools = find_field(block_lines, 'Tool')
        idea = find_field(block_lines, 'My idea') or find_field(block_lines, 'Idea')
        aim = find_field(block_lines, 'What I aim to achieve')
        inspiration = find_field(block_lines, 'inspiration')
        
        # Title logic
        title = content[title_index].strip() if title_index != -1 else "Unknown Title"
        if title_index != -1:
            title = title.lstrip('#').strip()
        
        idea_obj = {
            "id": i + 1,
            "title": title,
            "author": author,
            "role": role,
            "institution": institution,
            "context": context,
            "tools": tools,
            "description": idea,
            "aim": aim,
            "inspiration": inspiration
        }
        ideas.append(idea_obj)

    with open('ideas.json', 'w', encoding='utf-8') as f:
        json.dump(ideas, f, indent=4)
        
    print(f"Extracted {len(ideas)} ideas to ideas.json")

if __name__ == "__main__":
    extract_ideas('2023_06_22_101 101 creative ideas on using AI in Education.md')
