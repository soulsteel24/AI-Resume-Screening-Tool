from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from app.core.config import settings
from app.services.ml_service import ml_service
from app.schemas.resume import ResumeAnalysisResponse

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

        jd_keywords_dict = ml_service.extract_keywords(job_description)
        resume_keywords_dict = ml_service.extract_keywords(resume_text)

        jd_keywords = list(jd_keywords_dict.keys())
        resume_keywords = list(resume_keywords_dict.keys())

        semantic_score = ml_service.calculate_semantic_similarity(job_description, resume_text)
        keyword_match_score = ml_service.calculate_keyword_match_score(jd_keywords, resume_keywords)

        jd_set = set(jd_keywords)
        resume_set = set(resume_keywords)
        
        missing_keywords_list = []
        missing_set = jd_set - resume_set
        for keyword in missing_set:
            importance = jd_keywords_dict.get(keyword, 1)
            missing_keywords_list.append({"keyword": keyword, "importance": importance})
        
        # Sort by importance (descending)
        missing_keywords_list.sort(key=lambda x: x["importance"], reverse=True)

        detected_keywords = sorted(list(resume_set))

        return ResumeAnalysisResponse(
            semantic_score=semantic_score,
            keyword_match_score=keyword_match_score,
            missing_keywords=missing_keywords_list,
            detected_keywords=detected_keywords,
            job_description_keywords=sorted(jd_keywords)
        )

    except Exception as e:
        # In a real app, log the error
        print(f"Error processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the resume: {str(e)}"
        )

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Resume Screening API"}
