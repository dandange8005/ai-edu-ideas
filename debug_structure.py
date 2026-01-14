
def analyze_structure(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    author_indices = [i for i, line in enumerate(lines) if line.strip().startswith("## Author:")]
    
    print(f"Found {len(author_indices)} Author blocks.")
    
    # Check context before each author block
    for idx in author_indices:
        # Look back up to 20 lines for a number
        found = False
        context = []
        for i in range(idx - 1, max(-1, idx - 20), -1):
            line = lines[i].strip()
            if not line: continue
            
            # Check if line starts with a number
            parts = line.split(' ', 1)
            if parts[0].isdigit():
                print(f"Author at {idx+1} -> Found Header: '{line}' at line {i+1}")
                found = True
                break
            context.append(line)
        
        if not found:
            print(f"Author at {idx+1} -> NO numbered header found. Context: {context[:3]}...")

if __name__ == "__main__":
    analyze_structure("/Users/nanzhang/Developer/Github Repos/ai-edu-ideas/2023_06_22_101 101 creative ideas on using AI in Education.md")
