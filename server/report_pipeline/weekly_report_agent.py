import os
import re
import uuid
from datetime import datetime, timedelta, date
from typing import List

from llama_index.embeddings.openai import OpenAIEmbedding

from utils.tex_to_pdf import TeXCompiler
from utils.latex_utils import clean_latex_output, escape_latex_text, escape_latex_preserve_math
from sqlmodel import Session, select, desc
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from jinja2 import Template

from database import engine
from models import Paper,Report
from config import REPORT_DIR, get_embed_model, get_writing_model
from managers.storage_manager import StorageManager, REPORTS_BUCKET, get_supabase_client

embed_model = get_embed_model()
writing_model = get_writing_model()

#Latex template

LATEX_TEMPLATE = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\usepackage{geometry}
\usepackage{amssymb}
\usepackage{amsmath}
\usepackage{amsthm}
\usepackage{amsfonts}
\geometry{a4paper, margin=1in}
\usepackage{enumitem}

\title{ {{ report_title }} }
\author{ AI Research Agent }
\date{ {{ report_date }} }

\begin{document}

\maketitle

\section*{Summary}
{{ summary }}

\section*{Papers ({{ papers|length }})}

{% for paper in papers %}
\subsection*{ {{ paper.title }} }
\textbf{Authors:} {{ paper.authors }} \\
\textbf{Arxiv ID:} \href{ {{ paper.url }} }{ {{ paper.arxiv_id }} }

\begin{itemize}
    \item \textbf{Abstract:} \textit{ {{ paper.abstract }} }
    \item \textbf{AI summary:} {{ paper.summary }}
\end{itemize}

\vspace{0.5cm}
\hrule
\vspace{0.5cm}

{% endfor %}

