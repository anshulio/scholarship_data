import json
import re

def clean_all_text(text):
    if not text: return ""
    
    # 1. Remove HTML tags like <br> or <div>
    text = re.sub(r'<[^>]+>', '', text)
    
    # 2. Remove Markdown Bold/Italic markers (**text**, __text__, *text*)
    # This specifically removes the stars from the Benefit section
    text = re.sub(r'(\*\*|__|\*)', '', text)
    
    # 3. Remove Markdown Headers (e.g., # Header, ## Subheader)
    text = re.sub(r'#+\s?', '', text)
    
    # 4. Remove Markdown List bullets from the start of lines (- item, * item, + item)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    
    # 5. Remove Numbered list markers (e.g., 1. item, 2. item)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # 6. Clean up hitespace
    text = re.sub(r'\n\s*\n', '\n', text) 
    return text.strip()

def parse_md_to_list(text):
    """
    Splits markdown text into a clean Python list for array fields 
    like 'eligibility', 'docs', and 'process'.
    """
    if not text: return []
    # Clean the text first to remove stars and bullets
    cleaned = clean_all_text(text)
    # Split by newline and remove empty entries
    return [line.strip() for line in cleaned.split('\n') if line.strip()]

def generate_cleaned_json(json_list):
    # --- DEBUGGING: Check what we actually received ---
    has_basic = any('basicDetails' in obj.get('data', {}).get('en', {}) for obj in json_list)
    has_faqs = any('faqs' in obj.get('data', {}).get('en', {}) for obj in json_list)
    
    if not has_basic:
        print("DEBUG: Could not find 'basicDetails' in the provided JSON list.")
    if not has_faqs:
        print("DEBUG: Could not find 'faqs' in the provided JSON list.")

    try:
        # Identify the block containing core scholarship details
        # We use .get() and default to {} to prevent crashing if keys are missing
        main_block = next((obj for obj in json_list if 'basicDetails' in obj.get('data', {}).get('en', {})), None)
        
        if main_block:
            main_data = main_block['data']['en']
            basic = main_data.get('basicDetails', {})
            content = main_data.get('schemeContent', {})
            scheme_id = main_block.get('data', {}).get('_id', "")
            slug = main_block.get('data', {}).get('slug', "")
        else:
            # Fallback if basicDetails block is missing
            main_data, basic, content, scheme_id, slug = {}, {}, {}, "", ""

        # Identify the block containing FAQ data
        faq_block = next((obj for obj in json_list if 'faqs' in obj.get('data', {}).get('en', {})), None)
        faqs_raw = faq_block['data']['en'].get('faqs', []) if faq_block else []
        
    except Exception as e:
        print(f"Extraction Error: {e}")
        # We no longer 'raise' the error, we just use empty data to keep the script running
        main_data, basic, content, faqs_raw, scheme_id, slug = {}, {}, {}, [], "", ""

    # Safe extraction helpers
    nodal_dept = basic.get('nodalDepartmentName') or {}
    state_info = basic.get('state') or {}
    level_info = basic.get('level') or {}

    doc_raw = next((obj['data']['en'].get('documentsRequired_md', "") 
                   for obj in json_list if 'documentsRequired_md' in obj.get('data', {}).get('en', {})), "")

    cleaned_doc = {
        "schemeId": scheme_id,
        "slug": slug,
        "title": basic.get('schemeName', "Untitled Scholarship"),
        "state": state_info.get('label', "National"),
        "authority": (level_info.get('label', "Other")).replace('/ UT', '').strip() + " Government",
        "dept": nodal_dept.get('label', "").strip(),
        "briefDescription": content.get('briefDescription', ""),
        "detailedDescription": clean_all_text(content.get('detailedDescription_md', "")),
        "benefits": clean_all_text(content.get('benefits_md', "")),
        "amount": clean_all_text(content.get('benefits_md', "")),
        "tags": basic.get('tags', []),
        "link": (content.get('references', [{}])[0] or {}).get('url', ""),
        "deadline": "Open All Year", 
        "img": "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=800",
        "eligibility": parse_md_to_list(main_data.get('eligibilityCriteria', {}).get('eligibilityDescription_md', "")),
        "docs": parse_md_to_list(doc_raw),
        "process": parse_md_to_list(main_data.get('applicationProcess', [{}])[0].get('process_md', "")),
        "faqs": [{"q": f.get('question', ""), "a": clean_all_text(f.get('answer_md', ""))} for f in faqs_raw]
    }

    return cleaned_doc

def load_multiple_json(filepath):
    """Handles files containing multiple JSON objects {}{}{}."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    decoder = json.JSONDecoder()
    pos = 0
    objs = []
    while pos < len(content.strip()):
        obj, pos_inc = decoder.raw_decode(content, pos)
        objs.append(obj)
        pos = pos_inc
        while pos < len(content) and content[pos].isspace():
            pos += 1
    return objs