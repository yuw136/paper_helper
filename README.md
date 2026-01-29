# Paper Helper

An AI-powered research assistant for discovering, reading, and discussing academic papers. Features include automated paper collection from arXiv, AI-powered summarization, weekly report generation, and an interactive chat interface for discussing paper content.

## Features

- **Automated Paper Collection**: Download papers from arXiv based on topics and categories
- **AI Summarization**: Generate concise summaries using LLMs
- **Weekly Reports**: Automatically compile and email research reports as PDFs
- **Interactive Chat**: Discuss papers with an AI agent that has access to the full paper content
- **PDF Management**: view, and organize papers with vector search capabilities
- **Dual Storage**: Support for both local development and cloud deployment (Supabase)

## Architecture

### Backend
- FastAPI server with async support
- PostgreSQL with pgvector extension for vector similarity search
- LlamaIndex for document parsing and indexing
- LangChain/LangGraph for AI agent workflow
- LaTeX for PDF report generation

### Frontend
- React + TypeScript
- Vite for build tooling
- PDF.js for document viewing

### Storage Options
- **Local Development**: Files stored locally, PostgreSQL via Docker Compose
- **Production**: Supabase PostgreSQL + Supabase Storage for file hosting

---

## Configuration

### Quick Start

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Fill in your credentials in `.env`

3. Start development (see Development section)

### Environment Variables

All configuration is managed through the `.env` file at the project root.

#### Required Variables

**Database Configuration**
```bash
# Local development
LOCAL_DATABASE_URL=postgresql://postgres:password@localhost:5432/paper_helper

# Production (Supabase)
SUPABASE_DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-region.pooler.supabase.com:6543/postgres

# Database mode switch
USE_SUPABASE=false  # false for local, true for Supabase
```

**API Keys**
```bash
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key
OPENAI_API_KEY=your_openai_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key  # Optional
```

**Supabase Configuration** (for production)
```bash
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_PAPERS_BUCKET=papers
SUPABASE_REPORTS_BUCKET=reports
```

**LangChain Configuration** (optional)
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_PROJECT=paper_helper
```

**Backend Configuration**
```bash
# CORS allowed origins (comma-separated, no spaces)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Frontend Configuration**
```bash
# Leave empty for development (uses Vite proxy)
# Set to backend URL for production
VITE_API_BASE_URL=
```

**Email Configuration** (for weekly reports)
```bash
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password  # App-specific password, not regular password
EMAIL_RECEIVER=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

#### Optional Variables (Have Defaults)

**Model Settings**
```bash
WRITING_MODEL_NAME=gpt-4o
WRITING_MODEL_TEMPERATURE=0.2
DEDUCE_MODEL_NAME=o3-mini
EMBEDDING_MODEL_NAME=text-embedding-3-small
```

**Document Processing**
```bash
CHUNK_SIZE=1024
CHUNK_OVERLAP=200
```

### Configuration Files

**`server/config.py`**
- Data directories for PDFs, reports, metadata
- ArXiv search parameters (categories, topics, time windows)
- Model initialization

**`server/chatbox/core/config.py`**
- CORS settings
- Model configurations
- Database session settings

---

## Development

### Prerequisites

**System Requirements**
- Python 3.10+
- Node.js 18+
- PostgreSQL with pgvector extension (via Docker Compose)
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX) for PDF report generation

**Installing LaTeX**
```bash
# Ubuntu/Debian
sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra

# macOS
brew install --cask mactex

# Windows
# Download and install MiKTeX: https://miktex.org/download
```

### Local Development Setup

1. **Start Database**
```bash
docker-compose up -d postgres
```

2. **Install Backend Dependencies**
```bash
cd server
pip install -r requirements.txt
```

3. **Initialize Database**
```bash
cd server
python -c "from database import create_db_and_tables; create_db_and_tables()"
```

4. **Start Backend Server**
```bash
cd server
python run_server.py
```

5. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

6. **Start Frontend Development Server**
```bash
cd frontend
npm run dev
```

7. **Access Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

### Running Weekly Report Pipeline

```bash
cd server
python run_weekly_report.py
```

This will:
1. Download papers from arXiv based on configured topics
2. Parse and index papers into the database
3. Generate AI summaries
4. Compile LaTeX report to PDF
5. Send report via email

---

## Supabase Deployment

### Database Setup

1. **Create Supabase Project**
   - Go to https://supabase.com and create a new project

2. **Enable pgvector Extension**
   - Dashboard → Database → Extensions
   - Search for "vector" and enable it

3. **Get Connection String**
   - Dashboard → Project Settings → Database
   - Copy **Connection String** (Transaction mode)
   - Format: `postgresql://postgres.[project-ref]:[password]@[host].pooler.supabase.com:6543/postgres`
   - Important: Use port 6543 (Transaction pooler), not 5432 (Session mode)

4. **Update Environment Variables**
```bash
USE_SUPABASE=true
SUPABASE_DATABASE_URL=postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres
```

### Storage Setup

1. **Create Storage Buckets**
   - Dashboard → Storage → New Bucket
   - Create two private buckets:
     - `papers` - for PDF papers
     - `reports` - for weekly report PDFs

2. **Configure Bucket Settings**
   - Set both buckets to Private
   - No public access needed (backend generates signed URLs)

3. **Update Environment Variables**
```bash
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_PAPERS_BUCKET=papers
SUPABASE_REPORTS_BUCKET=reports
```

