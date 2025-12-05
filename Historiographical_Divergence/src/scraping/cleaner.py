"""
Text cleaning logic for Lincoln documents.
Removes archival metadata and extracts core content.
"""
import re

def clean_loc_content(doc_type: str, content: str, title: str) -> str:
    """Master cleaning function that routes to specific cleaners."""
    if not content:
        return ""
        
    # specific handling for Second Inaugural (it has unique structure)
    if "Second Inaugural" in title:
        return _clean_second_inaugural(content)
        
    # specific handling for Gettysburg
    if "Gettysburg" in title:
        return _clean_gettysburg(content)
        
    # General Letter Cleaning
    if doc_type == "Letter":
        return _clean_letter(content)
        
    # Default fallback
    return _general_cleanup(content)

def _clean_second_inaugural(text: str) -> str:
    """Extracts only the 'Printed Reading Copy' section."""
    # The document has two versions. We want the final reading copy.
    marker = "Printed Reading Copy"
    if marker in text:
        # Split and take the part after the marker
        parts = text.split(marker)
        target_text = parts[-1]
        
        # Remove the intro note "5 Whether Lincoln planned..."
        # Look for the start of the actual speech "FELLOW COUNTRYMEN:"
        start_marker = "FELLOW COUNTRYMEN:"
        if start_marker in target_text:
            start_idx = target_text.find(start_marker)
            target_text = target_text[start_idx:]
            
        # Cut off the revision notes at the end
        # "6 Lincoln made a great many changes..."
        end_marker = "6 Lincoln made"
        if end_marker in target_text:
            target_text = target_text.split(end_marker)[0]
            
        return _general_cleanup(target_text)
    
    return _general_cleanup(text)

def _clean_gettysburg(text: str) -> str:
    """Removes LoC footer menus."""
    # Cut off at "Connect with the Library"
    end_marker = "Connect with the Library"
    if end_marker in text:
        text = text.split(end_marker)[0]
    return _general_cleanup(text)

def _clean_letter(text: str) -> str:
    """Removes LoC headers from letters."""
    lines = text.split('\n')
    clean_lines = []
    
    # Common metadata headers to skip
    skip_phrases = [
        "Abraham Lincoln papers:",
        "Selected and converted",
        "Washington, DC",
        "Preceding element",
        "For more information about",
        "Copyright status",
        "This transcription is intended",
        "From Abraham Lincoln to", # We will keep the content, not this header
        "From Robert S. Chew",
        "http://",
        "Citations are generated",
        "Chicago citation style",
        "Download"
    ]
    
    start_collecting = False
    
    # Heuristic: Start collecting when we see a Date line or Salutation
    # Or just skip the known garbage lines
    for line in lines:
        line = line.strip()
        if not line: continue
        
        is_metadata = False
        for phrase in skip_phrases:
            if phrase.lower() in line.lower():
                is_metadata = True
                break
        
        if not is_metadata:
            clean_lines.append(line)
            
    return "\n".join(clean_lines)

def _general_cleanup(text: str) -> str:
    """Standard whitespace normalization."""
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove [notes] often found in transcripts
    # text = re.sub(r'\[.*?\]', '', text) 
    return text.strip()