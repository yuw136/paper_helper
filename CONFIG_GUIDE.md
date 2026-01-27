# Configuration Guide

This guide explains how to configure the Paper Helper application using environment variables and configuration files.

## Quick Start

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your actual credentials in `.env`

3. Review and modify config files if needed (optional)

## Environment Variables

All environment variables are defined in `.env` file at the project root.

### Required Variables

**Database Configuration**
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: Database name (default: `paper_helper`)
- `DATABASE_URL`: Full PostgreSQL connection string

**API Keys**
- `LLAMA_CLOUD_API_KEY`: LlamaParse API key for PDF parsing
- `OPENAI_API_KEY`: OpenAI API key for embeddings and chat models
- `DEEPSEEK_API_KEY`: DeepSeek API key (if using DeepSeek models)

**LangChain Configuration**
- `LANGCHAIN_TRACING_V2`: Enable LangSmith tracing (`true` or `false`)
- `LANGCHAIN_API_KEY`: LangSmith API key for monitoring
- `LANGCHAIN_PROJECT`: Project name in LangSmith

**Email Configuration**
- `EMAIL_SENDER`: Sender email address
- `EMAIL_PASSWORD`: App-specific password (for Gmail, generate from account settings)
- `EMAIL_RECEIVER`: Recipient email address
- `SMTP_SERVER`: SMTP server address (default: `smtp.gmail.com`)
- `SMTP_PORT`: SMTP port (default: `587`)

### Optional Variables (Have Defaults)

**Model Settings**
- `WRITING_MODEL_NAME`: Writing model for text generation, summarization, report writing (default: `gpt-4o`)
- `WRITING_MODEL_TEMPERATURE`: Temperature for writing model (default: `0.2`)
- `DEDUCE_MODEL_NAME`: Reasoning model for judgment, math understanding, logical reasoning (default: `o3-mini`)
- `DEDUCE_MODEL_TEMPERATURE`: Temperature for deduce model (default: `0`)
- `EMBEDDING_MODEL_NAME`: Embedding model (default: `text-embedding-3-small`)

**Document Processing**
- `CHUNK_SIZE`: Text chunk size for vector storage (default: `1024`)
- `CHUNK_OVERLAP`: Overlap between chunks (default: `200`)

## Configuration Files

### 1. `server/config.py`

Main configuration file for the report pipeline and data processing.

**Key configurations:**
- **Path settings**: Data directories for PDFs, reports, metadata
- **Pipeline settings**: ArXiv search parameters, topic, categories
- **Model instances**: Embedding and writing model initialization

**To modify:**
- `TARGET_CATEGORIES`: List of ArXiv categories to search
- `TOPIC`: Research topic keyword
- `MAX_RESULTS`: Maximum papers to download
- `TIME_WINDOW_DAYS`: Days to look back for new papers

### 2. `server/chatbox/core/config.py`

Configuration for the chatbox/conversation module.

**Key configurations:**
- **CORS settings**: Allowed frontend origins
- **Pydantic Settings**: Type-safe environment variable loading
- **Model instances**: Writing model (for text generation) and deduce model (for reasoning) singletons
- **Database connection**: Session persistence settings
- **Model usage strategy**: Deduce model for reasoning tasks (route, grade, transform), writing model for generation tasks (summarize, generate, report)

**To modify:**
- `BACKEND_CORS_ORIGINS`: Add allowed frontend URLs for CORS
- Model functions: Customize model initialization if needed

## Notes

- Never commit `.env` file to version control (it's in `.gitignore`)
- Use app-specific passwords for email (not your regular password)
- For Gmail: Enable 2FA and generate app password at https://myaccount.google.com/apppasswords
- LangSmith tracing is optional but useful for debugging agent behavior
- All paths in config files are created automatically if they don't exist
