import re
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util
import PyPDF2
from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Try to import pdfplumber for better PDF parsing
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

# Try to import spacy for better NLP
try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

# Try to import language_tool for grammar checking
try:
    import language_tool_python
    HAS_LANGUAGE_TOOL = True
except ImportError:
    HAS_LANGUAGE_TOOL = False


class MLService:
    def __init__(self):
        self.model = None
        self.nlp = None
        
        # Comprehensive skill list with categories
        self.common_tech_skills = [
            # Programming Languages
            "python", "java", "c++", "javascript", "typescript", "c#", "go", "rust", 
            "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "perl", "bash",
            # Web Technologies
            "react", "angular", "vue.js", "vue", "node.js", "nodejs", "express", "next.js", 
            "html", "css", "sass", "less", "tailwind", "bootstrap", "jquery", "webpack",
            # Databases
            "sql", "nosql", "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
            "oracle", "sqlite", "cassandra", "dynamodb", "firebase",
            # Cloud & DevOps
            "aws", "azure", "google cloud", "gcp", "docker", "kubernetes", "terraform",
            "jenkins", "ci/cd", "github actions", "gitlab", "ansible", "puppet", "chef",
            # Data Science & ML
            "machine learning", "deep learning", "natural language processing", "nlp",
            "data science", "pytorch", "tensorflow", "keras", "scikit-learn", "pandas",
            "numpy", "spark", "hadoop", "kafka", "airflow", "dbt",
            # Methodologies & Practices
            "agile", "scrum", "kanban", "devops", "devsecops", "tdd", "bdd", "ci/cd",
            "microservices", "rest api", "graphql", "grpc",
            # Tools & Platforms
            "git", "jira", "confluence", "slack", "figma", "tableau", "power bi",
            "excel", "linux", "unix", "windows",
            # Soft Skills
            "problem solving", "communication", "teamwork", "leadership", "project management",
            # Domains
            "cybersecurity", "blockchain", "ui/ux", "mobile development", "android", "ios",
            "web development", "frontend", "backend", "fullstack", "data analysis",
            "data visualization", "cloud computing", "cloud security", "networking",
            "system design", "api design", "database management", "distributed systems",
            "computer vision", "reinforcement learning", "big data", "etl", "data warehousing",
            # Common JD terms
            "software development", "software engineer", "sde", "swe", "coding", "programming",
            "algorithms", "data structures", "dsa", "object oriented", "oop", "clean code",
            "scalable", "design patterns", "debugging", "testing", "unit testing",
            "integration testing", "performance", "optimization", "mentoring", "collaboration",
            "computer science", "bachelor", "master", "degree"
        ]
        
        # Synonym mappings for better matching
        self.skill_synonyms = {
            "javascript": ["js", "es6", "ecmascript", "es2015", "es2020"],
            "typescript": ["ts"],
            "python": ["py", "python3", "python2"],
            "machine learning": ["ml", "ai", "artificial intelligence"],
            "deep learning": ["dl", "neural networks", "neural network"],
            "natural language processing": ["nlp"],
            "postgresql": ["postgres", "psql", "pg"],
            "mongodb": ["mongo"],
            "kubernetes": ["k8s"],
            "amazon web services": ["aws"],
            "google cloud platform": ["gcp", "google cloud"],
            "microsoft azure": ["azure"],
            "continuous integration": ["ci", "ci/cd"],
            "continuous delivery": ["cd", "ci/cd"],
            "node.js": ["nodejs", "node"],
            "react": ["reactjs", "react.js"],
            "angular": ["angularjs", "angular.js"],
            "vue.js": ["vue", "vuejs"],
            "c++": ["cpp", "cplusplus"],
            "c#": ["csharp", "c sharp"],
            "rest api": ["restful", "rest", "restful api"],
            "user interface": ["ui"],
            "user experience": ["ux"],
            "ui/ux": ["ui", "ux", "user interface", "user experience"],
            "software development engineer": ["sde", "software developer", "software engineer"],
            "software engineer": ["swe", "software dev", "engineer"],
            "data structures": ["dsa", "ds"],
            "algorithms": ["algo", "algos"],
            "object oriented programming": ["oop", "object oriented"],
        }
        
        # Experience keywords for relevance scoring
        self.experience_keywords = [
            "senior", "junior", "lead", "principal", "staff", "manager", "director",
            "head", "chief", "architect", "engineer", "developer", "analyst", "specialist",
            "consultant", "intern", "associate", "entry level", "mid level", "experienced"
        ]
        
        # Action verbs for resume quality
        self.action_verbs = [
            "developed", "implemented", "designed", "created", "built", "led", "managed",
            "optimized", "improved", "increased", "decreased", "reduced", "launched",
            "deployed", "architected", "spearheaded", "collaborated", "coordinated",
            "streamlined", "automated", "resolved", "analyzed", "delivered", "achieved"
        ]
        
        # Grammar checker (lazy loaded)
        self.grammar_tool = None

    def load_model(self, model_name: str):
        """Loads the SentenceTransformer model and spaCy if available."""
        self.model = SentenceTransformer(model_name)
        
        if HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Model not installed, try to download
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
                self.nlp = spacy.load("en_core_web_sm")

    def preprocess_text(self, text: str) -> str:
        """Cleans and preprocesses the text while preserving important tokens."""
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = text.replace("\n", " ").replace("\r", "")
        # Preserve common programming symbols
        text = text.replace("c++", "cplusplus").replace("c#", "csharp")
        text = re.sub(r'[^a-z0-9\s\.\+\#]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        # Restore programming language names
        text = text.replace("cplusplus", "c++").replace("csharp", "c#")
        return text

    def lemmatize_text(self, text: str) -> str:
        """Lemmatize text using spaCy if available."""
        if not HAS_SPACY or self.nlp is None:
            return text
        
        doc = self.nlp(text)
        lemmatized = " ".join([token.lemma_ for token in doc if not token.is_stop])
        return lemmatized

    def normalize_skill(self, skill: str) -> str:
        """Normalize a skill to its canonical form using synonyms."""
        skill_lower = skill.lower().strip()
        
        # Check if skill is a synonym
        for canonical, synonyms in self.skill_synonyms.items():
            if skill_lower in synonyms:
                return canonical
            if skill_lower == canonical:
                return canonical
        
        return skill_lower

    def extract_keywords(self, text: str) -> Dict[str, int]:
        """Extracts common tech skills from the text and their frequencies."""
        processed_text = self.preprocess_text(text)
        found_skills = {}

        # Sort by length (longest first) to match multi-word skills first
        sorted_skill_list = sorted(self.common_tech_skills, key=len, reverse=True)
        
        # Also check for synonyms
        all_patterns = []
        for skill in sorted_skill_list:
            all_patterns.append((skill, skill))
            if skill in self.skill_synonyms:
                for synonym in self.skill_synonyms[skill]:
                    all_patterns.append((synonym, skill))

        for pattern, canonical_skill in all_patterns:
            if len(pattern.split()) > 1:
                count = processed_text.count(pattern)
                if count > 0:
                    normalized = self.normalize_skill(canonical_skill)
                    found_skills[normalized] = found_skills.get(normalized, 0) + count
            else:
                regex_pattern = r'\b' + re.escape(pattern) + r'\b'
                matches = re.findall(regex_pattern, processed_text)
                if matches:
                    normalized = self.normalize_skill(canonical_skill)
                    found_skills[normalized] = found_skills.get(normalized, 0) + len(matches)
        
        return found_skills

    def calculate_tfidf_keywords(self, jd_text: str, resume_text: str) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Calculate TF-IDF weighted keywords for both texts."""
        processed_jd = self.preprocess_text(jd_text)
        processed_resume = self.preprocess_text(resume_text)
        
        # Create vocabulary from our skill list
        vectorizer = TfidfVectorizer(vocabulary=[s.lower() for s in self.common_tech_skills])
        
        try:
            tfidf_matrix = vectorizer.fit_transform([processed_jd, processed_resume])
            feature_names = vectorizer.get_feature_names_out()
            
            jd_scores = dict(zip(feature_names, tfidf_matrix.toarray()[0]))
            resume_scores = dict(zip(feature_names, tfidf_matrix.toarray()[1]))
            
            # Filter out zero scores
            jd_scores = {k: v for k, v in jd_scores.items() if v > 0}
            resume_scores = {k: v for k, v in resume_scores.items() if v > 0}
            
            return jd_scores, resume_scores
        except Exception:
            return {}, {}

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculates semantic similarity with chunking for longer texts."""
        if not text1 or not text2 or self.model is None:
            return 0.0

        # Chunk long texts for better embedding quality
        max_chunk_size = 512
        
        def chunk_text(text: str, size: int) -> List[str]:
            words = text.split()
            chunks = []
            for i in range(0, len(words), size):
                chunk = " ".join(words[i:i+size])
                if chunk.strip():
                    chunks.append(chunk)
            return chunks if chunks else [text[:size]]
        
        # Get chunks
        chunks1 = chunk_text(text1, max_chunk_size)
        chunks2 = chunk_text(text2, max_chunk_size)
        
        # Encode chunks
        embeddings1 = self.model.encode(chunks1, convert_to_tensor=True)
        embeddings2 = self.model.encode(chunks2, convert_to_tensor=True)
        
        # Average embeddings if multiple chunks
        if len(chunks1) > 1:
            embedding1 = embeddings1.mean(dim=0)
        else:
            embedding1 = embeddings1[0] if len(embeddings1.shape) > 1 else embeddings1
            
        if len(chunks2) > 1:
            embedding2 = embeddings2.mean(dim=0)
        else:
            embedding2 = embeddings2[0] if len(embeddings2.shape) > 1 else embeddings2

        cosine_scores = util.cos_sim(embedding1, embedding2)
        return float(cosine_scores.item())

    def calculate_keyword_match_score(self, jd_keywords: List[str], resume_keywords: List[str]) -> float:
        """Calculates the percentage of JD keywords present in the resume."""
        if not jd_keywords:
            return 0.0

        jd_set = set([self.normalize_skill(k) for k in jd_keywords])
        resume_set = set([self.normalize_skill(k) for k in resume_keywords])
        common_keywords = jd_set.intersection(resume_set)

        score = (len(common_keywords) / len(jd_set)) * 100
        return score

    def calculate_skills_coverage_score(self, jd_keywords_weighted: Dict[str, float], 
                                        resume_keywords: List[str]) -> float:
        """Calculate skills coverage with TF-IDF weighting."""
        if not jd_keywords_weighted:
            return 0.0
        
        resume_set = set([self.normalize_skill(k) for k in resume_keywords])
        
        total_weight = sum(jd_keywords_weighted.values())
        matched_weight = sum(
            weight for skill, weight in jd_keywords_weighted.items() 
            if self.normalize_skill(skill) in resume_set
        )
        
        if total_weight == 0:
            return 0.0
        
        return (matched_weight / total_weight) * 100

    def calculate_experience_relevance_score(self, jd_text: str, resume_text: str) -> float:
        """Calculate experience relevance based on job titles and levels."""
        jd_processed = self.preprocess_text(jd_text)
        resume_processed = self.preprocess_text(resume_text)
        
        # Find experience keywords in JD
        jd_exp_keywords = []
        for keyword in self.experience_keywords:
            if keyword in jd_processed:
                jd_exp_keywords.append(keyword)
        
        if not jd_exp_keywords:
            # If no specific experience level mentioned, give neutral score
            return 70.0
        
        # Check how many are in resume
        matches = 0
        for keyword in jd_exp_keywords:
            if keyword in resume_processed:
                matches += 1
        
        # Also check for action verbs in resume (quality indicator)
        action_verb_count = sum(1 for verb in self.action_verbs if verb in resume_processed)
        action_verb_bonus = min(action_verb_count * 2, 20)  # Max 20 points bonus
        
        base_score = (matches / len(jd_exp_keywords)) * 80 if jd_exp_keywords else 60
        
        return min(base_score + action_verb_bonus, 100.0)

    def calculate_overall_ats_score(self, semantic: float, keyword: float, 
                                     skills: float, experience: float) -> float:
        """Calculate weighted overall ATS score."""
        weights = {
            'semantic': 0.25,
            'keyword': 0.25,
            'skills': 0.30,
            'experience': 0.20
        }
        
        overall = (
            semantic * 100 * weights['semantic'] +
            keyword * weights['keyword'] +
            skills * weights['skills'] +
            experience * weights['experience']
        )
        
        return min(round(overall, 1), 100.0)

    def generate_improvement_tips(self, missing_keywords: List[str], 
                                   semantic_score: float,
                                   keyword_score: float,
                                   experience_score: float) -> List[Dict]:
        """Generate actionable improvement tips based on analysis."""
        tips = []
        
        # Tips for missing keywords
        if missing_keywords:
            high_priority = missing_keywords[:5]
            tips.append({
                "category": "Missing Skills",
                "tip": f"Add these important skills to your resume: {', '.join(high_priority)}",
                "priority": 1
            })
        
        # Tips for semantic alignment
        if semantic_score < 0.6:
            tips.append({
                "category": "Content Alignment",
                "tip": "Rewrite your experience bullets to mirror the language and responsibilities in the job description",
                "priority": 1
            })
        elif semantic_score < 0.8:
            tips.append({
                "category": "Content Alignment",
                "tip": "Use more action verbs and quantify your achievements to better match the job requirements",
                "priority": 2
            })
        
        # Tips for keyword matching
        if keyword_score < 50:
            tips.append({
                "category": "Keyword Optimization",
                "tip": "Your resume is missing many key terms. Review the job description and incorporate relevant keywords naturally",
                "priority": 1
            })
        elif keyword_score < 75:
            tips.append({
                "category": "Keyword Optimization",
                "tip": "Add more technical skills from the job description to your Skills section",
                "priority": 2
            })
        
        # Tips for experience relevance
        if experience_score < 60:
            tips.append({
                "category": "Experience Match",
                "tip": "Highlight experience that directly relates to the job level and responsibilities mentioned",
                "priority": 2
            })
        
        # General tips
        tips.append({
            "category": "General",
            "tip": "Ensure your resume is ATS-friendly: use standard section headers, avoid tables/graphics, and save as PDF",
            "priority": 3
        })
        
        # Sort by priority
        tips.sort(key=lambda x: x["priority"])
        
        return tips

    def check_grammar(self, text: str) -> Tuple[float, List[Dict]]:
        """Check grammar and spelling in text. Returns score and list of issues."""
        if not HAS_LANGUAGE_TOOL or not text:
            return 100.0, []
        
        try:
            # Lazy load the grammar tool (takes time to initialize)
            if self.grammar_tool is None:
                self.grammar_tool = language_tool_python.LanguageTool('en-US')
            
            # Check for issues
            matches = self.grammar_tool.check(text)
            
            # Filter out minor issues and limit to most important ones
            significant_issues = []
            for match in matches[:15]:  # Limit to 15 issues
                if match.ruleId not in ['WHITESPACE_RULE', 'COMMA_PARENTHESIS_WHITESPACE']:
                    significant_issues.append({
                        "message": match.message,
                        "context": match.context[:100] if match.context else "",
                        "suggestions": match.replacements[:3] if match.replacements else []
                    })
            
            # Calculate score based on issues
            # Fewer issues = higher score
            word_count = len(text.split())
            if word_count == 0:
                return 100.0, significant_issues
            
            # Calculate error rate (errors per 100 words)
            error_rate = (len(matches) / word_count) * 100
            
            # Score: 100 - (error_rate * 10), clamped between 0 and 100
            grammar_score = max(0, min(100, 100 - (error_rate * 10)))
            
            return round(grammar_score, 1), significant_issues
            
        except Exception as e:
            print(f"Grammar check failed: {e}")
            return 100.0, []

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extracts text from a PDF file using multiple methods."""
        text = ""
        
        # Try pdfplumber first (better for complex layouts)
        if HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(BytesIO(file_content)) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                if text.strip():
                    return text.strip()
            except Exception as e:
                print(f"pdfplumber failed: {e}")
        
        # Fallback to PyPDF2
        try:
            reader = PyPDF2.PdfReader(BytesIO(file_content))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
            return ""


ml_service = MLService()
