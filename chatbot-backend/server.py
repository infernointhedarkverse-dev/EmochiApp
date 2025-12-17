from fastapi import FastAPI, HTTPException, UploadFile, File  
from fastapi.middleware.cors import CORSMiddleware  
from pydantic import BaseModel  
from typing import List, Optional, Dict, Any  
from dotenv import load_dotenv  
import os  
import logging  
import shutil  
  
load_dotenv()  
  
from rp_engine import generate_reply, set_model, set_settings, set_wallpaper, get_state  
from storage import get_chat_dir  
  
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
logger = logging.getLogger(__name__)  
  
app = FastAPI(title="Emochi Chatbot Backend", description="Multi-provider LLM backend with personality models and emotion tracking", version="1.0.0")  
  
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])  
  
class MessageRequest(BaseModel):  
    text: str  
    provider: Optional[str] = None  
    model_hint: Optional[str] = None  
  
class MessageResponse(BaseModel):  
    chat_id: str  
    model: str  
    reply: str  
    emotion_hint: Dict[str, Any]  
  
class ModelRequest(BaseModel):  
    model: str  
  
class SettingsRequest(BaseModel):  
    intro: Optional[str] = None  
    personality: Optional[str] = None  
    welcome: Optional[str] = None  
    tags: Optional[List[str]] = None  
    gender: Optional[str] = None  
  
@app.get("/")  
async def root():  
    return {"status": "ok", "app": "Emochi Chatbot Backend", "version": "1.0.0"}  
  
@app.get("/health")  
async def health_check():  
    openai_key_status = "Loaded" if os.getenv("OPENAI_API_KEY") else "MISSING"  
    anthropic_key_status = "Loaded" if os.getenv("ANTHROPIC_API_KEY") else "MISSING"  
    google_key_status = "Loaded" if os.getenv("GOOGLE_API_KEY") else "MISSING"  
    return {"status": "ok", "app": "Emochi Chatbot Backend", "config_check": {"openai_key": openai_key_status, "anthropic_key": anthropic_key_status, "google_key": google_key_status, "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434")}}  
  
@app.post("/chat/{chat_id}/message", response_model=MessageResponse)  
async def send_message(chat_id: str, request: MessageRequest):  
    try:  
        result = generate_reply(chat_id=chat_id, user_text=request.text, provider_override=request.provider, model_hint=request.model_hint)  
        return MessageResponse(**result)  
    except Exception as e:  
        logger.exception(f"Error generating reply for chat {chat_id}")  
        raise HTTPException(status_code=500, detail=str(e))  
  
@app.post("/chat/{chat_id}/model")  
async def update_model(chat_id: str, request: ModelRequest):  
    try:  
        state = set_model(chat_id, request.model)  
        return {"ok": True, "state": state}  
    except ValueError as e:  
        raise HTTPException(status_code=400, detail=str(e))  
    except Exception as e:  
        logger.exception(f"Error updating model for chat {chat_id}")  
        raise HTTPException(status_code=500, detail=str(e))  
  
@app.post("/chat/{chat_id}/settings")  
async def update_settings(chat_id: str, request: SettingsRequest):  
    try:  
        state = set_settings(chat_id=chat_id, intro=request.intro, personality=request.personality, welcome=request.welcome, tags=request.tags, gender=request.gender)  
        return {"ok": True, "state": state}  
    except Exception as e:  
        logger.exception(f"Error updating settings for chat {chat_id}")  
        raise HTTPException(status_code=500, detail=str(e))  
  
@app.get("/chat/{chat_id}/state")  
async def get_chat_state(chat_id: str):  
    try:  
        state = get_state(chat_id)  
        return state  
    except Exception as e:  
        logger.exception(f"Error getting state for chat {chat_id}")  
        raise HTTPException(status_code=500, detail=str(e))  
  
@app.post("/chat/{chat_id}/wallpaper")  
async def upload_wallpaper(chat_id: str, file: UploadFile = File(...)):  
    try:  
        chat_dir = get_chat_dir(chat_id)  
        dest_path = os.path.join(chat_dir, file.filename)  
        with open(dest_path, "wb") as buffer:  
            shutil.copyfileobj(file.file, buffer)  
        meta = {"filename": file.filename, "path": dest_path, "content_type": file.content_type}  
        state = set_wallpaper(chat_id, meta)  
        return {"ok": True, "meta": meta}  
    except Exception as e:  
        logger.exception(f"Error uploading wallpaper for chat {chat_id}")  
        raise HTTPException(status_code=500, detail=str(e))  
  
@app.get("/models")  
async def list_models():  
    from model_personalities import model_personalities  
    return {"models": list(model_personalities.keys()), "descriptions": model_personalities}  
  
@app.get("/tags")  
async def list_tags():  
    return {"tags": ["Flirty", "Romantic", "Dominant", "Submissive", "Seductive", "Taboo", "Dark Romance", "Tsundere", "Yandere", "Bratty", "Demon", "Cold"]}  
  
if __name__ == "__main__":  
    import uvicorn  
    port = int(os.getenv("PORT", 8001))  
    host = os.getenv("HOST", "0.0.0.0")  
    logger.info(f"Starting Emochi Chatbot Backend on {host}:{port}")  
    uvicorn.run(app, host=host, port=port)