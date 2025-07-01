#!/usr/bin/env python3
"""
Simple test script for ReportLab PDF generation functionality
"""

import json
import os
from pathlib import Path
from pdf_generator_simple import ResumePDFGenerator, create_pdf_from_json

def create_sample_resume_data():
    """Create sample resume data for testing"""
    return {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1 (555) 123-4567",
            "location": "New York, NY",
            "linkedin": "linkedin.com/in/johndoe"
        },
        "professional_summary": "Experienced software engineer with 5+ years of expertise in full-stack development, specializing in Python, React, and cloud technologies. Proven track record of delivering scalable solutions and leading cross-functional teams.",
        "work_experience": [
            {
                "position": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "New York, NY",
                "start_date": "2021-01",
                "end_date": "Present",
                "responsibilities": [
                    "Led development of microservices architecture serving 10M+ users",
                    "Mentored 3 junior developers and improved team productivity by 40%",
                    "Implemented automated testing pipeline reducing deployment time by 60%",
                    "Collaborated with product managers to define technical requirements"
                ]
            },
            {
                "position": "Software Engineer",
                "company": "StartupXYZ",
                "location": "San Francisco, CA",
                "start_date": "2019-06",
                "end_date": "2020-12",
                "responsibilities": [
                    "Developed RESTful APIs using Python Flask and PostgreSQL",
                    "Built responsive web applications using React and TypeScript",
                    "Optimized database queries improving application performance by 50%",
                    "Participated in agile development process and code reviews"
                ]
            }
        ],
        "skills": {
            "Programming Languages": ["Python", "JavaScript", "TypeScript", "Java"],
            "Frameworks & Libraries": ["React", "Flask", "Django", "Node.js"],
            "Databases": ["PostgreSQL", "MongoDB", "Redis"],
            "Cloud & DevOps": ["AWS", "Docker", "Kubernetes", "CI/CD"]
        },
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Technology",
                "graduation_date": "2019-05",
                "gpa": "3.8"
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "date": "2022-03"
            },
            {
                "name": "Certified Kubernetes Administrator",
                "issuer": "Cloud Native Computing Foundation",
                "date": "2021-11"
            }
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Built a scalable e-commerce platform with microservices architecture, handling 50K+ daily transactions",
                "technologies": ["Python", "React", "PostgreSQL", "Redis", "AWS"]
            },
            {
                "name": "Real-time Chat Application",
                "description": "Developed a real-time messaging application with WebSocket support and user authentication",
                "technologies": ["Node.js", "React", "Socket.io", "MongoDB"]
            }
        ]
    }

def test_pdf_generation():
    """Test PDF generation functionality"""
    print("Testing ReportLab PDF generation...")
    
    # Create sample data
    resume_data = create_sample_resume_data()
    
    # Create test directories
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    json_path = test_dir / "sample_resume.json"
    pdf_path = test_dir / "sample_resume.pdf"
    
    try:
        # Save sample JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2)
        print(f"✓ Created sample JSON: {json_path}")
        
        # Test PDF generation using generator class
        generator = ResumePDFGenerator()
        success = generator.generate_pdf(resume_data, str(pdf_path))
        
        if success and pdf_path.exists():
            print(f"✓ PDF generated successfully: {pdf_path}")
            print(f"  File size: {pdf_path.stat().st_size} bytes")
        else:
            print("✗ PDF generation failed")
            return False
        
        # Test convenience function
        pdf_path_2 = test_dir / "sample_resume_2.pdf"
        success_2 = create_pdf_from_json(str(json_path), str(pdf_path_2))
        
        if success_2 and pdf_path_2.exists():
            print(f"✓ PDF generated using convenience function: {pdf_path_2}")
            print(f"  File size: {pdf_path_2.stat().st_size} bytes")
        else:
            print("✗ Convenience function failed")
            return False
        
        print("\n🎉 All tests passed! PDF generation is working correctly.")
        print(f"\nGenerated files:")
        print(f"  JSON: {json_path.absolute()}")
        print(f"  PDF 1: {pdf_path.absolute()}")
        print(f"  PDF 2: {pdf_path_2.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== ReportLab PDF Generation Test ===\n")
    
    # Test PDF generation
    pdf_success = test_pdf_generation()
    
    print(f"\n=== Test Results ===")
    print(f"PDF Generation: {'✓ PASS' if pdf_success else '✗ FAIL'}")
    
    if pdf_success:
        print("\n🎉 ReportLab PDF generation working!")
        print("\nYou can now:")
        print("1. Install dependencies: pip install reportlab")
        print("2. Run the FastAPI server: python main.py")
        print("3. Use the API endpoints to generate tailored resumes with PDF support")
    else:
        print("\n❌ PDF generation failed. Please check the error messages above.") 