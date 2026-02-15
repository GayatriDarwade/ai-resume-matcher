from flask import Flask, render_template, request, jsonify
import numpy as np
import logging
from functools import lru_cache
from resume_ingest import load_index, ingest_resumes, save_index
from ai_utils import (
    analyze_resume_match,
    extract_skills,
    calculate_skills_match,
    calculate_hybrid_score
)
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Load FAISS index + metadata
index, metadata = load_index()

# Embedding model for queries
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Cache for job descriptions
job_cache = {}

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            job_text = request.form.get("job_text", "").strip()
            
            if not job_text or len(job_text) < 10:
                return render_template("index.html", error="Please enter a valid job description (at least 10 characters)")
            
            if len(metadata) == 0:
                return render_template("index.html", error="No resumes in database. Please upload resumes first.")
            
            logger.info(f"Processing job description: {job_text[:50]}...")
            
            # Extract skills from job description (ONLY API call per search)
            logger.info("Extracting skills from job description...")
            job_skills = extract_skills(job_text, text_type="job")
            logger.info(f"Found {len(job_skills.get('technical_skills', []))} technical skills in job")
            
            # Embed job description with error handling
            try:
                job_embedding = embedder.encode([job_text]).reshape(1, -1).astype(np.float32)
            except Exception as e:
                logger.error(f"Embedding error: {e}")
                return render_template("index.html", error="Error processing job description")
            
            # FAISS search (get top 10 for re-ranking with skills)
            k = min(10, len(metadata))
            D, I = index.search(job_embedding, k=k)
            
            candidates = []
            seen_files = set()
            
            for dist, idx in zip(D[0], I[0]):
                if idx >= len(metadata):
                    continue
                    
                file_name = metadata[idx]["file"]
                if file_name in seen_files:
                    continue
                seen_files.add(file_name)
                
                # Calculate semantic similarity score
                semantic_score = 100 * np.exp(-dist)
                
                # Get cached skills (NO API CALL - already extracted during ingestion)
                resume_skills = metadata[idx].get("skills", {
                    "technical_skills": [],
                    "soft_skills": [],
                    "tools": [],
                    "certifications": []
                })
                
                # Calculate skills match
                skills_match = calculate_skills_match(job_skills, resume_skills)
                
                # Calculate hybrid score (60% semantic, 40% skills)
                hybrid_score = calculate_hybrid_score(semantic_score, skills_match["match_score"])
                
                candidates.append({
                    "file": file_name,
                    "text": metadata[idx]["text"][:1000],
                    "full_text": metadata[idx]["text"],
                    "semantic_score": round(semantic_score, 2),
                    "skills_score": skills_match["match_score"],
                    "hybrid_score": round(hybrid_score, 2),
                    "matched_skills": skills_match["matched_skills"],
                    "missing_skills": skills_match["missing_skills"],
                    "total_matched": skills_match["total_matched"],
                    "total_required": skills_match["total_required"]
                })
            
            # Sort by hybrid score and take top 5
            candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
            top_resumes = candidates[:5]
            
            # Add rank and score (NO detailed analysis here - lazy load on demand)
            for rank, resume_data in enumerate(top_resumes, 1):
                resume_data["rank"] = rank
                resume_data["score"] = resume_data["hybrid_score"]  # For compatibility
            
            # Cache the job
            job_cache[len(job_cache)] = {"job": job_text, "results": top_resumes}
            
            return render_template(
                "results.html",
                results=top_resumes,
                job_description=job_text[:200] + "..." if len(job_text) > 200 else job_text
            )
        
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return render_template("index.html", error="An error occurred. Please try again.")
    
    # GET request
    return render_template("index.html", resume_count=len(metadata))


@app.route("/upload", methods=["POST"])
def upload_resumes():
    """Handle resume file uploads."""
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({"error": "No files selected"}), 400
        
        import os
        from werkzeug.utils import secure_filename
        
        upload_folder = "data/resumes"
        os.makedirs(upload_folder, exist_ok=True)
        
        uploaded_files = []
        for file in files:
            if file and (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                uploaded_files.append(filename)
                logger.info(f"Uploaded: {filename}")
        
        if uploaded_files:
            # Re-ingest resumes
            count = ingest_resumes(upload_folder)
            save_index()
            return jsonify({
                "success": True,
                "message": f"Uploaded {len(uploaded_files)} file(s), ingested {count} resume(s)",
                "total_resumes": len(metadata)
            })
        else:
            return jsonify({"error": "No valid PDF or DOCX files provided"}), 400
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/analyze/<resume_filename>", methods=["POST"])
def analyze_resume(resume_filename):
    """Lazy-load detailed analysis for a specific resume (called on demand)."""
    try:
        data = request.json or {}
        job_text = data.get("job_text", "").strip()
        
        if not job_text:
            return jsonify({"error": "No job description provided"}), 400
        
        # Find resume in metadata
        resume_data = None
        for meta in metadata:
            if meta["file"] == resume_filename:
                resume_data = meta
                break
        
        if not resume_data:
            return jsonify({"error": "Resume not found"}), 404
        
        # Get detailed analysis (API call only when user clicks)
        try:
            analysis = analyze_resume_match(job_text, resume_data["text"], resume_filename)
            return jsonify({
                "success": True,
                "analysis": analysis
            })
        except Exception as e:
            logger.warning(f"Analysis failed for {resume_filename}: {e}")
            return jsonify({
                "success": False,
                "analysis": {
                    "strengths": ["Unable to analyze"],
                    "weaknesses": [],
                    "overall_fit": "N/A",
                    "reasoning": str(e)
                }
            })
    
    except Exception as e:
        logger.error(f"Analyze error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/stats")
def stats():
    """Return statistics about the system."""
    return jsonify({
        "total_resumes": len(metadata),
        "cached_searches": len(job_cache),
        "index_ready": index.ntotal > 0
    })


@app.errorhandler(404)
def not_found(error):
    return render_template("index.html", error="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return render_template("index.html", error="Server error occurred"), 500


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)
