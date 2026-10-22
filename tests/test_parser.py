"""
Unit tests for PDF extraction and Resume parsing modules.
"""

import io
import sys
from pathlib import Path
import pytest
from fpdf import FPDF

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyzer.pdf_parser import extract_text_from_pdf, PDFParseResult
from analyzer.resume_parser import ResumeParser
from utils.helpers import clean_text, extract_email, extract_phone, extract_links


def create_sample_pdf_bytes(content: str) -> bytes:
    """Helper to generate in-memory valid PDF bytes."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    for line in content.splitlines():
        pdf.cell(text=line, new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())


class TestPDFParser:
    """Tests for PDF extraction and error handling."""

    def test_valid_pdf_extraction(self):
        text_content = "Jane Doe\njane.doe@company.com\nSenior Python Developer"
        pdf_bytes = create_sample_pdf_bytes(text_content)
        result = extract_text_from_pdf(pdf_bytes)

        assert isinstance(result, PDFParseResult)
        assert result.is_valid is True
        assert result.num_pages >= 1
        assert "Jane Doe" in result.text
        assert "jane.doe@company.com" in result.text
        assert result.error_message is None

    def test_corrupt_pdf_bytes(self):
        corrupt_data = b"%PDF-corrupted-stream-data-without-valid-structures"
        result = extract_text_from_pdf(corrupt_data)
        assert result.is_valid is False
        assert result.error_message is not None

    def test_non_pdf_file_handling(self):
        txt_data = b"This is a plain text file, not a PDF."
        result = extract_text_from_pdf(txt_data)
        assert result.is_valid is False
        assert "Invalid file format" in result.error_message

    def test_empty_bytes_handling(self):
        result = extract_text_from_pdf(b"")
        assert result.is_valid is False
        assert result.error_message is not None

    def test_nonexistent_file_path(self):
        result = extract_text_from_pdf("non_existent_resume_file_xyz.pdf")
        assert result.is_valid is False
        assert "File not found" in result.error_message


class TestResumeParser:
    """Tests for structured information extraction from resumes."""

    @pytest.fixture
    def sample_resume_text(self):
        return """
        Sarah Connor
        sarah.connor@cyberdyne.io | +1 (555) 987-6543 | Los Angeles, CA
        LinkedIn: linkedin.com/in/sarah-connor | GitHub: github.com/sarahconnor

        PROFESSIONAL SUMMARY
        Experienced Cloud Architect with 6+ years in distributed systems, AWS, and Kubernetes.

        TECHNICAL SKILLS
        - Cloud: AWS, Docker, Kubernetes, Terraform, CI/CD
        - Languages: Python, Go, SQL, Bash
        - Databases: PostgreSQL, Redis

        WORK EXPERIENCE
        Principal Cloud Architect | SkyNet Security | 2020 - Present
        - Architected multi-region AWS cloud infrastructure supporting 5M daily active users.
        - Reduced cloud infrastructure costs by 28% through autoscaling optimization.
        - Spearheaded migration of 40 microservices to Kubernetes clusters.

        Cloud Engineer | TechOps Global | 2017 - 2020
        - Developed automated CI/CD deployment pipelines using GitHub Actions and Docker.
        - Maintained 99.99% service availability across distributed PostgreSQL clusters.

        EDUCATION
        Master of Science in Computer Science | Stanford University | 2017
        Bachelor of Science in Electrical Engineering | UCLA | 2015

        CERTIFICATIONS
        - AWS Certified Solutions Architect - Professional
        - Certified Kubernetes Administrator (CKA)
        """

    def test_contact_extraction(self, sample_resume_text):
        email = extract_email(sample_resume_text)
        phone = extract_phone(sample_resume_text)
        links = extract_links(sample_resume_text)

        assert email == "sarah.connor@cyberdyne.io"
        assert phone is not None and "987-6543" in phone
        assert links["linkedin"] == "linkedin.com/in/sarah-connor"
        assert links["github"] == "github.com/sarahconnor"

    def test_resume_parser_end_to_end(self, sample_resume_text):
        parser = ResumeParser()
        data = parser.parse(sample_resume_text)

        assert data.name is not None
        assert "Sarah" in data.name
        assert data.email == "sarah.connor@cyberdyne.io"
        assert len(data.skills) >= 6
        assert "AWS" in data.skills
        assert "Docker" in data.skills
        assert "Kubernetes" in data.skills
        assert "Python" in data.skills

        # Education
        assert len(data.education) >= 1
        assert any("Master" in edu["degree"] or "Science" in edu["degree"] for edu in data.education)

        # Experience calculation: 2017 - Present should be around 7-9 years
        assert data.experience_years >= 6.0

        # Bullet point analysis
        assert len(data.bullet_points) >= 4
        # Check action verbs and metrics detected
        metrics_found = [bp for bp in data.bullet_points if bp.has_metric]
        assert len(metrics_found) >= 2
