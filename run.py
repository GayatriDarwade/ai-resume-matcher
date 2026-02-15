#!/usr/bin/env python3
"""
Startup script for AI Resume Matcher.
Handles initialization and runs the Flask application.
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly configured."""
    logger.info("Checking environment configuration...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8+ required")
        return False
    
    # Note: No API keys required - 100% local processing
    
    # Check required directories
    dirs = ["data", "data/resumes", "vectorstore", "templates"]
    for dir_name in dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Directory exists: {dir_name}")
    
    return True

def check_dependencies():
    """Check if all required packages are installed."""
    logger.info("Checking dependencies...")
    
    required_packages = [
        "flask",
        "sentence_transformers",
        "faiss",
        "PyPDF2",
        "docx",
        "numpy",
        "google",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} is installed")
        except ImportError:
            missing.append(package)
            logger.error(f"✗ {package} is NOT installed")
    
    if missing:
        logger.error(f"Missing packages: {', '.join(missing)}")
        logger.error("Run: pip install -r requirements.txt")
        return False
    
    return True

def initialize_app():
    """Initialize the application."""
    logger.info("Initializing AI Resume Matcher...")
    
    try:
        from resume_ingest import load_index
        index, metadata = load_index()
        logger.info(f"✓ Loaded FAISS index with {len(metadata)} resumes")
        return True
    except Exception as e:
        logger.warning(f"Could not load existing index: {e}")
        logger.info("A new index will be created on first use")
        return True

def main():
    """Main entry point."""
    print("""
    ================================================
    AI Resume Matcher - Startup
    ================================================
    """)
    
    # Check environment
    if not check_environment():
        return 1
    
    print()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    print()
    
    # Initialize app
    if not initialize_app():
        return 1
    
    print()
    logger.info("=" * 50)
    logger.info("Starting Flask application...")
    logger.info("=" * 50)
    logger.info("")
    logger.info("Application is running at: http://127.0.0.1:5000")
    logger.info("Press CTRL+C to stop")
    logger.info("")
    
    # Import and run Flask app
    try:
        from app import app
        app.run(debug=True, host="127.0.0.1", port=5000)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
