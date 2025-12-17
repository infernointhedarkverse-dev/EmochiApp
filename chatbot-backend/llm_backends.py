import os  
import json  
import pathlib  
import requests  
import logging  
from typing import List, Dict, Any, Optional  
  
logger = logging.getLogger(__name__)  
  
try:  
    import openai  
except Exception:  
    openai = None  
  
try:  
    from emergentintegrations.llm.chat import LlmChat  
except Exception:  
    LlmChat = None  
  
OPENAI_KEY = os.getenv("OPENAI_API_KEY")  
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")  
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")  
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")  
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")  
USE_EMERGENT = os.getenv("USE_EMERGENT", "false").lower() in ("1", "true", "yes")  
EMERGENT_DEFAULT_MODEL = os.getenv("EMERGENT_MODEL", "default")  
  
DEFAULT_MODEL_PROVIDER_MAP = {"Vanilla": "ollama", "Vanilla Short": "ollama", "Matcha": "ollama", "Strawberry": "openai", "Chocolate": "openai", "Peach": "ollama", "Blueberry": "openai", "Mint": "openai", "Blackberry": "openai", "Rainbow": "openai", "Unicorn": "openai", "Sage": "openai"}  
  
def load_model_provider_map() -> Dict[str, str]:  
    cfg_path = pathlib.Path(__file__).parent / "model_provider_map.json"  
    if cfg_path.exists():  
        try:  
            with cfg_path.open("r", encoding="utf-8") as f:  
                return json.load(f)  
        except Exception as e:  
            logger.warning("Failed to load model_provider_map.json: %s", e)  
    return DEFAULT_MODEL_PROVIDER_MAP  
  
MODEL_PROVIDER_MAP = load_model_provider_map()  
  
def call_openai(messages: List[Dict[str, str]], model: str = "gpt-4o", max_tokens: int = 512, temperature: float = 0.8) -> str:  
    if openai is None:  
        raise RuntimeError("OpenAI SDK not installed. Run: pip install openai")  
    if OPENAI_KEY is None:  
        raise RuntimeError("OPENAI_API_KEY not configured in environment.")  
    client = openai.OpenAI(api_key=OPENAI_KEY, base_url=OPENAI_BASE_URL)  
    try:  
        response = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens, temperature=temperature)  
        return response.choices[0].message.content  
    except Exception as e:  
        logger.error(f"OpenAI API error: {e}")  
        raise RuntimeError(f"OpenAI API error: {e}")  
  
def call_ollama(model: str, prompt: str, max_tokens: int = 512, temperature: float = 0.8) -> str:  
    url = f"{OLLAMA_URL}/api/generate"  
    payload = {"model": model, "prompt": prompt, "options": {"num_predict": max_tokens, "temperature": temperature}, "stream": False}  
    try:  
        resp = requests.post(url, json=payload, timeout=60)  
        resp.raise_for_status()  
        data = resp.json()  
        if isinstance(data, dict) and "response" in data:  
            return data["response"]  
        if isinstance(data, dict) and "text" in data:  
            return data["text"]  
        if isinstance(data, list) and len(data) > 0:  
            return data[0].get("content", "")  
        return json.dumps(data)  
    except Exception as e:  
        logger.error(f"Ollama API error: {e}")  
        raise RuntimeError(f"Ollama API error: {e}")  
  
def call_emergent(conversation: List[Dict[str, str]], model_hint: Optional[str] = None, max_tokens: int = 512) -> str:  
    if LlmChat is None:  
        raise RuntimeError("Emergent LlmChat wrapper is not available.")  
    llm = LlmChat(model=model_hint or EMERGENT_DEFAULT_MODEL)  
    try:  
        return llm.generate(conversation, max_tokens=max_tokens)  
    except Exception:  
        return llm.chat(conversation)  
  
def call_claude(messages: List[Dict[str, str]], model_hint: Optional[str] = None, max_tokens: int = 512) -> str:  
    if ANTHROPIC_KEY:  
        logger.warning("Claude integration not fully implemented, using OpenAI fallback")  
    if OPENAI_KEY and openai is not None:  
        return call_openai(messages, model=model_hint or "gpt-4o", max_tokens=max_tokens)  
    raise RuntimeError("Claude selected but no Claude integration configured.")  
  
def call_gemini(messages: List[Dict[str, str]], model_hint: Optional[str] = None, max_tokens: int = 512) -> str:  
    if GOOGLE_KEY:  
        logger.warning("Gemini integration not fully implemented, using OpenAI fallback")  
    if OPENAI_KEY and openai is not None:  
        return call_openai(messages, model=model_hint or "gpt-4o", max_tokens=max_tokens)  
    raise RuntimeError("Gemini selected but no Gemini integration configured.")  
  
def choose_and_call(provider: Optional[str], system_prompt: str, messages: List[Dict[str, str]], model_name_hint: Optional[str] = None, model_name: Optional[str] = None, max_tokens: int = 512) -> str:  
    msgs = [{"role": "system", "content": system_prompt}] + messages  
    chosen = (provider or "auto").lower()  
    if chosen in ("auto", ""):  
        chosen = MODEL_PROVIDER_MAP.get(model_name, None) or ("openai" if OPENAI_KEY else ("ollama" if OLLAMA_URL else ("emergent" if USE_EMERGENT else "ollama")))  
    chosen = chosen.lower()  
    logger.info("choose_and_call: model_name=%s -> provider=%s (hint=%s)", model_name, chosen, model_name_hint)  
    if chosen == "openai":  
        return call_openai(msgs, model=model_name_hint or "gpt-4o", max_tokens=max_tokens)  
    if chosen == "ollama":  
        joined = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in msgs])  
        return call_ollama(model_name_hint or "llama2", prompt=joined, max_tokens=max_tokens)  
    if chosen == "emergent":  
        return call_emergent(msgs, model_hint=model_name_hint, max_tokens=max_tokens)  
    if chosen == "claude":  
        return call_claude(msgs, model_hint=model_name_hint, max_tokens=max_tokens)  
    if chosen == "gemini":  
        return call_gemini(msgs, model_hint=model_name_hint, max_tokens=max_tokens)  
    if OPENAI_KEY:  
        return call_openai(msgs, model=model_name_hint or "gpt-4o", max_tokens=max_tokens)  
    return call_ollama(model_name_hint or "llama2", prompt="\n".join([m["content"] for m in msgs]), max_tokens=max_tokens)