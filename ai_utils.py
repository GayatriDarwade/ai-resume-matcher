"""
Local AI utilities for resume matching - No external API required!
All processing happens locally using keyword extraction and embeddings.
"""

import os
import logging
import re
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Set

# Setup logging
logger = logging.getLogger(__name__)

# Load local embedding model (CPU-friendly, no quotas, no API)
local_embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ----------------------------------------
# Comprehensive Skills Database
# ----------------------------------------

TECH_SKILLS_DB = {
    # Programming Languages
    'languages': [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'ruby', 'go', 'golang',
        'rust', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash',
        'powershell', 'objective-c', 'dart', 'elixir', 'haskell', 'lua', 'groovy', 'vb.net',
        'julia', 'fortran', 'cobol', 'assembly', 'sql', 'plsql', 't-sql', 'nosql'
    ],
    
    # Web Frameworks & Libraries
    'web_frameworks': [
        'react', 'angular', 'vue', 'vue.js', 'svelte', 'next.js', 'nuxt.js', 'gatsby',
        'django', 'flask', 'fastapi', 'express', 'express.js', 'nest.js', 'koa',
        'spring', 'spring boot', 'asp.net', '.net core', 'laravel', 'symfony', 'rails',
        'ruby on rails', 'node.js', 'nodejs', 'jquery', 'backbone.js', 'ember.js',
        'meteor', 'webpack', 'vite', 'parcel', 'rollup', 'babel'
    ],
    
    # Databases
    'databases': [
        'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'cassandra', 'dynamodb',
        'oracle', 'mssql', 'sql server', 'sqlite', 'mariadb', 'couchdb', 'neo4j',
        'elasticsearch', 'firestore', 'firebase', 'realm', 'influxdb', 'timescaledb',
        'cockroachdb', 'aurora', 'documentdb', 'cosmosdb'
    ],
    
    # Cloud & DevOps
    'cloud': [
        'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud',
        'docker', 'kubernetes', 'k8s', 'helm', 'terraform', 'ansible', 'puppet', 'chef',
        'jenkins', 'gitlab ci', 'github actions', 'circleci', 'travis ci', 'bitbucket pipelines',
        'ci/cd', 'ec2', 's3', 'lambda', 'ecs', 'eks', 'cloudformation', 'cloudwatch',
        'iam', 'vpc', 'rds', 'api gateway', 'cloudfront', 'route53', 'azure devops',
        'heroku', 'netlify', 'vercel', 'digital ocean', 'linode', 'openshift'
    ],
    
    # AI/ML & Data Science
    'ai_ml': [
        'machine learning', 'deep learning', 'neural networks', 'nlp', 'natural language processing',
        'computer vision', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas',
        'numpy', 'scipy', 'jupyter', 'matplotlib', 'seaborn', 'opencv', 'hugging face',
        'transformers', 'bert', 'gpt', 'llama', 'stable diffusion', 'data science',
        'data analysis', 'statistics', 'spark', 'pyspark', 'hadoop', 'airflow',
        'mlflow', 'kubeflow', 'sagemaker', 'vertex ai', 'azure ml'
    ],
    
    # Mobile Development
    'mobile': [
        'ios', 'android', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova',
        'swift', 'swiftui', 'objective-c', 'kotlin', 'jetpack compose', 'xcode'
    ],
    
    # Testing & Quality
    'testing': [
        'jest', 'mocha', 'chai', 'jasmine', 'pytest', 'unittest', 'selenium', 'cypress',
        'playwright', 'puppeteer', 'junit', 'testng', 'cucumber', 'postman', 'jmeter',
        'k6', 'locust', 'unit testing', 'integration testing', 'e2e testing', 'tdd',
        'bdd', 'test automation'
    ],
    
    # Tools & IDEs
    'tools': [
        'git', 'github', 'gitlab', 'bitbucket', 'svn', 'vscode', 'visual studio',
        'intellij', 'pycharm', 'eclipse', 'vim', 'emacs', 'sublime text', 'atom',
        'jira', 'confluence', 'slack', 'teams', 'notion', 'trello', 'asana'
    ],
    
    # APIs & Protocols
    'apis': [
        'rest api', 'restful', 'graphql', 'grpc', 'soap', 'websocket', 'http', 'https',
        'oauth', 'jwt', 'api design', 'openapi', 'swagger', 'postman'
    ],
    
    # Methodologies
    'methodologies': [
        'agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd', 'microservices',
        'monolith', 'serverless', 'event-driven', 'domain-driven design', 'ddd',
        'solid', 'design patterns', 'clean code', 'clean architecture'
    ],
    
    # Other Technical
    'other': [
        'linux', 'unix', 'windows', 'macos', 'nginx', 'apache', 'rabbitmq', 'kafka',
        'celery', 'redis queue', 'message queue', 'webscraping', 'beautiful soup',
        'scrapy', 'regex', 'json', 'xml', 'yaml', 'html', 'css', 'sass', 'scss',
        'tailwind', 'bootstrap', 'material ui', 'chakra ui', 'security', 'encryption',
        'blockchain', 'web3', 'ethereum', 'solidity', 'smart contracts'
    ]
}

