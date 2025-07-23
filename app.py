import streamlit as st
from sentence_transformers import SentenceTransformer, util
import numpy as np
import re
from collections import Counter
import PyPDF2

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

COMMON_TECH_SKILLS = [
    "python", "java", "c++", "javascript", "react", "angular", "vue.js", "node.js",
    "html", "css", "sql", "nosql", "mongodb", "postgresql", "mysql", "aws",
    "azure", "google cloud", "docker", "kubernetes", "git", "jenkins", "ci/cd",
    "agile", "scrum", "linux", "unix", "windows", "machine learning", "deep learning",
    "natural language processing", "nlp", "data science", "pytorch", "tensorflow",
    "scikit-learn", "pandas", "numpy", "spark", "hadoop", "kafka", "rest api",
    "graphql", "microservices", "frontend", "backend", "fullstack", "devops",
    "cloud computing", "cybersecurity", "blockchain", "ui/ux", "tableau", "power bi",
    "excel", "data analysis", "big data", "algorithms", "data structures",
    "software development", "web development", "mobile development", "android", "ios",
    "swift", "kotlin", "go", "rust", "php", "ruby", "rails", "django", "flask",
    "spring boot", "dotnet", "c#", "typescript", "bash", "shell scripting",
    "networking", "security", "testing", "qa", "automation", "jira", "confluence",
    "api design", "system design", "problem solving", "communication", "teamwork",
    "leadership", "project management", "data visualization", "cloud security",
    "containerization", "continuous integration", "continuous delivery", "database management",
    "distributed systems", "etl", "data warehousing", "big data analytics",
    "statistical analysis", "predictive modeling", "computer vision", "reinforcement learning",
    "devsecops", "site reliability engineering", "sre", "technical documentation",
    "unit testing", "integration testing", "end-to-end testing", "performance tuning"
]

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

def extract_keywords(text, skill_list):
    processed_text = preprocess_text(text)
    found_skills = set()

    sorted_skill_list = sorted(skill_list, key=len, reverse=True)

    for skill in sorted_skill_list:
        if len(skill.split()) > 1:
            if skill in processed_text:
                found_skills.add(skill)
        else:
            if re.search(r'\b' + re.escape(skill) + r'\b', processed_text):
                found_skills.add(skill)
    return list(found_skills)

def calculate_semantic_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0

    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)

    cosine_scores = util.cos_sim(embedding1, embedding2)
    return cosine_scores.item()

def calculate_keyword_match_score(jd_keywords, resume_keywords):
    if not jd_keywords:
        return 0.0

    jd_set = set(jd_keywords)
    resume_set = set(resume_keywords)
    common_keywords = jd_set.intersection(resume_set)

    score = (len(common_keywords) / len(jd_set)) * 100
    return score

st.set_page_config(page_title="AI Resume Screener", layout="wide")

st.title("🤖 AI-Powered Resume Screening Tool (ATS Simulator)")
st.markdown("""
    This tool helps you quickly assess how well a resume matches a job description
    by extracting keywords and calculating a semantic similarity score.
    Upload a resume (or paste text) and a job description to get started!
""")

col1, col2 = st.columns(2)

with col1:
    st.header("📄 Job Description")
    job_description = st.text_area(
        "Paste the Job Description here:",
        height=300,
        value="We are looking for a Python Developer with strong experience in Django, REST APIs, and PostgreSQL. Knowledge of AWS and Docker is a plus. Experience with Agile methodologies and Git is required. Familiarity with React or Angular for frontend development is a bonus. Strong problem-solving skills and teamwork are essential."
    )

with col2:
    st.header("🧑‍💻 Resume Content")
    uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])
    resume_content = ""

    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                for page_num in range(len(reader.pages)):
                    resume_content += reader.pages[page_num].extract_text() or ""
                if not resume_content:
                    st.warning("Could not extract text from the PDF. Please ensure it's not an image-only PDF or paste content manually.")
            except Exception as e:
                st.error(f"Error reading PDF: {e}. Please try pasting the content manually.")
                resume_content = ""
        else:
            st.warning("Unsupported file type. Please upload a .pdf file.")

        resume_content_manual = st.text_area(
            "Or paste Resume content here (if PDF parsing failed or for manual input):",
            height=300,
            value=resume_content
        )
        if resume_content_manual:
            resume_content = resume_content_manual

    else:
        resume_content = st.text_area(
            "Paste the Resume content here (or upload a PDF above):",
            height=300,
            value="Experienced Software Engineer with 5+ years in Python development. Proficient in Django, Flask, and building robust RESTful APIs. Hands-on experience with PostgreSQL and MongoDB. Successfully deployed applications on AWS using Docker. Skilled in Git, CI/CD pipelines, and Agile practices. Familiar with React.js for frontend. Excellent problem-solving and communication skills."
        )

