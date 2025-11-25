import re
from typing import List, Set
from sentence_transformers import SentenceTransformer, util
import PyPDF2
from io import BytesIO

class MLService:
    def __init__(self):
        self.model = None
        self.common_tech_skills = [
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

    def load_model(self, model_name: str):
        """Loads the SentenceTransformer model."""
        self.model = SentenceTransformer(model_name)

    def preprocess_text(self, text: str) -> str:
        """Cleans and preprocesses the text."""
        if not isinstance(text, str):
            return ""
        text = text.lower()
        # Remove newlines and extra spaces
        text = text.replace("\n", " ").replace("\r", "")
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_keywords(self, text: str) -> dict[str, int]:
        """Extracts common tech skills from the text and their frequencies."""
        processed_text = self.preprocess_text(text)
        found_skills = {}

        sorted_skill_list = sorted(self.common_tech_skills, key=len, reverse=True)

        for skill in sorted_skill_list:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if len(skill.split()) > 1:
                 # For multi-word skills, simple count in processed text might be slightly inaccurate due to overlaps, 
                 # but acceptable for this use case. 
                 # Better to use regex for multi-word too to ensure boundaries if possible, 
                 # but 'processed_text' has no punctuation.
                 count = processed_text.count(skill)
                 if count > 0:
                     found_skills[skill] = count
            else:
                matches = re.findall(pattern, processed_text)
                if matches:
                    found_skills[skill] = len(matches)
        return found_skills

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculates semantic similarity between two texts."""
        if not text1 or not text2 or self.model is None:
            return 0.0

        embedding1 = self.model.encode(text1, convert_to_tensor=True)
        embedding2 = self.model.encode(text2, convert_to_tensor=True)

        cosine_scores = util.cos_sim(embedding1, embedding2)
        return cosine_scores.item()

    def calculate_keyword_match_score(self, jd_keywords: List[str], resume_keywords: List[str]) -> float:
        """Calculates the percentage of JD keywords present in the resume."""
        if not jd_keywords:
            return 0.0

        jd_set = set(jd_keywords)
        resume_set = set(resume_keywords)
        common_keywords = jd_set.intersection(resume_set)

        score = (len(common_keywords) / len(jd_set)) * 100
        return score

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extracts text from a PDF file content."""
        try:
            reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

ml_service = MLService()
