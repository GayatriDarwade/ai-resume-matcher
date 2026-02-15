import os
import faiss
import numpy as np
import logging
import json
import hashlib
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
import docx
import pickle
from pathlib import Path
from ai_utils import extract_skills

# Setup logging
logger = logging.getLogger(__name__)

# ------------------------------
# Initialize embedding model
# ------------------------------
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# FAISS index (L2 similarity)
embedding_dim = 384  # all-MiniLM-L6-v2 output size
index = faiss.IndexFlatL2(embedding_dim)

# Store metadata (mapping vector → resume path)
metadata = []

VECTORSTORE_DIR = "vectorstore"
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# Track file hashes to detect duplicates
file_hashes = {}

# -------- PDF Extraction --------
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file with error handling."""
    try:
        reader = PdfReader(file_path)
        if not reader.pages:
            logger.warning(f"PDF {file_path} has no pages")
            return ""
        text = " ".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF {file_path}: {e}")
        raise ValueError(f"Failed to read PDF: {e}")

# -------- DOCX Extraction --------
def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file with error handling."""
    try:
        doc = docx.Document(file_path)
        text = " ".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting DOCX {file_path}: {e}")
        raise ValueError(f"Failed to read DOCX: {e}")

# -------- Compute file hash for deduplication --------
def compute_file_hash(file_path: str) -> str:
    """Compute SHA256 hash of file content for deduplication."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# -------- Resume Processing --------
def process_resume(file_path: str) -> tuple:
    """Extract text and embedding from resume file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")
    
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    
    if not text or len(text.strip()) < 10:
        raise ValueError(f"Resume {file_path} contains insufficient text")
    
    # Get embedding
    try:
        embedding = embedder.encode([text])[0]
        return text, embedding
    except Exception as e:
        logger.error(f"Error embedding resume {file_path}: {e}")
        raise

# -------- Batch Ingestion (updated) --------
def ingest_resumes(resume_folder: str = "data/resumes") -> int:
    """Ingest resumes from folder, skipping duplicates based on content hash."""
    global metadata, file_hashes
    
    if not os.path.exists(resume_folder):
        logger.warning(f"Resume folder not found: {resume_folder}")
        return 0
    
    existing_files = {m["file"] for m in metadata}
    existing_hashes = set(file_hashes.values())
    
    ingested_count = 0
    skipped_duplicates = 0
    skipped_errors = 0
    
    for fname in os.listdir(resume_folder):
        fpath = os.path.join(resume_folder, fname)
        
        # Skip if not a file or wrong format
        if not os.path.isfile(fpath) or not fname.endswith((".pdf", ".docx")):
            continue
        
        # Skip if already ingested by filename
        if fname in existing_files:
            logger.info(f"Skipping already ingested: {fname}")
            continue
        
        try:
            # Check for duplicate content
            file_hash = compute_file_hash(fpath)
            if file_hash in existing_hashes:
                logger.info(f"Duplicate content detected for {fname}, skipping")
                skipped_duplicates += 1
                continue
            
            text, embedding = process_resume(fpath)
            
            # Extract and cache skills to avoid API calls later
            try:
                skills = extract_skills(text, text_type="resume")
            except Exception as e:
                logger.warning(f"Failed to extract skills for {fname}: {e}")
                skills = {
                    "technical_skills": [],
                    "soft_skills": [],
                    "tools": [],
                    "certifications": []
                }
            
            index.add(np.array([embedding], dtype=np.float32))
            metadata.append({
                "file": fname,
                "text": text,
                "hash": file_hash,
                "skills": skills
            })
            file_hashes[fname] = file_hash
            logger.info(f"Ingested: {fname}")
            ingested_count += 1
        except Exception as e:
            logger.error(f"Failed to ingest {fname}: {e}")
            skipped_errors += 1
    
    logger.info(f"Ingestion complete: {ingested_count} added, {skipped_duplicates} duplicates, {skipped_errors} errors. Total: {len(metadata)}")
    return ingested_count

# -------- Save FAISS + Metadata --------
def save_index() -> bool:
    """Save FAISS index and metadata to disk."""
    try:
        faiss.write_index(index, os.path.join(VECTORSTORE_DIR, "resume_index.faiss"))
        with open(os.path.join(VECTORSTORE_DIR, "resume_metadata.pkl"), "wb") as f:
            pickle.dump(metadata, f)
        
        # Also save as JSON for transparency
        metadata_json = []
        for m in metadata:
            m_copy = m.copy()
            m_copy.pop('hash', None)  # Remove hash from JSON
            metadata_json.append(m_copy)
        with open(os.path.join(VECTORSTORE_DIR, "resume_metadata.json"), "w") as f:
            json.dump(metadata_json, f, indent=2)
        
        logger.info("Saved index and metadata")
        return True
    except Exception as e:
        logger.error(f"Error saving index: {e}")
        return False

# -------- Load FAISS + Metadata --------
def load_index() -> tuple:
    """Load FAISS index and metadata from disk."""
    global index, metadata, file_hashes
    try:
        index = faiss.read_index(os.path.join(VECTORSTORE_DIR, "resume_index.faiss"))
        with open(os.path.join(VECTORSTORE_DIR, "resume_metadata.pkl"), "rb") as f:
            metadata = pickle.load(f)
        
        # Rebuild file_hashes from metadata
        file_hashes = {m["file"]: m.get("hash", "") for m in metadata if "hash" in m}
        
        logger.info(f"Loaded index with {len(metadata)} resumes")
    except FileNotFoundError:
        logger.warning("No existing index found. Starting fresh...")
        metadata = []
        file_hashes = {}
        index = faiss.IndexFlatL2(384)
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        metadata = []
        file_hashes = {}
        index = faiss.IndexFlatL2(384)
    
    return index, metadata

# -------- CLI (optional) --------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ingest_resumes()
    save_index()
