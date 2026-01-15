import json
import os
import re

# Set path to the JSON file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDEAS_JSON_PATH = os.path.join(BASE_DIR, 'data', 'ideas.json')

THEME_KEYWORDS = {
    'Assessment & Feedback': [
        'feedback', 'assessment', 'rubric', 'grading', 'exam', 'marking', 
        'peer review', 'quiz', 'formative', 'summative', 'evaluation', 'evaluate'
    ],
    'Creative Arts': [
        'poetry', 'poem', 'art', 'song', 'drawing', 'literary', 'metaphor', 'design', 
        'creative', 'creativity', 'fiction', 'comic', 'story', 'museum', 'exhibition', 
        'visual', 'meme', 'character', 'animation', 'illustration'
    ],
    'Critical Literacy': [
        'critical', 'criticality', 'thinking', 'ethics', 'ethical', 'bias', 'reliability', 'literacy', 
        'stochastic', 'trust', 'integrity', 'authorship', 'veracity', 
        'unethical', 'discriminatory', 'feminism', 'citation', 'cite'
    ],
    'Language & Literature': [
        'translation', 'translate', 'language', 'grammar', 'phonetic', 'writing', 'write',
        'english', 'discourse', 'style', 'author', 'lyrics', 'poetry', 'literature'
    ],
    'Technical Skills': [
        'code', 'coding', 'java', 'uml', 'entrepreneur', 'startup', 
        'biotech', 'prototype', 'mathematics', 'maths', 'geogebra', 'programming', 
        'software', 'algorithm', 'api', 'data analysis', 'h5p', 'digital'
    ],
    'Research & Inquiry': [
        'research', 'interview', 'persona', 'query', 'investigation', 
        'socratic', 'discovery', 'inquiry', 'scientist', 'scholarly', 
        'literature review', 'thematic analysis', 'data'
    ],
    'Teaching Support': [
        'lesson', 'plan', 'mentor', 'scenarios', 'case study', 'curriculum', 
        'activity', 'activities', 'counsellor', 'pastoral', 'pedagogy', 'classroom', 
        'workshop', 'instructional', 'personalized learning', 'tutor', 'shadow teacher'
    ]
}

TAG_KEYWORDS = {
    'Visual': [
        'image', 'art', 'drawing', 'picture', 'illustration', 'video', 'comic', 
        'dall-e', 'midjourney', 'stable diffusion', 'visual', 'metaphor', 
        'portrait', 'animation', 'adobe', 'canva'
    ],
    'Textual': [
        'text', 'poem', 'poetry', 'essay', 'article', 'writing', 'lyrics', 
        'transcription', 'summary', 'citation', 'abstract', 'blog'
    ],
    'Conversational': [
        'chat', 'debate', 'interview', 'persona', 'buddy', 'mentor', 
        'conversation', 'socratic', 'role-play', 'facilitator'
    ],
    'Functional': [
        'code', 'logic', 'structure', 'functional', 'tool', 'rubric', 
        'feedback', 'translation', 'summary', 'guide', 'worksheet', 
        'formula', 'transcribe'
    ]
}

def get_word_score(text, keywords):
    score = 0
    for kw in keywords:
        # Use regex to find whole words to avoid partial matches like 'art' in 'artificial'
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, text):
            score += 1
    return score

def determine_theme(idea):
    full_text = f"{idea.get('title', '')} {idea.get('my_idea', '')} {idea.get('what_i_aim_to_achieve', '')}".lower()
    
    scored_themes = []
    for theme, keywords in THEME_KEYWORDS.items():
        score = get_word_score(full_text, keywords)
        if score > 0:
            scored_themes.append((theme, score))
    
    if not scored_themes:
        return "Teaching Support"
        
    # Sort by score DESC, and then by theme name so we have deterministic tie-breaking
    scored_themes.sort(key=lambda x: (-x[1], x[0]))
    return scored_themes[0][0]

def determine_tags(idea):
    # For tags we also check tools_used
    full_text = f"{idea.get('title', '')} {idea.get('my_idea', '')} {idea.get('tools_used', '')}".lower()
    
    tags = []
    for tag, keywords in TAG_KEYWORDS.items():
        if get_word_score(full_text, keywords) > 0:
            tags.append(tag)
    
    return tags

def enrich_data():
    if not os.path.exists(IDEAS_JSON_PATH):
        print(f"Error: {IDEAS_JSON_PATH} not found.")
        return

    with open(IDEAS_JSON_PATH, 'r', encoding='utf-8') as f:
        ideas = json.load(f)

    print(f"Enriching {len(ideas)} ideas with word boundaries...")

    for idea in ideas:
        idea['theme'] = determine_theme(idea)
        idea['tags'] = determine_tags(idea)

    with open(IDEAS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(ideas, f, indent=2, ensure_ascii=False)

    print("Enrichment complete! Updated ideas.json")

if __name__ == "__main__":
    enrich_data()
