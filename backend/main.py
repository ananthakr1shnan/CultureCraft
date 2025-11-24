from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from services.pdf_service import extract_text_from_pdf
from services.ai_service import rewrite_text_with_culture, describe_image, transcribe_audio, generate_audio, generate_quiz, chat_with_persona
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CultureCraft API is running"}

@app.post("/rewrite")
async def rewrite_content(
    file: UploadFile = File(None),
    text_input: str = Form(None),
    culture: str = Form(...),
    page_number: int = Form(1)
):
    extracted_text = ""

    # 1. Determine Input Type
    if text_input:
        extracted_text = text_input
    elif file:
        content_type = file.content_type
        if "pdf" in content_type:
            extracted_text = await extract_text_from_pdf(file, page_number)
        elif "image" in content_type:
            content = await file.read()
            extracted_text = await describe_image(content)
        elif "audio" in content_type or "mp4" in content_type or "mpeg" in content_type:
            content = await file.read()
            extracted_text = await transcribe_audio(content)
        else:
             raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")
    else:
        raise HTTPException(status_code=400, detail="No file or text input provided.")

    if not extracted_text:
        raise HTTPException(status_code=400, detail="Could not extract text from input.")

    # 2. Call AI to rewrite
    ai_result = await rewrite_text_with_culture(extracted_text, culture)
    
    return {
        "original_text": extracted_text,
        "rewritten_text": ai_result.get("rewritten_text", ""),
        "image_prompt": ai_result.get("image_prompt", "")
    }

class TTSRequest(BaseModel):
    text: str
    voice: str

@app.post("/tts")
async def tts_endpoint(request: TTSRequest):
    audio_bytes = await generate_audio(request.text, request.voice)
    return Response(content=audio_bytes, media_type="audio/mpeg")

class QuizRequest(BaseModel):
    text: str

@app.post("/quiz")
async def quiz_endpoint(request: QuizRequest):
    return await generate_quiz(request.text)

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]
    context: str
    culture: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    response = await chat_with_persona(request.message, request.history, request.context, request.culture)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
