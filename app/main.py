from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from app.core.config import settings
from app.services.ml_service import ml_service
from app.schemas.resume import ResumeAnalysisResponse, ScoreBreakdown, ImprovementTip, MissingKeyword, GrammarIssue

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model on startup
    print("Loading model...")
    ml_service.load_model(settings.MODEL_NAME)
    print("Model loaded.")
    yield
    # Clean up resources if needed
    print("Shutting down...")

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post(f"{settings.API_V1_STR}/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are supported."
        )

    try:
        file_content = await file.read()
        resume_text = ml_service.extract_text_from_pdf(file_content)
        
        if not resume_text:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from the PDF."
            )

        # Extract keywords using standard method
        jd_keywords_dict = ml_service.extract_keywords(job_description)
        resume_keywords_dict = ml_service.extract_keywords(resume_text)

        jd_keywords = list(jd_keywords_dict.keys())
        resume_keywords = list(resume_keywords_dict.keys())

        # Calculate TF-IDF weighted keywords
        jd_tfidf, resume_tfidf = ml_service.calculate_tfidf_keywords(job_description, resume_text)

        # Calculate all scores
        semantic_score = ml_service.calculate_semantic_similarity(job_description, resume_text)
        keyword_match_score = ml_service.calculate_keyword_match_score(jd_keywords, resume_keywords)
        skills_coverage_score = ml_service.calculate_skills_coverage_score(jd_tfidf, resume_keywords)
        experience_relevance_score = ml_service.calculate_experience_relevance_score(job_description, resume_text)
        
        # Check grammar and spelling
        grammar_score, grammar_issues_raw = ml_service.check_grammar(resume_text)
        
        grammar_issues = [
            GrammarIssue(
                message=issue["message"],
                context=issue["context"],
                suggestions=issue["suggestions"]
            )
            for issue in grammar_issues_raw
        ]
        
        # Calculate overall ATS score (now includes grammar)
        overall_ats_score = ml_service.calculate_overall_ats_score(
            semantic_score,
            keyword_match_score,
            skills_coverage_score,
            experience_relevance_score
        )
        # Slightly adjust for grammar (10% weight)
        overall_ats_score = round(overall_ats_score * 0.9 + grammar_score * 0.1, 1)

        # Identify missing keywords with importance
        jd_set = set(jd_keywords)
        resume_set = set(resume_keywords)
        
        missing_keywords_list = []
        missing_set = jd_set - resume_set
        for keyword in missing_set:
            importance = jd_keywords_dict.get(keyword, 1)
            # Boost importance if keyword has high TF-IDF score
            if keyword in jd_tfidf:
                importance = max(importance, int(jd_tfidf[keyword] * 10) + 1)
            missing_keywords_list.append(MissingKeyword(keyword=keyword, importance=importance))
        
        # Sort by importance (descending)
        missing_keywords_list.sort(key=lambda x: x.importance, reverse=True)

        detected_keywords = sorted(list(resume_set))

        # Generate improvement tips
        missing_kw_names = [mk.keyword for mk in missing_keywords_list]
        improvement_tips_raw = ml_service.generate_improvement_tips(
            missing_kw_names,
            semantic_score,
            keyword_match_score,
            experience_relevance_score
        )
        
        # Add grammar tip if needed
        if grammar_score < 80:
            improvement_tips_raw.insert(0, {
                "category": "Grammar & Spelling",
                "tip": f"Found {len(grammar_issues)} grammar/spelling issues. Proofread your resume carefully.",
                "priority": 1 if grammar_score < 60 else 2
            })
        
        improvement_tips = [
            ImprovementTip(
                category=tip["category"],
                tip=tip["tip"],
                priority=tip["priority"]
            )
            for tip in improvement_tips_raw
        ]

        # Create score breakdown
        score_breakdown = ScoreBreakdown(
            keyword_match=round(keyword_match_score, 1),
            semantic_similarity=round(semantic_score * 100, 1),
            skills_coverage=round(skills_coverage_score, 1),
            experience_relevance=round(experience_relevance_score, 1),
            grammar_score=round(grammar_score, 1)
        )

        return ResumeAnalysisResponse(
            overall_ats_score=overall_ats_score,
            semantic_score=semantic_score,
            keyword_match_score=keyword_match_score,
            skills_coverage_score=skills_coverage_score,
            experience_relevance_score=experience_relevance_score,
            grammar_score=grammar_score,
            score_breakdown=score_breakdown,
            missing_keywords=missing_keywords_list,
            detected_keywords=detected_keywords,
            job_description_keywords=sorted(jd_keywords),
            improvement_tips=improvement_tips,
            grammar_issues=grammar_issues
        )

    except HTTPException:
        raise
    except Exception as e:
        # In a real app, log the error
        print(f"Error processing request: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the resume: {str(e)}"
        )

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Resume Screening API"}
