import os  
import json  
import uuid  
from datetime import datetime, timezone  
from typing import Dict, Any, Optional  
  
BASE_DIR = os.path.join(os.path.dirname(__file__), "rp_data")  
os.makedirs(BASE_DIR, exist_ok=True)  
  
def _chat_dir(chat_id: str) -> str:  
    d = os.path.join(BASE_DIR, chat_id)  
    os.makedirs(d, exist_ok=True)  
    return d  
  
def _state_file(chat_id: str) -> str:  
    return os.path.join(_chat_dir(chat_id), "state.json")  
  
def load_state(chat_id: str) -> Dict[str, Any]:  
    p = _state_file(chat_id)  
    if not os.path.exists(p):  
        st = {"chat_id": chat_id, "model": "Vanilla", "intro": "", "personality": "", "welcome": "", "tags": [], "gender": "neutral", "wallpaper": None, "messages": [], "meta": {}}  
        save_state(chat_id, st)  
        return st  
    with open(p, "r", encoding="utf-8") as f:  
        return json.load(f)  
  
def save_state(chat_id: str, state: Dict[str, Any]) -> None:  
    with open(_state_file(chat_id), "w", encoding="utf-8") as f:  
        json.dump(state, f, ensure_ascii=False, indent=2)  
  
def append_message(chat_id: str, role: str, content: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:  
    st = load_state(chat_id)  
    m = {"id": str(uuid.uuid4()), "role": role, "content": content, "time": datetime.now(timezone.utc).isoformat(), "meta": meta or {}}  
    st["messages"].append(m)  
    st["messages"] = st["messages"][-400:]  
    save_state(chat_id, st)  
    return m  
  
def get_chat_dir(chat_id: str) -> str:  
    return _chat_dir(chat_id)