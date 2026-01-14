import re
import json

def extract_ideas(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # ---------------------------------------------------------
    # PASS 1: Author-Based Extraction
    # ---------------------------------------------------------
    
    # 1. Provide "Regions" based on Author blocks
    # Each region i ends at Author i. Starts at Author i-1 (end).
    
    author_indices = []
    for i, line in enumerate(lines):
        if re.match(r'^##\s*(Author|Editor):', line, re.IGNORECASE):
            author_indices.append(i)
    
    # Add dummy end
    # regions = list of (start_line, author_line)
    
    # Iterate through author blocks
    raw_ideas = []
    header_pattern = re.compile(r'^(\d+)[ .:]+(.*)')
    # Alt header: ## Title
    alt_header_pattern = re.compile(r'^##\s+(.*)')
    # metadata_keys used for heuristic title detection (if needed) but parsed in parse_idea_block
    
    for i in range(len(author_indices)):
        start_idx = author_indices[i]
        # End is next author or EOF
        if i < len(author_indices) - 1:
            end_idx = author_indices[i+1]
        else:
            end_idx = len(lines)
            
        region_lines = lines[start_idx:end_idx]
        
        # Parse metadata immediately to get Author/Role etc
        data = parse_idea_block(region_lines)
        
        # Find Title
        # 1. Check for Numbered Header
        found_title = None
        found_num = None
        
        for line in region_lines:
            sline = line.strip()
            if not sline: continue
            
            # Check Numbered
            m = header_pattern.match(sline)
            if m:
                try:
                    num = int(m.group(1))
                    if num < 200: # Sanity check
                        found_num = num
                        found_title = m.group(2).strip()
                        break
                except: pass
                
            # Check for "My idea" line if no numbered header found yet?
            # Or reliance on metadata?
            
        # If no numbered header, use Implied Title
        if not found_title:
            # Implied: Name or first non-empty/non-marker line?
            # But parse_idea_block consumes markers.
            # Maybe use 'data' to guess?
            # If "My idea" in data, maybe title is generic?
            # Let's assume title is "Idea X" if unknown, or try to find a meaningful line.
            
            # For Editors, Title should be their Name (Author).
            if data.get('Author'):
                found_title = data.get('Author')
            else:
                found_title = "Unknown Title"
        
        if found_num is None:
            # Sequential inference
            # If we are at index i, and we assume 1-based.
            # But duplicate authors might exist?
            # Just use i + 1 for now.
            found_num = i + 1

        idea = {
            'Number': found_num,
            'Title': found_title,
            'start_line': start_idx,
            'author_line': start_idx, # Author is at start now
            'end_line': end_idx
        }
        idea.update(data) # Add metadata
        raw_ideas.append(idea)

    return raw_ideas

    # ---------------------------------------------------------
    # PASS 3: Renumbering / Anomaly Fix
    # ---------------------------------------------------------
    # Now we have a list of ideas.
    # Force sequential numbering 1..N
    # But respect explicit numbers if they imply we skipped something effectively?
    # Actually, simpler: Just renumber 1 to len(final_ideas).
    # Why? Because if "1. Providing feedback" was Idea 5, it IS the 5th idea in the list.
    # The file structure (Author blocks) preserves order.
    # The only risk is if we *missed* an idea entirely (no author, no number).
    # But we did a Gap Scan.
    
    # Let's trust the Order.
    for idx, idea in enumerate(final_ideas):
        idea['CorrectNumber'] = idx + 1
        
        # If original number was None, use CorrectNumber.
        # If original number was WAY OFF (e.g. 1 instead of 5), use CorrectNumber.
        # If original number matches CorrectNumber, great.
        
        # Update metadata
        # Extract full metadata
        start = idea['start_line']
        auth = idea['author_line']
        end = idea['end_line']
        
        meta_start = auth if auth != -1 else start
        
        meta_chunk = lines[meta_start:end]
        data = parse_idea_block(meta_chunk)
        
        data['Number'] = idea['CorrectNumber']
        # If 'Title' in event was just "1.", we might want to look deeper? 
        # But 'title' captured the text after regex. "Providing feedback". So it's good.
        data['Title'] = idea['title']
        
        # If title is "Implied Title" and Description is empty, assume title text IS description too?
        # (Already handled in extraction logic implicitly)
        
        # Update idea object with data
        idea.update(data)
        
        # Consolidate Aim if present
        # If we found "What I aim to achieve" or "Aim:", ensure it is stored.
        # The parse_idea_block handles this mapping.

    return final_ideas

def parse_idea_block(lines):
    data = {}
    current_key = None
    buffer = []
    
    markers = {
        "## Author:": "Author",
        "## Editor:": "Author",
        "## Role:": "Role",
        "## Institution/organisation:": "Institution",
        "## Context:": "Context",
        "## Aim:": "Aim",
        "## Tool(s) used:": "Tools",
        "## My idea": "Description",
        "## Contact details:": "Contact",
        "## Keywords": "Keywords",
        "## Where the inspiration comes from": "Inspiration",
        "## What I aim to achieve": "Aim"
    }
    
    for line in lines:
        stripped = line.strip()
        is_marker = False
        for marker, key in markers.items():
            if stripped.startswith(marker):
                if current_key:
                    data[current_key] = "\n".join(buffer).strip()
                current_key = key
                buffer = []
                content_after = stripped[len(marker):].strip()
                if content_after: buffer.append(content_after)
                is_marker = True
                break
        
        if not is_marker:
            if current_key:
                if stripped: buffer.append(stripped)
    
    if current_key:
        data[current_key] = "\n".join(buffer).strip()

    # Image
    for line in lines:
        if "![" in line and "](" in line:
             data['Image_Line'] = line.strip()
             break
             
    return data

if __name__ == "__main__":
    file_path = "/Users/nanzhang/Developer/Github Repos/ai-edu-ideas/2023_06_22_101 101 creative ideas on using AI in Education.md"
    ideas = extract_ideas(file_path)
    print(f"Extracted {len(ideas)} ideas.")
    with open('ideas.json', 'w', encoding='utf-8') as f:
        json.dump(ideas, f, indent=4)
