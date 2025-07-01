import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

class ResumePDFGenerator:
    """
    A service for generating professional PDF resumes from JSON data using ReportLab
    """
    
    def __init__(self):
        """Initialize the PDF generator"""
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom styles for the resume"""
        # Name/Header style
        self.styles.add(ParagraphStyle(
            name='ResumeTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.grey
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=2,
            textColor=colors.black
        ))
        
        # Company/Date style
        self.styles.add(ParagraphStyle(
            name='CompanyDate',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            textColor=colors.darkgrey,
            fontName='Helvetica-Oblique'
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=3,
            textColor=colors.black
        ))
        
        # Skills style
        self.styles.add(ParagraphStyle(
            name='Skills',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            textColor=colors.black
        ))
    
    def generate_pdf(self, 
                     resume_data: Dict[str, Any], 
                     output_path: str) -> bool:
        """
        Generate a PDF resume from JSON data
        
        Args:
            resume_data (Dict[str, Any]): Resume data in JSON format
            output_path (str): Path where the PDF should be saved
            
        Returns:
            bool: True if PDF was generated successfully, False otherwise
        """
        try:
            # Normalize the resume data
            normalized_data = self._normalize_resume_data(resume_data)
            
            # Create the PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch,
                leftMargin=0.75*inch,
                rightMargin=0.75*inch
            )
            
            # Build the story (content)
            story = []
            
            # Add header
            self._add_header(story, normalized_data.get('personal_info', {}))
            
            # Add professional summary
            if normalized_data.get('professional_summary'):
                self._add_professional_summary(story, normalized_data['professional_summary'])
            
            # Add work experience
            if normalized_data.get('work_experience'):
                self._add_work_experience(story, normalized_data['work_experience'])
            
            # Add skills
            if normalized_data.get('skills'):
                self._add_skills(story, normalized_data['skills'])
            
            # Add education
            if normalized_data.get('education'):
                self._add_education(story, normalized_data['education'])
            
            # Add certifications
            if normalized_data.get('certifications'):
                self._add_certifications(story, normalized_data['certifications'])
            
            # Add projects
            if normalized_data.get('projects'):
                self._add_projects(story, normalized_data['projects'])
            
            # Build the PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
    
    def _add_header(self, story: List, personal_info: Dict[str, Any]):
        """Add header with name and contact information"""
        # Name
        name = personal_info.get('name', 'Your Name')
        story.append(Paragraph(name, self.styles['ResumeTitle']))
        
        # Contact information
        contact_parts = []
        if personal_info.get('email'):
            contact_parts.append(personal_info['email'])
        if personal_info.get('phone'):
            contact_parts.append(personal_info['phone'])
        if personal_info.get('location'):
            contact_parts.append(personal_info['location'])
        if personal_info.get('linkedin'):
            contact_parts.append(personal_info['linkedin'])
        
        if contact_parts:
            contact_text = ' • '.join(contact_parts)
            story.append(Paragraph(contact_text, self.styles['ContactInfo']))
    
    def _add_professional_summary(self, story: List, summary: str):
        """Add professional summary section"""
        story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['SectionHeading']))
        story.append(Paragraph(summary, self.styles['Normal']))
        story.append(Spacer(1, 6))
    
    def _add_work_experience(self, story: List, experience: List[Dict[str, Any]]):
        """Add work experience section"""
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", self.styles['SectionHeading']))
        
        for job in experience:
            # Job title
            title = job.get('position') or job.get('title', 'Position')
            story.append(Paragraph(title, self.styles['JobTitle']))
            
            # Company and dates
            company = job.get('company', 'Company')
            start_date = job.get('start_date', '')
            end_date = job.get('end_date', 'Present')
            location = job.get('location', '')
            
            company_info = f"{company}"
            if location:
                company_info += f" • {location}"
            if start_date:
                company_info += f" • {start_date} - {end_date}"
            
            story.append(Paragraph(company_info, self.styles['CompanyDate']))
            
            # Responsibilities
            if job.get('responsibilities'):
                for responsibility in job['responsibilities']:
                    bullet_text = f"• {responsibility}"
                    story.append(Paragraph(bullet_text, self.styles['BulletPoint']))
            
            story.append(Spacer(1, 8))
    
    def _add_skills(self, story: List, skills: Any):
        """Add skills section"""
        story.append(Paragraph("SKILLS", self.styles['SectionHeading']))
        
        if isinstance(skills, dict):
            # Categorized skills
            for category, skill_list in skills.items():
                category_text = f"<b>{category}:</b> "
                if isinstance(skill_list, list):
                    category_text += ', '.join(skill_list)
                else:
                    category_text += str(skill_list)
                story.append(Paragraph(category_text, self.styles['Skills']))
        elif isinstance(skills, list):
            # Simple skill list
            skills_text = ', '.join(skills)
            story.append(Paragraph(skills_text, self.styles['Skills']))
        
        story.append(Spacer(1, 6))
    
    def _add_education(self, story: List, education: List[Dict[str, Any]]):
        """Add education section"""
        story.append(Paragraph("EDUCATION", self.styles['SectionHeading']))
        
        for edu in education:
            # Degree
            degree = edu.get('degree', 'Degree')
            story.append(Paragraph(degree, self.styles['JobTitle']))
            
            # Institution and date
            institution = edu.get('institution') or edu.get('school', 'Institution')
            grad_date = edu.get('graduation_date') or edu.get('end_date', '')
            gpa = edu.get('gpa', '')
            
            edu_info = institution
            if grad_date:
                edu_info += f" • {grad_date}"
            if gpa:
                edu_info += f" • GPA: {gpa}"
            
            story.append(Paragraph(edu_info, self.styles['CompanyDate']))
            story.append(Spacer(1, 6))
    
    def _add_certifications(self, story: List, certifications: List):
        """Add certifications section"""
        story.append(Paragraph("CERTIFICATIONS", self.styles['SectionHeading']))
        
        for cert in certifications:
            if isinstance(cert, dict):
                cert_name = cert.get('name', str(cert))
                issuer = cert.get('issuer', '')
                date = cert.get('date', '')
                
                cert_text = cert_name
                if issuer:
                    cert_text += f" - {issuer}"
                if date:
                    cert_text += f" ({date})"
            else:
                cert_text = str(cert)
            
            story.append(Paragraph(f"• {cert_text}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 6))
    
    def _add_projects(self, story: List, projects: List[Dict[str, Any]]):
        """Add projects section"""
        story.append(Paragraph("PROJECTS", self.styles['SectionHeading']))
        
        for project in projects:
            # Project name
            name = project.get('name') or project.get('title', 'Project')
            story.append(Paragraph(name, self.styles['JobTitle']))
            
            # Description
            if project.get('description'):
                story.append(Paragraph(project['description'], self.styles['Normal']))
            
            # Technologies
            if project.get('technologies'):
                if isinstance(project['technologies'], list):
                    tech_text = f"<b>Technologies:</b> {', '.join(project['technologies'])}"
                else:
                    tech_text = f"<b>Technologies:</b> {project['technologies']}"
                story.append(Paragraph(tech_text, self.styles['Skills']))
            
            story.append(Spacer(1, 6))
    
    def _normalize_resume_data(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize resume data to handle different field naming conventions
        
        Args:
            resume_data (Dict[str, Any]): Raw resume data
            
        Returns:
            Dict[str, Any]: Normalized resume data
        """
        normalized = {}
        
        # Handle personal information
        personal_info = {}
        for key in ['personal_info', 'personal_information', 'contact', 'header']:
            if key in resume_data:
                personal_info.update(resume_data[key])
                break
        
        # Fallback to root level fields
        if not personal_info:
            personal_fields = ['name', 'email', 'phone', 'location', 'linkedin', 'address']
            for field in personal_fields:
                if field in resume_data:
                    personal_info[field] = resume_data[field]
        
        normalized['personal_info'] = personal_info
        
        # Handle professional summary
        summary_fields = ['professional_summary', 'summary', 'objective', 'about']
        for field in summary_fields:
            if field in resume_data:
                normalized['professional_summary'] = resume_data[field]
                break
        
        # Handle work experience
        exp_fields = ['work_experience', 'experience', 'employment', 'jobs']
        for field in exp_fields:
            if field in resume_data:
                normalized['work_experience'] = resume_data[field]
                break
        
        # Handle skills
        skill_fields = ['skills', 'technical_skills', 'competencies']
        for field in skill_fields:
            if field in resume_data:
                normalized['skills'] = resume_data[field]
                break
        
        # Handle education
        edu_fields = ['education', 'academic', 'qualifications']
        for field in edu_fields:
            if field in resume_data:
                normalized['education'] = resume_data[field]
                break
        
        # Handle other sections
        other_sections = ['certifications', 'projects', 'achievements', 'awards']
        for section in other_sections:
            if section in resume_data:
                normalized[section] = resume_data[section]
        
        return normalized

def create_pdf_from_json(json_file_path: str, output_pdf_path: str) -> bool:
    """
    Convenience function to create PDF from JSON file
    
    Args:
        json_file_path (str): Path to the JSON resume file
        output_pdf_path (str): Path where the PDF should be saved
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        
        generator = ResumePDFGenerator()
        return generator.generate_pdf(resume_data, output_pdf_path)
        
    except Exception as e:
        print(f"Error creating PDF from JSON: {e}")
        return False 