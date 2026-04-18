import os
import glob
import json
import bs4
import pdfplumber

CACHE_DIR = os.path.join(os.path.dirname(__file__), "_cache")

def parse_html(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        soup = bs4.BeautifulSoup(f.read(), 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.extract()
        
    text = soup.get_text(separator=' ', strip=True)
    return text

def parse_pdf(filepath):
    text_chunks = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_chunks.append(text)
    except Exception as e:
        print(f"Error parsing PDF {filepath}: {e}")
        return ""
    return "\n\n".join(text_chunks)

def main():
    if not os.path.exists(CACHE_DIR):
        print("No cache directory found.")
        return
        
    for meta_file in glob.glob(os.path.join(CACHE_DIR, "*.meta.json")):
        base_name = meta_file.replace(".meta.json", "")
        md_file = base_name + ".md"
        
        # Determine source file
        src_file = None
        if os.path.exists(base_name + ".html"):
            src_file = base_name + ".html"
        elif os.path.exists(base_name + ".pdf"):
            src_file = base_name + ".pdf"
            
        if not src_file:
            print(f"No source file found for {base_name}")
            continue
            
        if os.path.exists(md_file):
            # Already parsed
            continue
            
        print(f"Parsing {src_file} -> {md_file}")
        
        md_text = ""
        if src_file.endswith(".html"):
            md_text = parse_html(src_file)
        elif src_file.endswith(".pdf"):
            md_text = parse_pdf(src_file)
            
        if md_text:
            with open(md_file, "w", encoding='utf-8') as f:
                f.write(md_text)
        else:
            print(f"Warning: No text extracted from {src_file}")

if __name__ == "__main__":
    main()
