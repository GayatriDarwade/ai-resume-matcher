# 🚀 Deployment Guide - Render

## Quick Deploy (5 minutes)

### Prerequisites
- GitHub account
- Render account (free - sign up at https://render.com)

### Step 1: Push to GitHub

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - AI Resume Matcher"
   ```

2. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Name: `ai-resume-matcher` (or your preferred name)
   - Make it public or private
   - Don't initialize with README (we already have one)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ai-resume-matcher.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Create New Web Service**:
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   - **Name**: `ai-resume-matcher` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 app:app`
   - **Instance Type**: `Free` (512 MB RAM, 0.1 CPU)

3. **Environment Variables** (optional):
   - None required! (100% local processing)

4. **Advanced Settings** (optional):
   - **Health Check Path**: `/`
   - **Auto-Deploy**: `Yes` (deploys automatically on git push)

5. **Click "Create Web Service"**

### Step 3: Wait for Deployment

- Initial deployment takes 5-10 minutes
- Render will:
  - Install Python dependencies (~400MB)
  - Download sentence-transformers model (~90MB)
  - Build FAISS index
  - Start the app

### Step 4: Upload Resumes

After deployment completes:

1. **Visit your app**: `https://your-app-name.onrender.com`
2. **Upload resumes**: Use the web interface to upload PDF/DOCX files
3. **Search**: Paste job descriptions and find matches!

## 📊 Render Free Tier Limits

- ✅ **750 hours/month** (enough for 24/7 uptime)
- ✅ **512 MB RAM** (sufficient for ~50-100 resumes)
- ⚠️ **Spins down after 15 min inactivity** (takes ~30s to wake up)
- ✅ **Unlimited bandwidth**
- ✅ **Custom domains** (free SSL)

## 🔧 Upgrade Options

If you need more power:

### Render Starter ($7/month)
- No spin-down (always on)
- Faster startup
- Better performance

### Increase RAM
- **$7/month**: 512MB → 1GB
- **$15/month**: 1GB → 2GB (handles 500+ resumes)

## 🛠️ Troubleshooting

### App Won't Start
- Check build logs for dependency errors
- Verify Python version (3.10 or 3.11 recommended)

### Slow First Request
- Free tier spins down after inactivity
- First request after spin-down takes 20-30 seconds
- Upgrade to Starter plan for always-on service

### Out of Memory
- Free tier has 512MB RAM limit
- Reduce number of resumes in database
- Or upgrade to higher RAM plan

### Model Download Timeout
- On first deploy, model download may timeout
- Just redeploy - model is cached after first download

## 🌐 Custom Domain

1. **Add Custom Domain** (Render Dashboard):
   - Go to your service → Settings → Custom Domains
   - Add your domain: `resume-matcher.yourdomain.com`

2. **Update DNS**:
   - Add CNAME record pointing to Render URL
   - SSL certificate is auto-provisioned (free)

## 📝 Post-Deployment

### Upload Sample Resumes
Upload your existing resumes from `data/resumes/` folder through the web interface.

### Test the App
1. Go to your Render URL
2. Upload 2-3 test resumes
3. Paste a job description
4. Verify results and UI enhancements

### Monitor Performance
- Check Render dashboard for metrics
- View logs for errors
- Monitor response times

## 🔄 Updating Your App

Every time you push to GitHub, Render auto-deploys:

```bash
git add .
git commit -m "Update: new feature"
git push
```

Render automatically:
1. Detects the push
2. Rebuilds the app
3. Deploys the new version
4. Zero-downtime deployment!

## 💡 Alternative: Manual Deployment

If you prefer manual control:

1. Disable auto-deploy in Render settings
2. Trigger manual deploys from Render dashboard
3. Test locally before deploying

## 🎯 Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Deployment succeeded (check logs)
- [ ] App loads at Render URL
- [ ] Resume upload works
- [ ] Job search returns results
- [ ] Dark mode toggles properly
- [ ] Circular progress bars animate
- [ ] Skills tags display correctly

## 🚨 Important Notes

1. **Data Persistence**:
   - Render free tier may lose data on redeploys
   - Upgrade to add persistent disk ($1/GB/month)
   - Or re-upload resumes after each deployment

2. **Performance**:
   - Free tier is ideal for personal use/testing
   - For production, consider Starter plan ($7/month)

3. **Scaling**:
   - App can handle ~50 resumes on free tier
   - For more, upgrade RAM or use persistent disk

---

**Need Help?** 
- Render Docs: https://render.com/docs
- render-support@render.com
- Or open an issue on GitHub

**Ready to deploy? Follow Step 1 above! 🚀**
