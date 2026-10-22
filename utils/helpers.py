"""
Helper utilities for text cleaning, regex information extraction,
section parsing, and sample datasets.
"""

import re
from typing import Dict, List, Optional, Tuple


def clean_text(text: str) -> str:
    """
    Cleans raw extracted text: removes non-printable characters,
    normalizes excessive whitespace, and preserves punctuation.
    """
    if not text:
        return ""
    # Replace non-breaking spaces and odd unicode spaces
    cleaned = text.replace("\u00a0", " ").replace("\u200b", "")
    # Standardize bullet point symbols
    cleaned = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25CF]", "\n* ", cleaned)
    # Remove multiple consecutive blank lines
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)
    # Strip trailing whitespace on each line
    lines = [line.strip() for line in cleaned.splitlines()]
    return "\n".join(lines).strip()


def extract_email(text: str) -> Optional[str]:
    """
    Extracts the first valid email address found in the text.
    """
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """
    Extracts a phone number supporting international, domestic, and dotted formats.
    """
    phone_pattern = r"(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4})"
    matches = re.findall(phone_pattern, text)
    for m in matches:
        cleaned_m = re.sub(r"[^\d+]", "", m)
        # Reasonable phone length between 7 and 15 digits
        if 10 <= len(cleaned_m) <= 15:
            return m.strip()
    return None


def extract_links(text: str) -> Dict[str, Optional[str]]:
    """
    Extracts links such as LinkedIn, GitHub, and portfolio URLs.
    """
    links: Dict[str, Optional[str]] = {
        "linkedin": None,
        "github": None,
        "portfolio": None
    }
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
    if linkedin_match:
        links["linkedin"] = linkedin_match.group(0)

    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
    if github_match:
        links["github"] = github_match.group(0)

    portfolio_match = re.search(r"(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.(?:io|me|dev|app|com)(?:/[^\s]*)?", text, re.IGNORECASE)
    if portfolio_match and portfolio_match.group(0) != links["linkedin"] and portfolio_match.group(0) != links["github"]:
        links["portfolio"] = portfolio_match.group(0)

    return links


def extract_sections(text: str) -> Dict[str, str]:
    """
    Splits resume text into common sections using header pattern detection.
    """
    section_patterns = {
        "summary": r"(?:summary|professional summary|profile|about me|objective)",
        "experience": r"(?:experience|work experience|employment history|professional experience)",
        "education": r"(?:education|academic background|qualifications)",
        "skills": r"(?:skills|technical skills|core competencies|technologies)",
        "projects": r"(?:projects|key projects|personal projects|technical projects)",
        "certifications": r"(?:certifications|licenses|certificates|achievements)"
    }

    sections: Dict[str, str] = {k: "" for k in section_patterns}
    sections["header"] = ""

    lines = text.splitlines()
    current_section = "header"
    section_buffers: Dict[str, List[str]] = {k: [] for k in sections}

    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue

        matched_section = None
        # Check if line matches a known section header
        if len(cleaned_line.split()) <= 4:
            clean_hdr = re.sub(r"[:\-_#*]", "", cleaned_line).strip().lower()
            for sec_name, pattern in section_patterns.items():
                if re.fullmatch(pattern, clean_hdr, re.IGNORECASE):
                    matched_section = sec_name
                    break

        if matched_section:
            current_section = matched_section
        else:
            section_buffers[current_section].append(cleaned_line)

    for k in sections:
        sections[k] = "\n".join(section_buffers[k]).strip()

    return sections


