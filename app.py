from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, Field, HttpUrl
from typing import Optional, List
import uvicorn
from datetime import datetime
import os
import aiofiles
from pathlib import Path
from process import main

# Initialize FastAPI app
app = FastAPI(
    title="Resume Maker API",
    description="A FastAPI application for resume generation with cross validation",
    version="1.0.0"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": "Welcome to MPower AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "improvement_profile": "/improvement-profile"
        }
    }
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Resume Maker API"
    }

@app.post("/improvement-profile")
async def improve_resume(
    resume_file: UploadFile = File(..., description="Resume file (PDF, DOC, DOCX)")
):
    """Improve resume using provided links and uploaded resume file"""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        file_extension = Path(resume_file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Validate URLs if provided
        # profile_data = {}
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{resume_file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await resume_file.read()
            await f.write(content)

        string_data, processed_results, total_tokens = await main(file_path)

        

        # Clean up: delete the uploaded file after processing
        try:
            if file_path.exists():
                file_path.unlink()
                print(f"Successfully deleted uploaded file: {file_path}")
        except Exception as delete_error:
            print(f"Warning: Could not delete file {file_path}: {delete_error}")
            # Continue execution even if file deletion fails

        return {
            "status_code": 200,
            "status": "success",
            "message": "Comprehensive resume analysis completed successfully",
            "processed_results": processed_results,
            "string_data": string_data,
            "total_tokens": total_tokens
            

        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, status="error", message=f"Error processing resume: {str(e)}")
    
        


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )