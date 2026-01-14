import re
import json
import os

def clean_text(text):
    if not text:
        return ""
    # Remove form feeds and normalize whitespace
    text = text.replace('\f', '')
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing chunks of footers that might have survived
    text = re.sub(r'Idea \d+ / 101 Creative ideas.*', '', text, flags=re.I)
    return text.strip()

def extract_ideas_v3(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pages = content.split('\f')
    ideas = []
    
    # Improved regex markers for better matching
    markers = {
        r'Authors?(\(s\))?([: ]|$)': "author",
        r'Roles?([: ]|$)': "role",
        r'Institutions?/organisations?([: ]|$)': "institution",
        r'Contexts?([: ]|$)': "context",
        r'Tools?(\(s\))? used([: ]|$)': "tools_used",
        r'(My|Our) ideas?([: ]|$)': "my_idea",
        r'What (I|we) aims? to achieve([: ]|$)': "aims",
        r'Where (the )?inspiration comes from([: ]|$)': "inspiration",
        r'Contact details?([: ]|$)': "contact_details"
    }

    for page in pages:
        all_lines = page.split('\n')
        lines = [line.strip() for line in all_lines if line.strip()]
        if not lines: continue
        
        page_ideas = []
        for i, line in enumerate(lines):
            if re.match(r'^\d+$', line):
                num = int(line)
                if 1 <= num <= 101:
                    title = lines[i+1] if i+1 < len(lines) else "Unknown"
                    if re.match(r'^\d+$', title) or any(re.search(m, title, re.I) for m in markers):
                        title = "Unknown Title"
                    page_ideas.append({"number": str(num).zfill(2), "title": title, "start_line": i})

        if not page_ideas:
            continue

        footer_pattern = re.compile(r'Idea \d+ / 101 Creative ideas', re.IGNORECASE)
        footer_indices = [i for i, line in enumerate(lines) if footer_pattern.search(line)]
        
        blocks = []
        if len(footer_indices) > 1:
            last_idx = 0
            for f_idx in footer_indices:
                blocks.append(lines[last_idx:f_idx+1])
                last_idx = f_idx + 1
            if last_idx < len(lines):
                blocks.append(lines[last_idx:])
        else:
            blocks = [lines]

        for i, block in enumerate(blocks):
            if i < len(page_ideas):
                num = page_ideas[i]["number"]
                title = page_ideas[i]["title"]
            else:
                num = None
                for line in block:
                    if re.match(r'^\d+$', line):
                        val = int(line)
                        if 1 <= val <= 101:
                            num = str(val).zfill(2)
                            break
                if not num: continue
                title = "Unknown"

            idea_data = {
                "number": num,
                "title": title,
                "author": "",
                "role": "",
                "institution": "",
                "context": "",
                "tools_used": "",
                "my_idea": "",
                "aims": "",
                "inspiration": "",
                "contact_details": ""
            }

            current_field = None
            buffer = []

            for line in block:
                found_marker = False
                for marker_pattern, field in markers.items():
                    match = re.search(marker_pattern, line, re.IGNORECASE)
                    if match:
                        if current_field and buffer:
                            idea_data[current_field] = clean_text(" ".join(buffer))
                        current_field = field
                        buffer = []
                        content_after = line[match.end():].strip()
                        if content_after: buffer.append(content_after)
                        found_marker = True
                        break
                
                if not found_marker:
                    if current_field:
                        if not footer_pattern.search(line):
                            buffer.append(line)

            if current_field and buffer:
                idea_data[current_field] = clean_text(" ".join(buffer))
            
            # Post-processing heuristic:
            # If author is empty and my_idea starts with what looks like a name (2-3 words capitalized)
            # and describes the author, move it.
            if not idea_data["author"] and idea_data["my_idea"]:
                desc = idea_data["my_idea"]
                # Match first 2-3 capitalized words
                name_match = re.match(r'^([A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)?)\s+(.*)', desc)
                if name_match:
                    idea_data["author"] = name_match.group(1)
                    idea_data["my_idea"] = name_match.group(2)

            ideas.append(idea_data)

    final_ideas = {}
    for idea in ideas:
        num = idea["number"]
        score = sum(len(str(v)) for v in idea.values())
        if num not in final_ideas or score > final_ideas[num]["score"]:
            final_ideas[num] = {"data": idea, "score": score}

    return [final_ideas[num]["data"] for num in sorted(final_ideas.keys())]

if __name__ == "__main__":
    input_file = "/Users/nanzhang/Developer/Github Repos/ai-edu-ideas/exports/101_creative_ideas_on_using_AI_in_Education.md"
    output_file = "/Users/nanzhang/Developer/Github Repos/ai-edu-ideas/data/ideas.json"
    
    extracted_ideas = extract_ideas_v3(input_file)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_ideas, f, indent=4)
        
    print(f"Successfully extracted {len(extracted_ideas)} ideas to {output_file}.")