# Sample Resumes and Sample Job Descriptions for instantaneous UI testing
SAMPLE_RESUMES = {
    "AI / ML Engineer": """Alex Mercer
alex.mercer@email.com | +1 (555) 234-5678 | San Francisco, CA
LinkedIn: linkedin.com/in/alex-mercer | GitHub: github.com/alexmercer

PROFESSIONAL SUMMARY
Senior Machine Learning Engineer with 5+ years of experience designing scalable deep learning pipelines, NLP systems, and predictive models. Expert in Python, PyTorch, TensorFlow, and AWS cloud infrastructure.

TECHNICAL SKILLS
- Programming: Python, SQL, C++, Bash
- ML/AI: Machine Learning, Deep Learning, NLP, Computer Vision, Transformers, Hugging Face, PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy
- Cloud & MLOps: AWS (S3, EC2, SageMaker), Docker, Kubernetes, CI/CD, MLflow
- Databases: PostgreSQL, MongoDB, Redis

WORK EXPERIENCE
Senior Machine Learning Engineer | DataVision AI | 2021 - Present
- Architected and deployed an end-to-end NLP document classification pipeline processing 1.5M requests/day, reducing inference latency by 35%.
- Fine-tuned transformer models (BERT, RoBERTa) achieving 94.2% F1-score for automated contract review.
- Scaled training pipelines across distributed AWS SageMaker clusters, cutting monthly GPU spend by $42,000.
- Mentored a cross-functional team of 5 junior data scientists and conducted code reviews.

Machine Learning Engineer | Apex Analytics | 2018 - 2021
- Developed customer churn prediction models using XGBoost and Scikit-learn, improving customer retention by 18%.
- Built automated feature engineering pipelines in Pandas and SQL processing 200GB+ tables daily.
- Containerized model microservices using Docker and deployed on Kubernetes with 99.9% uptime.

PROJECTS
- LLM Agentic Query Engine: Built a LangChain and Hugging Face retrieval system indexing 50,000 research papers with vector embeddings.
- VisionQA: Developed an open-source PyTorch computer vision model with 88% Top-1 accuracy.

EDUCATION
Master of Science in Computer Science | Stanford University | 2018
Bachelor of Science in Computer Engineering | UC Berkeley | 2016

CERTIFICATIONS
- AWS Certified Machine Learning - Specialty
- Deep Learning Specialization (Coursera)
""",

    "Full-Stack Python & React Developer": """Jordan Lee
jordan.lee@devmail.io | +1 (415) 890-1234 | Austin, TX
LinkedIn: linkedin.com/in/jordanlee-dev | GitHub: github.com/jordanleedev

PROFESSIONAL SUMMARY
Dynamic Full-Stack Software Engineer with 4 years of experience crafting responsive web applications, robust REST APIs, and microservices using Python, Django, React, and PostgreSQL.

SKILLS
- Languages: Python, JavaScript, TypeScript, HTML5, CSS3, SQL
- Frontend: React, Redux, Tailwind CSS, Next.js, Material UI
- Backend: Django, FastAPI, Flask, REST API, Node.js, Express
- Cloud & Tools: AWS, Docker, Git, GitHub Actions, Linux, Nginx, Pytest
- Databases: PostgreSQL, MySQL, Redis

EXPERIENCE
Full-Stack Developer | CloudTech Solutions | 2022 - Present
- Engineered high-traffic SaaS portal using React, TypeScript, and FastAPI, supporting 120,000 active monthly users.
- Redesigned backend REST API endpoints, decreasing response times from 450ms to 110ms.
- Built reusable React UI component library adopted across 6 company-wide frontend products.
- Automated CI/CD testing workflows using GitHub Actions and Pytest, boosting test coverage to 92%.

Software Engineer | NextGen Apps | 2020 - 2022
- Built e-commerce web applications with Django and React, integrating Stripe payment processing for $1.2M in annual transactions.
- Migrated legacy monolithic architecture into Docker containers on AWS ECS.
- Designed relational database schemas in PostgreSQL with optimized query indexing.

PROJECTS
- DevPulse Analytics: Real-time telemetry dashboard built with React, FastAPI, Redis, and Plotly.
- TaskFlow Pro: Full-stack Kanban task manager using React, Node.js, Express, and PostgreSQL.

EDUCATION
Bachelor of Science in Software Engineering | University of Texas at Austin | 2020

CERTIFICATIONS
- AWS Certified Developer - Associate
- Meta Front-End Developer Professional Certificate
"""
}

SAMPLE_JOB_DESCRIPTIONS = {
    "Senior Machine Learning Engineer": """Senior Machine Learning Engineer

Company: NextGen AI Solutions
Location: San Francisco, CA (Hybrid / Remote)
Experience Level: 4-6 years

About the Role:
We are seeking an experienced Senior Machine Learning Engineer to design, deploy, and scale state-of-the-art NLP and generative AI systems. You will collaborate with engineering and product teams to integrate machine learning models into production systems handling millions of users.

Key Responsibilities:
- Design, train, and deploy machine learning and deep learning models using Python, PyTorch, and Hugging Face.
- Build production NLP pipelines, transformers, and LLM-powered applications.
- Scale model inference and training on AWS cloud infrastructure using Docker, Kubernetes, and MLflow.
- Optimize feature pipelines with Pandas, NumPy, and SQL on PostgreSQL and BigQuery.
- Ensure high code quality through unit testing, Pytest, and CI/CD automation.

Requirements:
- 4+ years of professional software engineering and machine learning experience.
- Deep expertise in Python, PyTorch or TensorFlow, and Scikit-learn.
- Strong hands-on experience with NLP, Transformers, and LLMs.
- Proficiency in AWS services (SageMaker, S3, EC2) and containerization with Docker and Kubernetes.
- Solid understanding of relational databases (PostgreSQL, SQL) and distributed systems.
- Master's or Bachelor's degree in Computer Science, Data Science, or related quantitative field.

Nice to Have:
- Experience with LangChain, Vector databases, and LLM fine-tuning.
- Contributions to open-source ML libraries.
- AWS Certified Machine Learning - Specialty.
""",

    "Full-Stack Python Engineer": """Full-Stack Software Engineer (Python & React)

Company: Apex Cloud Systems
Location: Remote / Austin, TX
Experience: 3-5 years

Role Overview:
We are looking for a skilled Full-Stack Software Engineer to build and maintain scalable enterprise SaaS applications. You will be responsible for both frontend client interfaces and backend microservices architecture.

Responsibilities:
- Develop responsive, accessible web applications using React, TypeScript, and modern CSS/Tailwind CSS.
- Architect high-performance backend microservices using Python, FastAPI or Django, and REST APIs.
- Manage database models and query performance across PostgreSQL and Redis.
- Write unit and integration tests with Pytest and Jest to maintain 90%+ code coverage.
- Deploy and monitor cloud applications on AWS utilizing Docker containers and CI/CD pipelines.

Qualifications:
- 3+ years of professional full-stack development experience.
- Strong proficiency in Python, JavaScript, and TypeScript.
- Extensive experience with React and state management (Redux).
- Proven track record designing RESTful APIs and backend services with FastAPI or Django.
- Hands-on experience with Docker, AWS, and Git workflows.
- Bachelor's degree in Computer Science or equivalent work experience.
"""
}
