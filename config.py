"""
Configuration file for AI Resume Matcher application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== Application Settings ==========
APP_NAME = "AI Resume Matcher"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
HOST = "127.0.0.1"
PORT = 5000

# ========== Data Settings ==========
DATA_DIR = "data"
RESUME_DIR = os.path.join(DATA_DIR, "resumes")
VECTORSTORE_DIR = "vectorstore"
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

# ========== AI Processing Settings ==========
# This app uses LOCAL processing only - no external API required!
# All skills extraction and analysis happens locally using keyword matching
# and sentence-transformers embeddings. No quotas, no API costs, easy deployment.

# ========== Embedding Settings ==========
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
USE_LOCAL_EMBEDDINGS = True  # Always use local embeddings (no API calls)

# ========== Search Settings ==========
TOP_K_RESUMES = 5
TOP_K_CANDIDATES = 10  # Retrieve more candidates for re-ranking
MIN_JOB_DESCRIPTION_LENGTH = 10
SIMILARITY_THRESHOLD = 0.0  # Return all results above threshold (0 = no threshold)

# Hybrid Search Settings
HYBRID_SEARCH_ENABLED = True
SEMANTIC_WEIGHT = 0.6  # 60% weight for semantic similarity
SKILLS_WEIGHT = 0.4    # 40% weight for skills matching

# ========== Caching Settings ==========
ENABLE_CACHING = True
CACHE_MAX_SIZE = 1000
CACHE_TTL_SECONDS = 86400  # 24 hours

# ========== Logging Settings ==========
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ========== Flask Settings ==========
FLASK_ENV = os.getenv("FLASK_ENV", "development")
MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESUME_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)
