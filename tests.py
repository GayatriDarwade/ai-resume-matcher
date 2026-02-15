"""
Unit tests for AI Resume Matcher application.
Run with: python -m pytest tests.py -v
"""

import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_utils import get_embedding, extract_skills, analyze_resume_match
from resume_ingest import (
    extract_text_from_pdf, extract_text_from_docx, 
    compute_file_hash, process_resume, ingest_resumes, 
    save_index, load_index
)


class TestGeminiUtils(unittest.TestCase):
    """Test Gemini utility functions."""
    
    def test_get_embedding_invalid_input(self):
        """Test get_embedding with invalid input."""
        with self.assertRaises(ValueError):
            get_embedding("")
        
        with self.assertRaises(ValueError):
            get_embedding(None)
    
    def test_get_embedding_valid_input(self):
        """Test get_embedding with valid input."""
        text = "This is a sample resume text"
        embedding = get_embedding(text)
        self.assertIsInstance(embedding, list)
        self.assertEqual(len(embedding), 384)  # MiniLM model output size
    
    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_chat_with_gemini_no_api_key(self):
        """Test chat_with_gemini without API key."""
        with self.assertRaises(RuntimeError):
            chat_with_gemini("Test prompt")
    
    def test_chat_with_gemini_invalid_prompt(self):
        """Test chat_with_gemini with invalid prompt."""
        with self.assertRaises(ValueError):
            chat_with_gemini("")
        
        with self.assertRaises(ValueError):
            chat_with_gemini(None)


class TestResumeIngest(unittest.TestCase):
    """Test resume ingestion functions."""
    
    def setUp(self):
        """Set up temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.resume_dir = os.path.join(self.test_dir, "resumes")
        os.makedirs(self.resume_dir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)
    
    def test_compute_file_hash(self):
        """Test file hash computation."""
        # Create a test file
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        hash1 = compute_file_hash(test_file)
        hash2 = compute_file_hash(test_file)
        
        # Same file should produce same hash
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA256 hex length
    
    def test_extract_text_from_docx_invalid_file(self):
        """Test extracting text from non-existent DOCX."""
        with self.assertRaises(Exception):
            extract_text_from_docx("/nonexistent/path/file.docx")
    
    def test_ingest_resumes_empty_folder(self):
        """Test ingesting from empty folder."""
        count = ingest_resumes(self.resume_dir)
        self.assertEqual(count, 0)
    
    def test_ingest_resumes_nonexistent_folder(self):
        """Test ingesting from non-existent folder."""
        count = ingest_resumes("/nonexistent/path")
        self.assertEqual(count, 0)
    
    def test_process_resume_nonexistent_file(self):
        """Test processing non-existent resume."""
        with self.assertRaises(FileNotFoundError):
            process_resume("/nonexistent/resume.pdf")
    
    def test_save_and_load_index(self):
        """Test saving and loading index."""
        # Create temp vectorstore
        vectorstore_dir = os.path.join(self.test_dir, "vectorstore")
        os.makedirs(vectorstore_dir, exist_ok=True)
        
        # Save
        save_index()
        
        # Check files were created
        self.assertTrue(os.path.exists(os.path.join(vectorstore_dir, "resume_index.faiss")))
        self.assertTrue(os.path.exists(os.path.join(vectorstore_dir, "resume_metadata.pkl")))


class TestFlaskApp(unittest.TestCase):
    """Test Flask application routes."""
    
    def setUp(self):
        """Set up Flask test client."""
        from app import app
        self.app = app
        self.client = app.test_client()
    
    def test_home_get(self):
        """Test GET request to home page."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI Resume Matcher", response.data)
    
    def test_home_post_no_input(self):
        """Test POST with no job description."""
        response = self.client.post("/", data={"job_text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"error", response.data.lower())
    
    def test_home_post_short_input(self):
        """Test POST with insufficient input."""
        response = self.client.post("/", data={"job_text": "short"})
        self.assertEqual(response.status_code, 200)
    
    def test_stats_endpoint(self):
        """Test stats endpoint."""
        response = self.client.get("/stats")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("total_resumes", data)
        self.assertIn("index_ready", data)
    
    def test_upload_no_files(self):
        """Test upload without files."""
        response = self.client.post("/upload", data={})
        self.assertEqual(response.status_code, 400)
    
    def test_upload_invalid_format(self):
        """Test upload with invalid file format."""
        response = self.client.post("/upload", data={
            "files": (open(__file__, "rb"), "test.txt")
        })
        self.assertEqual(response.status_code, 400)
    
    def test_404_error(self):
        """Test 404 error handling."""
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)


class TestInputValidation(unittest.TestCase):
    """Test input validation across modules."""
    
    def test_embedding_with_special_characters(self):
        """Test embedding with special characters."""
        text = "Skills: Python, C++, Java. Email: test@example.com. Phone: +1-234-567-8901"
        embedding = get_embedding(text)
        self.assertIsInstance(embedding, list)
        self.assertEqual(len(embedding), 384)
    
    def test_embedding_with_unicode(self):
        """Test embedding with unicode characters."""
        text = "Multilingual: English, 中文, 日本語, 한국어"
        embedding = get_embedding(text)
        self.assertIsInstance(embedding, list)
    
    def test_embedding_with_long_text(self):
        """Test embedding with very long text."""
        text = "Resume content. " * 1000  # Very long resume
        embedding = get_embedding(text)
        self.assertIsInstance(embedding, list)
        self.assertEqual(len(embedding), 384)


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""
    
    def test_invalid_pdf_file(self):
        """Test handling of corrupted PDF."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"Not a valid PDF")
            f.flush()
            
            try:
                with self.assertRaises(Exception):
                    extract_text_from_pdf(f.name)
            finally:
                os.unlink(f.name)
    
    def test_process_resume_with_empty_text(self):
        """Test processing resume with no extractable text."""
        # This test would need actual PDF/DOCX files with no text
        # Skipped for now as it requires file setup
        pass


if __name__ == "__main__":
    unittest.main()
