# 🎯 AI Resume Matcher

**100% Local AI Resume Matching** - No API keys, No quotas, No limits!

A powerful resume matching system that runs entirely on your machine using local AI and vector search. Perfect for deployment anywhere without worrying about API costs or quotas.

## ✨ Features
- **🚀 100% Local Processing** - No external API calls, runs completely offline
- **🔍 Semantic Search** - FAISS vector search finds contextually similar resumes
- **🎯 Skills Matching** - Comprehensive keyword extraction (200+ tech skills)
- **⚡ Hybrid Scoring** - Combines semantic similarity (60%) + skills match (40%)
- **💰 Zero Cost** - No API fees, unlimited usage
- **📦 Easy Deployment** - Deploy on any $5/month server (no GPU needed)
- **🎨 Modern UI** - Clean, responsive interface with real-time feedback
- **🔄 Duplicate Detection** - Automatically eliminates duplicate resumes

## 🚀 Quick Start

```bash
# Clone repository
cd ai-resume-matcher

# Install dependencies (no API clients needed!)
pip install -r requirements.txt

# Run immediately - no API keys required!
python app.py
```

Visit `http://localhost:5000` and start matching!

## 📋 How It Works

1. **Upload** resumes (PDF/DOCX) → Skills extracted using local keyword matching
2. **Paste** job description → Requirements extracted locally
3. **Search** runs:
   - Vector similarity using local sentence-transformers
   - Skills matching using 200+ keyword patterns
   - Hybrid scoring combines both
4. **Results** show top 5 candidates with detailed breakdowns

## 🛠️ Tech Stack
- **Backend:** Flask (lightweight web framework)
- **AI/ML:** 
  - Sentence Transformers (local embeddings, no API)
  - FAISS (vector similarity search)
  - Custom keyword extraction (200+ tech skills)
- **Frontend:** HTML/CSS (no framework - fast & simple)
- **Storage:** Pickle + JSON metadata
- **Documents:** PyPDF2, python-docx

## 💡 Why Local Processing?

### ✅ Advantages
- **No API Costs** - Save $50-500/month
- **No Quotas** - Unlimited searches and analyses
- **Privacy** - All data stays on your machine
- **Fast** - No network latency
- **Easy Deployment** - Works on cheap hosting ($5-10/month)
- **Offline** - No internet required after model download
- **Predictable** - No rate limits or API downtime

### 📊 Accuracy
Still very accurate with local processing:
- **Semantic matching** via FAISS vectors (same quality as before)
- **Skills extraction** using 200+ keyword patterns
- **Hybrid scoring** combines both approaches
- **Results** are data-driven rather than prose-based

## 🚢 Deployment

### One-Click Deploy to Render (Free)

1. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ai-resume-matcher.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `ai-resume-matcher`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 app:app`
     - **Instance Type**: Free (512 MB RAM)
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment

3. **Access Your App**: 
   - URL: `https://your-app-name.onrender.com`
   - Upload resumes and start matching!

### Free Tier Limits
- ✅ **750 hours/month** (enough for 24/7)
- ✅ **512 MB RAM** (handles ~50-100 resumes)
- ⚠️ **Spins down after 15 min inactivity** (30s wake up)
- ✅ **Unlimited searches** - no API quotas!

### Alternative Hosting
Works on any platform with Python 3.10+:
- **Railway** ($5/month) - No spin-down
- **DigitalOcean** ($6/month) - 1GB RAM
- **AWS EC2** (Free tier) - t2.micro
- **PythonAnywhere** ($5/month) - Beginner-friendly
- **Your VPS** - Complete control

### Requirements
- **RAM:** 2GB minimum, 4GB recommended
- **CPU:** Any modern CPU (no GPU needed!)
- **Disk:** 500MB for models + storage
- **OS:** Linux, Windows, or macOS

## 📁 File Structure
```
ai-resume-matcher/
├── app.py                   # Flask web server
├── ai_utils.py             # Local AI processing (no API!)
├── resume_ingest.py        # Resume processing & FAISS indexing
├── config.py               # Configuration
├── requirements.txt        # Dependencies (no API clients)
├── templates/
│   ├── index.html         # Upload & search UI
│   └── results.html       # Results with skills breakdown
├── data/resumes/          # Uploaded resume files
└── vectorstore/           # FAISS index & metadata
```

## 🎯 Skills Database

Detects 200+ skills including:
- **Languages:** Python, Java, JavaScript, TypeScript, C++, Go, Rust...
- **Web:** React, Angular, Vue, Django, Flask, Node.js, Spring...
- **Databases:** PostgreSQL, MongoDB, Redis, MySQL, Cassandra...
- **Cloud:** AWS, Azure, GCP, Docker, Kubernetes, Terraform...
- **AI/ML:** TensorFlow, PyTorch, Scikit-learn, Pandas, NLP...

See `ai_utils.py` for the complete list.

## 🔧 Configuration

Edit `config.py` to customize:
```python
SEMANTIC_WEIGHT = 0.6  # 60% semantic similarity
SKILLS_WEIGHT = 0.4    # 40% skills matching
TOP_K_RESUMES = 5      # Number of results
```

## 🙋 FAQ

**Q: Is it really 100% local?**  
A: Yes! Everything runs locally after the initial model download.

**Q: How accurate is keyword extraction vs AI?**  
A: Very accurate for technical skills (200+ patterns). Perfect for skill matching.

**Q: Can I add more skills?**  
A: Yes! Edit `TECH_SKILLS_DB` in `ai_utils.py`.

**Q: Does it work offline?**  
A: Yes, 100% offline after first run.

**Q: Deployment costs?**  
A: $0-10/month. No AI API costs!

---
**Built with ❤️ for easy deployment and unlimited usage**
