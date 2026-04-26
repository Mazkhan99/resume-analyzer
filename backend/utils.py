import re

# Skills database
TECH_SKILLS = {
    "critical": [
        "python", "java", "c++", "c#", "javascript", "typescript", "ruby", "php", "go", "swift", "kotlin",
        "sql", "mysql", "postgresql", "mongodb", "nosql", "machine learning", "deep learning", "nlp", 
        "computer vision", "data science", "data structures", "algorithms", "system design"
    ],
    "optional": [
        "redis", "elasticsearch", "cassandra", "html", "css", "react", "angular", "vue", "node.js", 
        "express", "django", "flask", "spring", "asp.net", "pandas", "numpy", "scikit-learn",
        "tensorflow", "keras", "pytorch", "matplotlib", "seaborn", "aws", "azure", "gcp", "docker", 
        "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd", "terraform", "ansible",
        "agile", "scrum", "kanban", "jira", "linux", "bash", "shell scripting", "powershell",
        "rest", "graphql", "grpc", "api"
    ]
}

# Synonym normalization
SYNONYM_MAP = {
    "js": "javascript",
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "ts": "typescript",
    "react.js": "react",
    "reactjs": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "vue.js": "vue",
    "vuejs": "vue",
    "k8s": "kubernetes",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "golang": "go",
}

def clean_text(text: str) -> str:
    """
    Cleans raw text by removing extra whitespaces, lowercasing,
    and removing specific punctuation while preserving skills like C++ or C#.
    """
    if not text:
        return ""
    text = text.encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[^a-z0-9\s#\+\.\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_skill(skill: str) -> str:
    skill = skill.lower().strip()
    return SYNONYM_MAP.get(skill, skill)