### Storage Architecture

The application uses a dual-path storage model:

```
Paper/Report Models:
├── local_pdf_path  # For frontend display (e.g., "pdfs/math.DG/paper.pdf")
└── storage_url     # Actual storage location
    ├── Local mode: Full local file path
    └── Supabase mode: "bucket_name/path/to/file"
```

**Frontend Access Pattern:**
1. Call `/api/pdf-url/{file_id}` to get PDF URL
2. Local mode: Returns API endpoint for file streaming
3. Supabase mode: Returns signed URL for direct CDN access

### Testing Connection

```bash
cd server
python -c "from database import engine; from sqlalchemy import text; engine.connect().execute(text('SELECT 1'))"
```

---

## Render Deployment

### Prerequisites

- GitHub repository with your code
- Render account (https://render.com)
- Supabase database configured (see Supabase Deployment section)

### Files Overview

- **`Dockerfile`**: Defines Docker image with Python + LaTeX
- **`.dockerignore`**: Excludes unnecessary files from image
- **`render.yaml`**: Render service configuration

### Deployment Steps

#### 1. Update render.yaml

Edit `render.yaml` line 6 to point to your GitHub repository:
```yaml
repo: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
```

#### 2. Commit Docker Configuration

```bash
git add Dockerfile .dockerignore render.yaml
git commit -m "Add Docker configuration with LaTeX support"
git push origin main
```

#### 3. Render Auto-Detects and Deploys

Once you push to GitHub, Render will:
- Detect the Dockerfile
- Switch to Docker build mode
- Install LaTeX (texlive-xetex)
- Install Python dependencies
- Deploy the service

First build takes approximately 5-10 minutes due to LaTeX installation.

#### 4. Configure Environment Variables

Go to Render Dashboard → Your Service → Environment

Add all variables from your `.env` file:

**Required Variables:**
```bash
SUPABASE_DATABASE_URL=postgresql://...
LLAMA_CLOUD_API_KEY=xxx
OPENAI_API_KEY=xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
SUPABASE_PAPERS_BUCKET=papers
SUPABASE_REPORTS_BUCKET=reports
BACKEND_CORS_ORIGINS=https://your-frontend-url.com
```

**Optional Variables:**
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=xxx
EMAIL_SENDER=xxx
EMAIL_PASSWORD=xxx
EMAIL_RECEIVER=xxx
WRITING_MODEL_NAME=gpt-4o
DEDUCE_MODEL_NAME=o3-mini
```

Important: Environment variables in Render override any `.env` file. Do not commit `.env` to version control.

### Verifying Deployment

**Check Build Logs**
- Dashboard → Logs tab
- Look for: "Successfully installed texlive-xetex"

**Check Service Status**
- Dashboard should show green "Live" status
- Visit your service URL (e.g., https://paper-helper.onrender.com)

**Test LaTeX Support**
```bash
# In Render Shell (Dashboard → Shell tab)
cd /app/server
python run_weekly_report.py
```

### Updating Code

After initial deployment, updates are automatic:
```bash
git push origin main
```

Render will:
- Pull latest code
- Rebuild Docker image
- Redeploy service

### Resource Considerations

**Free Plan**
- Suitable for development and testing
- Services sleep after 15 minutes of inactivity
- 750 hours/month free (approximately 31 days)


### GitHub Actions for Weekly Reports

Run weekly reports via GitHub Actions:

Create `.github/workflows/weekly_report.yml`:
```yaml
name: Weekly Research Report

on:
  schedule:
    - cron: '0 0 * * 1'  # Every Monday at midnight UTC
  workflow_dispatch:  # Manual trigger

jobs:
  generate-report:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install LaTeX
      run: |
        sudo apt-get update
        sudo apt-get install -y texlive-xetex texlive-fonts-recommended texlive-latex-extra
    
    - name: Install Python dependencies
      run: |
        cd server
        pip install -r requirements.txt
    
    - name: Run weekly report
      env:
        # Database
        SUPABASE_DATABASE_URL: ${{ secrets.SUPABASE_DATABASE_URL }}
        USE_SUPABASE: true
        
        # API Keys
        LLAMA_CLOUD_API_KEY: ${{ secrets.LLAMA_CLOUD_API_KEY }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        
        # Supabase Storage
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        SUPABASE_PAPERS_BUCKET: papers
        SUPABASE_REPORTS_BUCKET: reports
        
        # Email Configuration
        EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
        EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        EMAIL_RECEIVER: ${{ secrets.EMAIL_RECEIVER }}
        SMTP_SERVER: smtp.gmail.com
        SMTP_PORT: 587
        
        # Model Configuration (optional, have defaults)
        WRITING_MODEL_NAME: gpt-4o
        WRITING_MODEL_TEMPERATURE: 0.2
        DEDUCE_MODEL_NAME: o3-mini
        EMBEDDING_MODEL_NAME: text-embedding-3-small
        
        # Document Processing (optional, have defaults)
        CHUNK_SIZE: 1024
        CHUNK_OVERLAP: 200
      run: |
        cd server
        python run_weekly_report.py
```

Add secrets in GitHub: Repository → Settings → Secrets and variables → Actions

Required secrets to add:
- `SUPABASE_DATABASE_URL`
- `LLAMA_CLOUD_API_KEY`
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `EMAIL_SENDER`
- `EMAIL_PASSWORD`
- `EMAIL_RECEIVER`

---


## License

MIT
