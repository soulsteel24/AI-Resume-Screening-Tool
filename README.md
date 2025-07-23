# AI-Resume-Screening-Tool
🤖 AI-Powered Resume Screening Tool (ATS Simulator)
This project implements a simplified, AI-powered Resume Screening Tool, acting as an Applicant Tracking System (ATS) simulator. It helps users understand how well a resume matches a job description by leveraging Natural Language Processing (NLP) to extract keywords, calculate semantic similarity, and provide actionable feedback for improvement.

✨ Features
Job Description Input: Paste or manually enter the job description.

Resume Upload/Input: Upload a PDF resume (text extraction will be attempted) or paste resume content directly.

Keyword & Skill Extraction: Identifies common technical skills and keywords from both the job description and the resume.

Semantic Match Score: Calculates a similarity score based on the contextual meaning of the job description and resume using a pre-trained Sentence Transformer model (BERT-like).

Keyword Match Score: Provides a traditional ATS-like score based on the percentage of job description keywords found in the resume.

Match Visualization: Displays both semantic and keyword match scores using a bar chart for easy comparison.

Resume Improvement Suggestions: Offers targeted advice on how to improve the resume, including:

Skill Gap Analysis: Highlights keywords missing from the resume but present in the job description.

Semantic Alignment Tips: Guides on refining narratives and quantifying achievements to better match the job's context.

General Tailoring Advice: Provides best practices for resume customization.

🚀 Technologies Used
Python: The core programming language.

Streamlit: For creating the interactive web application interface.

Hugging Face Transformers (Sentence-Transformers library): Utilized for generating semantic embeddings and calculating similarity (specifically all-MiniLM-L6-v2 model).

PyPDF2: For extracting text content from PDF resume files.

Numpy & Re: For numerical operations and regular expression-based text processing.

⚙️ Setup and Installation
To run this application locally, follow these steps:

Clone the repository (if applicable):

git clone <your-repo-url>
cd <your-repo-name>

Create a virtual environment (recommended):

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

Install the required libraries:

pip install streamlit sentence-transformers PyPDF2 numpy

Save the application code:
Save the provided Python code (e.g., app.py) into the root directory of your project.

Run the Streamlit application:

streamlit run app.py

This command will open the application in your default web browser.

⚠️ Disclaimer
This tool is a simplified simulator for demonstration purposes. Real-world Applicant Tracking Systems (ATS) are significantly more complex, employing advanced parsing techniques, sophisticated ranking algorithms, and often integrating with broader HR management systems. The scores and suggestions provided by this tool are indicative and should be used as a guide for resume optimization, not as definitive evaluations.