\end{document}
"""

def get_paper(session:Session, topic:str, start_date:datetime, end_date:datetime):
    statement = select(Paper).where(Paper.topic == topic).where(Paper.published_date >= start_date).where(Paper.published_date <= end_date).order_by(desc(Paper.published_date))
    return session.exec(statement).all()

def generate_ai_summary(session:Session, paper:Paper):
    prompt = ChatPromptTemplate.from_template("""
        You are a helpful research assistant. You are given a paper and you need to generate a summary of the paper.
        Read the following abstract and generate a summary of the paper. Requirements:
        1. Keep it short and concise, no more than 100 words, but at least 50 words.
        2. Use latex format for mathematical notation. Keep the notation consistent with the paper as much as possible.
        3. Mainly discuss the key contributions of the paper, the main results, and the main or novel ideas of the paper.
        4. Use "this paper" to refer to the paper, "the authors" to refer to the authors.
        5. IMPORTANT: Return ONLY the summary text content with LaTeX math notation. 
           Any Greek letters should be written in LaTeX format. Respect the original latex format in the markdown files you recieve.
           DO NOT include any document structure commands like \\documentclass, \\begin{{document}}, \\end{{document}}, etc.
           DO NOT wrap your response in markdown code blocks (no ```latex or ```).
           Just return plain text with inline LaTeX math notation.

        Title: {title}

        Abstract: {abstract}

        Available LaTeX packages in the template: amssymb, amsmath, amsthm, amsfonts, hyperref, geometry, enumitem
    """)

    try:
        content = (prompt | writing_model).invoke({
        "title": paper.title, 
        "abstract": paper.abstract,
        "template": LATEX_TEMPLATE
    }).content     

        summary = ""
        if isinstance(content, str):
            summary = content.strip()
        else:
            # if list of strings, convert to string
            summary = "".join(str(item) for item in content).strip()
        
        # Clean the output to remove any unwanted LaTeX structure or markdown
        summary = clean_latex_output(summary)

        #update paper summary in database
        paper.summary = summary
        session.add(paper)
        session.commit()
        session.refresh(paper)
        return summary
        
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        return "Error: No summary generated"

def generate_report(topic:str, start_date:datetime, end_date:datetime):
    print("Writer Agent started...")
    
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    with Session(engine) as session:
        papers = get_paper(session, topic, start_date, end_date)
        if not papers:
            return
        
        #1. generate summary for each paper
        summaries = []
        rendered_papers = []
        final_summary = ""
        for paper in papers:
            paper_summary = generate_ai_summary(session,paper)
            summaries.append(paper_summary)
            #put summary into list and template
            rendered_papers.append({
                "title": escape_latex_preserve_math(paper.title),
                "authors": escape_latex_text(paper.authors),
                "url": paper.arxiv_url,
                "arxiv_id": paper.id,
                "abstract": escape_latex_preserve_math(paper.abstract),
                "summary": paper_summary
            })

        #2 generate summary for all papers
        prompt = ChatPromptTemplate.from_template("""
            You are a helpful research assistant. 
            You are given a list of summaries of papers this week and you need to generate a report explaining the key contributions and main results of the papers
            in the field of research this week. Requirements:
            1. Keep it no more than 150 words, but more than 50 words (at least 2 sentences).
            2. Use latex format for mathematical notation.
            3. IMPORTANT: Return ONLY the summary text content with LaTeX math notation.
               Any Greek letters should be written in LaTeX format. Respect the original latex format in the markdown files you recieve.
               DO NOT include any document structure commands like \\documentclass, \\begin{{document}}, \\end{{document}}, etc.
               DO NOT wrap your response in markdown code blocks (no ```latex or ```).
               Just return plain text with inline LaTeX math notation.

            Available LaTeX packages: amssymb, amsmath, amsthm, amsfonts, hyperref, geometry, enumitem
            
            Summaries: {summaries}
        """)

        final_summary_raw = (prompt | writing_model).invoke({"summaries": summaries}).content
        
        # Convert to string if needed
        if isinstance(final_summary_raw, str):
            final_summary_str = final_summary_raw
        else:
            final_summary_str = "".join(str(item) for item in final_summary_raw)
        
        # Clean the output to remove any unwanted LaTeX structure or markdown
        final_summary = clean_latex_output(final_summary_str)

        #3 turn into latex format
        date_str = date.today().strftime("%Y-%m-%d")
        report_title = f"Weekly Report for {topic} - {date_str}"

        template = Template(LATEX_TEMPLATE)
        latex_source = template.render(
            report_title=escape_latex_preserve_math(report_title),
            report_date=date_str,
            summary=final_summary,
            papers=rendered_papers
        )


        #4 save the latex file
        filename = f"report_{date.today().strftime('%Y%m%d')}.tex"
        topic_safe = topic.replace(' ', '_')
        year = date.today().strftime("%Y")
        month = date.today().strftime("%m")
        filepath = os.path.join(REPORT_DIR,topic_safe,year,month,filename)

        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(latex_source)
        
        print(f"LaTeX report generated: {filepath}")

        #5 compile latex to pdf
        compiler = TeXCompiler(engine="xelatex")
        pdf_path = filepath.replace(".tex", ".pdf")
        if compiler.compile(filepath):
            print(f"PDF report generated: {pdf_path}")
        else:
            print("Failed to compile LaTeX to PDF, PDF may have some errors.")

            

        #6 Prepare storage paths
        # display_path: relative path for frontend tree display
        # storage_url: actual storage location
        pdf_filename = filename.replace(".tex", ".pdf")
        display_path = f"weekly_reports/{topic_safe}/{year}/{month}/{pdf_filename}"
        storage_url = f"{REPORTS_BUCKET}/{display_path}"
        if StorageManager.is_supabase_mode() and os.path.exists(pdf_path):
            # Upload to Supabase Storage
            try:
                with open(pdf_path, 'rb') as f:
                    file_content = f.read()
                
                client = get_supabase_client()
                client.storage.from_(REPORTS_BUCKET).upload(
                    path=display_path,
                    file=file_content,
                    file_options={"content-type": "application/pdf"}
                )
                
                print(f" Uploaded report to Supabase Storage: {storage_url}")
                
            except Exception as e:
                print(f" Failed to upload report to Supabase Storage: {e}")
        
        #7 save md file to database with embedding
        content_md = f"# {report_title}\n\n## Executive Summary\n{final_summary}\n\n## Papers\n"
        for p in rendered_papers:
            content_md += f"### {p['title']}\n* **Contribution:** {p['summary']}\n\n"
        content_md.strip()
        embedding = embed_model.get_text_embedding(content_md)
        report = Report(
            id = str(uuid.uuid4()),
            topic = topic,
            start_date = start_date,
            end_date = end_date,
            local_pdf_path = pdf_path,
            storage_url = storage_url,      
            title = report_title,
            content_md = content_md,
            summary_embedding = embedding
        )

        session.add(report)
        session.commit()
        session.refresh(report)

        print(f"Report saved to database: {report.title}")
        return report
