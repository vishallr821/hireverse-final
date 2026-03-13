import pdfplumber
import docx
import os
import re

SKILLS_KEYWORDS = [
    'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue', 'Node.js', 
    'Django', 'Flask', 'FastAPI', 'Spring', 'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 
    'Redis', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'Linux', 'REST', 
    'GraphQL', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 
    'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'C', 'C++', 'C#', 
    'Go', 'Rust', 'Swift', 'Kotlin', 'Flutter', 'React Native', 'HTML', 'CSS', 
    'Tailwind', 'Bootstrap', 'Jenkins', 'CI/CD', 'Terraform', 'Ansible', 'Spark', 
    'Hadoop', 'Kafka', 'Elasticsearch', 'OpenCV', 'BERT', 'GPT', 'LLM', 'RAG', 
    'LangChain', 'Pinecone', 'ChromaDB', 'Tableau', 'PowerBI', 'Excel', 'R', 
    'MATLAB', 'Unity', 'Unreal', 'PHP', 'Laravel', 'Ruby', 'Rails', 'Scala', 
    'Hive', 'Airflow', 'dbt', 'Snowflake', 'Databricks'
]

def clean_text(text: str) -> str:
    """Removes excessive whitespace, special characters, normalizes newlines"""
    if not text:
        return ""
    # Replace multiple whitespaces/newlines with single ones
    text = re.sub(r'\s+', ' ', text)
    # Remove some non-standard characters but keep punctuation
    text = re.sub(r'[^\x00-\x7f]', r'', text)
    return text.strip()

def extract_text_from_pdf(file_path: str) -> str:
    """Uses pdfplumber to extract text from all pages"""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return clean_text(text)

def extract_text_from_docx(file_path: str) -> str:
    """Uses python-docx to extract text from all paragraphs"""
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return clean_text(text)

def extract_skills_from_text(text: str) -> list:
    """Returns list of matched skills found in text (case-insensitive)"""
    found_skills = []
    text_lower = text.lower()
    for skill in SKILLS_KEYWORDS:
        # Match using word boundaries to avoid partial matches like 'C' in 'CAT'
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    return found_skills

def extract_email(text: str) -> str:
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else ''

def extract_phone(text: str) -> str:
    patterns = [
        r'\+91[\s\-]?[6-9]\d{9}',
        r'[6-9]\d{9}',
        r'\d{10}',
        r'\+\d{1,3}[\s\-]?\d{10}'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return ''

def extract_name(text: str, filename: str) -> str:
    lines = [l.strip() for l in text.split('\n') 
             if l.strip()]
    
    for line in lines[:10]:
        words = line.split()
        if (2 <= len(words) <= 4 and
            all(w.replace('.','').isalpha() 
                for w in words) and
            not any(w.lower() in [
                'resume', 'curriculum', 'vitae',
                'cv', 'profile', 'email', 'phone',
                'mobile', 'address', 'objective'
            ] for w in words) and
            line[0].isupper()):
            return line.title()
    
    name = filename.replace('_', ' ')
    name = name.replace('-', ' ')
    for word in ['resume', 'cv', 'Resume', 
                 'CV', 'final', 'new']:
        name = name.replace(word, '')
    name = re.sub(r'\.(pdf|docx|doc)$', '', 
                  name, flags=re.IGNORECASE)
    return name.strip().title()

def parse_resume(file_path: str) -> dict:
    """Detects file extension and extracts text and skills"""
    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""
    
    if ext == '.pdf':
        raw_text = extract_text_from_pdf(file_path)
    elif ext == '.docx':
        raw_text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    skills = extract_skills_from_text(raw_text)
    
    return {
        'raw_text': raw_text,
        'skills': skills,
        'email': extract_email(raw_text),
        'phone': extract_phone(raw_text),
        'name': extract_name(raw_text, os.path.basename(file_path)),
        'file_type': ext[1:]
    }
