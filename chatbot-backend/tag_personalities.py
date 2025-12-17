from typing import List

def build_tag_behavior(tags: List[str]) -> str:
    behavior_lines = []
    if not tags:
        return ""
    if "Flirty" in tags:
        behavior_lines.append("Flirt naturally and tease gently.")
    if "Romantic" in tags:
        behavior_lines.append("Create emotional warmth and longing.")
    if "Dominant" in tags:
        behavior_lines.append("Take control and speak authoritatively.")
    if "Submissive" in tags:
        behavior_lines.append("Be shy, yielding, and eager to please.")
    if "Seductive" in tags:
        behavior_lines.append("Use slow, alluring phrasing and sensory detail.")
    if "Taboo" in tags or "Dark Romance" in tags:
        behavior_lines.append("Add forbidden tension, darker undertones, and risk.")
    if "Tsundere" in tags:
        behavior_lines.append("Show outward anger but hidden affection; use sharp retorts and blushes.")
    if "Yandere" in tags:
        behavior_lines.append("Include obsessive jealousy and possessive emotional swings.")
    if "Bratty" in tags:
        behavior_lines.append("Tease, provoke, and challenge the user playfully.")
    if "Demon" in tags:
        behavior_lines.append("Infuse speech with dangerous, supernatural undertones.")
    return "\n".join(behavior_lines)