# Flatten all skills into one searchable list
ALL_TECH_SKILLS = []
for category in TECH_SKILLS_DB.values():
    ALL_TECH_SKILLS.extend(category)

# Soft skills database
SOFT_SKILLS = [
    'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
    'critical thinking', 'creativity', 'collaboration', 'time management',
    'project management', 'mentoring', 'coaching', 'public speaking', 'presentation',
    'negotiation', 'conflict resolution', 'adaptability', 'flexibility', 'initiative',
    'self-motivated', 'detail-oriented', 'organized', 'multitasking', 'prioritization'
]

# Certifications patterns
CERTIFICATION_PATTERNS = [
    r'aws certified', r'azure certified', r'google cloud certified', r'gcp certified',
    r'certified kubernetes', r'ckad?', r'pmp', r'cissp', r'comptia', r'ccna', r'ccnp',
    r'ceh', r'oscp', r'cisa', r'cism', r'itil', r'prince2', r'csm', r'safe',
    r'bachelor', r'master', r'mba', r'phd', r'b\.?s\.?', r'm\.?s\.?', r'b\.?tech',
    r'm\.?tech', r'b\.?e\.?', r'm\.?e\.?'
]

# ----------------------------------------
# Function: Get local embeddings (always local, no API)
# ----------------------------------------
def get_embedding(text: str) -> List[float]:
    """
    Get embeddings for text using local sentence-transformers model.
    No API calls, works offline, unlimited usage.
    """
    if not text or not isinstance(text, str):
        logger.error("Invalid text provided for embedding")
        raise ValueError("Text must be a non-empty string")
    
    try:
        return local_embedding_model.encode(text).tolist()
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise

# ----------------------------------------
# Function: Enhanced keyword-based skills extraction
# ----------------------------------------
def extract_skills(text: str, text_type: str = "resume") -> Dict[str, any]:
    """
    Extract skills from text using comprehensive keyword matching.
    Works completely offline with no API calls.
    
    Args:
        text: Resume or job description text
        text_type: "resume" or "job" for logging context
    
    Returns:
        dict with technical_skills, soft_skills, tools, and certifications
    """
    if not text or not isinstance(text, str):
        return {
            "technical_skills": [],
            "soft_skills": [],
            "tools": [],
            "certifications": [],
            "years_experience": "N/A"
        }
    
    text_lower = text.lower()
    
    # Extract technical skills
    tech_skills_found = set()
    for skill in ALL_TECH_SKILLS:
        # Use word boundaries for better matching
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            tech_skills_found.add(skill)
    
    # Extract soft skills
    soft_skills_found = set()
    for skill in SOFT_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            soft_skills_found.add(skill)
    
    # Extract certifications
    certifications_found = set()
    for cert_pattern in CERTIFICATION_PATTERNS:
        matches = re.finditer(cert_pattern, text_lower, re.IGNORECASE)
        for match in matches:
            cert_text = match.group(0)
            # Get surrounding context for better cert names
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end].strip()
            certifications_found.add(cert_text)
    
    # Extract years of experience
    years_exp = "N/A"
    years_patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience[:\s]+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience'
    ]
    for pattern in years_patterns:
        match = re.search(pattern, text_lower)
        if match:
            years_exp = f"{match.group(1)}+ years"
            break
    
    logger.info(f"Extracted {len(tech_skills_found)} technical skills from {text_type}")
    
    return {
        "technical_skills": sorted(list(tech_skills_found)),
        "soft_skills": sorted(list(soft_skills_found)),
        "tools": [],  # Already included in technical_skills
        "certifications": sorted(list(certifications_found)),
        "years_experience": years_exp
    }

