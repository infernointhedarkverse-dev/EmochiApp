import re  
import random  
from typing import Dict, Any, List, Optional  
  
DEFAULT_INTENSITY_DECAY = 0.85  
MIN_INTENSITY = 0  
MAX_INTENSITY = 100  
  
TRIGGERS = {  
    "affection": ["love", "like you", "i care", "miss you", "cherish", "adore"],  
    "anger": ["shut up", "stupid", "idiot", "what the hell", "hate", "screw you"],  
    "fear": ["please stop", "don't", "no", "help", "scared"],  
    "flirty": ["come here", "kiss", "touch", "want", "seduce", "hot"],  
    "tease": ["make me", "try me", "dare you", "you wish"],  
    "curiosity": ["why", "how", "what do you mean", "explain"],  
    "jealousy": ["who is that", "with who", "are you with"],  
    "sad": ["sad", "cry", "tears", "sorry", "alone"]  
}  
  
REACTION_SNIPPETS = {  
    "soft": ["*Her voice softens, a hush beneath the words.*", "*A small smile tugs at the corner of her mouth.*"],  
    "angry": ["*Her jaw tightens; a flash of hurt passes across her face.*", "*She snaps—but the brightness in her eyes betrays something fragile.*"],  
    "nervous": ["*Her fingers fidget at her sleeve; she looks away for a beat.*", "*A tiny tremor in her breath betrays the calm in her voice.*"],  
    "conflicted": ["*Her words are sharp, but her eyes linger too long.*", "*She says no—and yet her posture betrays doubt.*"],  
    "aroused": ["*Her breath stutters—quick and shallow.*", "*Heat pools low, barely concealed.*"]  
}  
  
def clamp(x: float, a: float = MIN_INTENSITY, b: float = MAX_INTENSITY) -> int:  
    return int(max(a, min(b, x)))  
  
def score_triggers(text: str) -> Dict[str, int]:  
    t = (text or "").lower()  
    scores = {k: 0 for k in TRIGGERS}  
    for k, words in TRIGGERS.items():  
        for w in words:  
            if w in t:  
                scores[k] += max(1, len(w) // 3)  
    return scores  
  
def dominant_from_scores(scores: Dict[str, int]) -> Optional[str]:  
    if not scores:  
        return None  
    k = max(scores.keys(), key=lambda x: scores[x])  
    return k if scores[k] > 0 else None  
  
def build_emotion_hint(prev_hint: Optional[Dict[str, Any]], user_text: str, bot_text: str, tags: List[str] = None, emotion_state: Dict[str, Any] = None) -> Dict[str, Any]:  
    tags = tags or []  
    emotion_state = emotion_state or {}  
    user_scores = score_triggers(user_text or "")  
    bot_scores = score_triggers(bot_text or "")  
    combined = {k: user_scores.get(k, 0) + bot_scores.get(k, 0) for k in TRIGGERS.keys()}  
    base = sum(combined.values()) * 6  
    prev_int = (prev_hint.get("intensity", 0) if prev_hint else 0)  
    intensity = clamp(base + prev_int * DEFAULT_INTENSITY_DECAY)  
    if "Taboo" in tags or "Dark Romance" in tags:  
        intensity = clamp(intensity + 8)  
    if "Flirty" in tags or "Seductive" in tags:  
        intensity = clamp(intensity + 6)  
    if "Cold" in tags:  
        intensity = clamp(intensity - 6)  
    dom = dominant_from_scores(combined)  
    mapping = {"affection": "soft", "flirty": "aroused", "tease": "conflicted", "anger": "angry", "fear": "nervous", "curiosity": "curious", "jealousy": "jealous", "sad": "sad"}  
    primary = mapping.get(dom, None)  
    if "Yandere" in tags:  
        primary = "jealous" if not primary else primary  
        intensity = clamp(intensity + 10)  
    if "Tsundere" in tags and primary is None:  
        primary = "conflicted"  
    meta = {  
        "attraction": clamp((combined.get("flirty", 0) + combined.get("affection", 0)) * 8 + emotion_state.get("attraction", 0) // 2),  
        "trust": clamp(emotion_state.get("trust", 20)),  
        "anger": clamp(combined.get("anger", 0) * 10 + emotion_state.get("anger", 0))  
    }  
    snippet_pool = REACTION_SNIPPETS.get(primary, None) or []  
    snippet = random.choice(snippet_pool) if snippet_pool else ""  
    contradict = False  
    if bot_text:  
        if re.search(r"\b(no|don't|can't|not|never)\b", bot_text.lower()) and meta["attraction"] > 20:  
            contradict = True  
        if re.search(r"\b(leave|alone|stop)\b", bot_text.lower()) and meta["trust"] > 40:  
            contradict = True  
    return {"primary": primary or "neutral", "secondary": [], "intensity": intensity, "meta": meta, "snippet": snippet, "contradiction": contradict}