if st.button("✨ Analyze Resume Match", use_container_width=True):
    if not job_description or not resume_content:
        st.warning("Please provide both a Job Description and Resume content to analyze.")
    else:
        st.subheader("📊 Analysis Results")

        st.markdown("---")
        st.subheader("🔍 Keyword & Skill Extraction")
        jd_keywords = extract_keywords(job_description, COMMON_TECH_SKILLS)
        resume_keywords = extract_keywords(resume_content, COMMON_TECH_SKILLS)

        st.write("**Job Description Keywords:**")
        if jd_keywords:
            st.code(", ".join(sorted(jd_keywords)))
        else:
            st.info("No common tech skills found in the Job Description.")

        st.write("**Resume Keywords:**")
        if resume_keywords:
            st.code(", ".join(sorted(resume_keywords)))
        else:
            st.info("No common tech skills found in the Resume.")

        st.markdown("---")
        st.subheader("💡 Semantic Match Score (AI-Powered)")
        semantic_score = calculate_semantic_similarity(job_description, resume_content)
        semantic_score_percent = round(semantic_score * 100, 2)

        st.write(f"The AI model calculated a **semantic similarity score of {semantic_score_percent}%**.")
        st.progress(min(semantic_score, 1.0))

        st.info(
            "This score reflects how semantically similar the overall content of the resume "
            "is to the job description, capturing nuances beyond just exact keyword matches."
        )

        st.markdown("---")
        st.subheader("🎯 Keyword Match Score (Traditional ATS-like)")
        keyword_match_percent = calculate_keyword_match_score(jd_keywords, resume_keywords)
        keyword_match_percent_rounded = round(keyword_match_percent, 2)

        st.write(f"Based on common keywords, the resume has a **{keyword_match_percent_rounded}% keyword match** with the job description.")
        st.progress(keyword_match_percent / 100.0)

        st.info(
            "This score indicates the percentage of job description keywords that are also present in the resume. "
            "It's a simpler, more direct match often used by traditional ATS systems."
        )

        st.markdown("---")
        st.subheader("Summary & Visualization")
        st.markdown(f"""
            - **Semantic Match:** The AI model suggests a **{semantic_score_percent}%** overall semantic alignment.
            - **Keyword Match:** A direct keyword comparison shows a **{keyword_match_percent_rounded}%** match.
        """)

        scores_data = {
            'Metric': ['Semantic Match', 'Keyword Match'],
            'Score (%)': [semantic_score_percent, keyword_match_percent_rounded]
        }
        st.bar_chart(scores_data, x='Metric', y='Score (%)', use_container_width=True)

        st.markdown("---")
        st.subheader("📝 How to Improve Your Resume for a Better Match")
        st.markdown("""
            Based on the analysis, here's what you can do to enhance your resume's match with the job description:
        """)

        jd_set = set(jd_keywords)
        resume_set = set(resume_keywords)
        missing_keywords = sorted(list(jd_set - resume_set))

        if missing_keywords:
            st.markdown("#### 1. Skill Gap Analysis: Address Missing Keywords")
            st.markdown(f"""
                The following keywords/skills from the Job Description were **not explicitly found** in your Resume:
                `{', '.join(missing_keywords)}`
                
                **Action:** Strategically integrate these terms into your resume.
                * **Experience Section:** Weave them into your bullet points describing past responsibilities and achievements.
                * **Skills Section:** Ensure these are listed if they are relevant to your capabilities.
                * **Project Descriptions:** If you have projects where you used these technologies/skills, highlight them.
                * **Avoid Keyword Stuffing:** Integrate them naturally, ensuring the text remains readable and coherent.
            """)
        else:
            st.markdown("#### 1. Skill Gap Analysis: Keyword Coverage")
            st.info("Great! Your resume seems to cover all the common technical keywords identified in the Job Description.")

        st.markdown("#### 2. Enhance Semantic Alignment (Beyond Keywords)")
        st.markdown(f"""
            Your **Semantic Match Score** is **{semantic_score_percent}%**. This score reflects how well the overall meaning and context of your resume align with the job description.
            
            **Action:**
            * **Tailor your narratives:** Rework your experience bullet points to directly address the responsibilities, challenges, and desired outcomes mentioned in the job description.
            * **Use Action Verbs:** Start bullet points with strong action verbs that demonstrate your impact (e.g., "Led," "Developed," "Optimized," "Managed").
            * **Quantify Achievements:** Whenever possible, use numbers and metrics to quantify your accomplishments (e.g., "Increased efficiency by 15%," "Managed a team of 5," "Reduced costs by $10,000").
            * **Mirror Language:** While avoiding plagiarism, try to use similar phrasing and terminology as the job description, especially for key responsibilities and soft skills.
        """)

        st.markdown("#### 3. General Resume Tailoring Tips")
        st.markdown("""
            * **Customize for Each Application:** Always tailor your resume specifically for each job you apply to. A generic resume rarely performs as well.
            * **Highlight Relevant Experience:** Prioritize experience and projects that are most relevant to the job description.
            * **Proofread Thoroughly:** Ensure there are no typos or grammatical errors.
            * **Read the Job Description Carefully:** Understand the core requirements and priorities of the role.
        """)

        st.markdown("---")
        st.success("Analysis complete! Use these insights to refine resumes or job descriptions.")

st.markdown("""
    ---
    *Disclaimer: This is a simplified ATS simulator for demonstration purposes.
    Real-world ATS systems are far more complex and involve advanced parsing,
    ranking algorithms, and often integrate with HR systems.*
""")