# ----------------------------------------
# Function: Calculate skills match score
# ----------------------------------------
def calculate_skills_match(job_skills: Dict, resume_skills: Dict) -> Dict:
    """
    Calculate how well resume skills match job requirements.
    Pure local computation, no API calls.
    
    Returns:
        dict with match_score (0-100), matched_skills, and missing_skills
    """
    def normalize_list(items):
        """Normalize list items to lowercase set."""
        if not isinstance(items, list):
            return set()
        return set(str(item).lower().strip() for item in items if item)
    
    # Combine all job requirements
    job_all = (
        normalize_list(job_skills.get('technical_skills', [])) |
        normalize_list(job_skills.get('tools', [])) |
        normalize_list(job_skills.get('certifications', []))
    )
    
    # Combine all resume skills
    resume_all = (
        normalize_list(resume_skills.get('technical_skills', [])) |
        normalize_list(resume_skills.get('tools', [])) |
        normalize_list(resume_skills.get('certifications', []))
    )
    
    if not job_all:
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "total_required": 0,
            "total_matched": 0
        }
    
    # Calculate matches
    matched = job_all & resume_all
    missing = job_all - resume_all
    
    # Score: percentage of required skills found
    match_score = (len(matched) / len(job_all)) * 100 if job_all else 0
    
    return {
        "match_score": round(match_score, 2),
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing)),
        "total_required": len(job_all),
        "total_matched": len(matched)
    }

# ----------------------------------------
# Function: Hybrid scoring (semantic + skills)
# ----------------------------------------
def calculate_hybrid_score(semantic_score: float, skills_match_score: float, alpha: float = 0.6) -> float:
    """
    Combine semantic similarity and skills match into hybrid score.
    
    Args:
        semantic_score: Score from vector similarity (0-100)
        skills_match_score: Score from skills matching (0-100)
        alpha: Weight for semantic score (default 0.6 = 60% semantic, 40% skills)
    
    Returns:
        Hybrid score (0-100)
    """
    return alpha * semantic_score + (1 - alpha) * skills_match_score

# ----------------------------------------
# Function: Local resume analysis (no API)
# ----------------------------------------
def analyze_resume_match(job_description: str, resume_text: str, resume_filename: str) -> Dict:
    """
    Analyze resume match using local skills extraction only.
    No API calls, completely offline processing.
    
    Returns:
        dict with strengths, weaknesses, and overall fit assessment
    """
    # Extract skills from both
    job_skills = extract_skills(job_description, "job")
    resume_skills = extract_skills(resume_text, "resume")
    
    # Calculate match
    skills_match = calculate_skills_match(job_skills, resume_skills)
    
    # Generate strengths (matched skills)
    strengths = []
    if skills_match["matched_skills"]:
        top_matches = skills_match["matched_skills"][:5]  # Top 5
        strengths = [f"Has {skill}" for skill in top_matches]
    
    # Generate weaknesses (missing skills)
    weaknesses = []
    if skills_match["missing_skills"]:
        top_missing = skills_match["missing_skills"][:5]  # Top 5
        weaknesses = [f"Missing {skill}" for skill in top_missing]
    
    # Determine overall fit based on match score
    match_score = skills_match["match_score"]
    if match_score >= 70:
        overall_fit = "High"
    elif match_score >= 40:
        overall_fit = "Medium"
    else:
        overall_fit = "Low"
    
    # Generate reasoning
    reasoning = f"Matched {skills_match['total_matched']}/{skills_match['total_required']} required skills ({match_score:.1f}%)"
    
    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "overall_fit": overall_fit,
        "reasoning": reasoning
    }
