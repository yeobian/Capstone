from typing import Dict, List


# maps user-facing style names to internal keys
STYLE_GOAL_MAP = {
    "formal":      "more_formal",
    "casual":      "more_casual",
    "minimal":     "more_minimal",
    "sporty":      "more_sporty",
    "elegant":     "more_elegant",
    "streetwear":  "more_streetwear",
    "vintage":     "more_vintage",
    "colorful":    "more_colorful",
}

# maps avoid options to internal keys
AVOID_MAP = {
    "cropped":     "cropped",
    "hood":        "hood",
    "skinny fit":  "skinny_fit",
    "logos":       "logos",
    "patterns":    "patterns",
    "sheer":       "sheer",
    "embellished": "embellished",
}

# maps fit options to internal keys
FIT_MAP = {
    "slim": "slim",
    "regular": "regular",
    "relaxed": "relaxed",
    "oversized": "oversized",
}

# maps color names to internal keys
COLOR_MAP = {
    "black": "black", "white": "white", "beige": "beige",
    "gray": "gray", "navy": "navy", "blue": "blue",
    "red": "red", "green": "green", "pink": "pink",
    "brown": "brown", "yellow": "yellow", "orange": "orange", "purple": "purple",
}

# maps common free-text phrases to structured preference rules
FREE_TEXT_PATTERNS = {
    "more formal": {"goals": ["more_formal"]},
    "less sporty": {"avoid": ["sporty"]},
    "more casual": {"goals": ["more_casual"]},
    "more minimal": {"goals": ["more_minimal"]},
    "not cropped": {"avoid": ["cropped"]},
    "avoid cropped": {"avoid": ["cropped"]},
    "no hood": {"avoid": ["hood"]},
    "avoid hood": {"avoid": ["hood"]},
    "not skinny fit": {"avoid": ["skinny_fit"]},
    "avoid skinny fit": {"avoid": ["skinny_fit"]},
    "no logos": {"avoid": ["logos"]},
    "avoid logos": {"avoid": ["logos"]},
    "relaxed fit": {"constraints": {"fit": "relaxed"}},
    "regular fit": {"constraints": {"fit": "regular"}},
    "slim fit": {"constraints": {"fit": "slim"}},
    "oversized fit": {"constraints": {"fit": "oversized"}},
}


def _merge_unique(items: List[str], new_items: List[str]) -> List[str]:
    for item in new_items:
        if item not in items:
            items.append(item)
    return items


# parse free-text notes like "more casual" or "no hood" into structured rules
def parse_free_text_preferences(free_text: str) -> Dict:
    parsed = {
        "goals": [],
        "avoid": [],
        "constraints": {},
        "keywords": [],
    }

    text = free_text.strip().lower()
    if not text:
        return parsed

    parsed["keywords"].append(free_text.strip())

    for phrase, rule in FREE_TEXT_PATTERNS.items():
        if phrase in text:
            if "goals" in rule:
                parsed["goals"] = _merge_unique(parsed["goals"], rule["goals"])
            if "avoid" in rule:
                parsed["avoid"] = _merge_unique(parsed["avoid"], rule["avoid"])
            if "constraints" in rule:
                parsed["constraints"].update(rule["constraints"])

    return parsed


# combine all sidebar inputs into one preference object passed to reranking
def build_preference_schema(
    more_style: str,
    avoid_features: List[str],
    fit_preference: str,
    free_text: str,
    color_preference: str = "any",
) -> Dict:
    goals = []
    avoid = []
    constraints = {}
    keywords = []

    if more_style in STYLE_GOAL_MAP:
        goals.append(STYLE_GOAL_MAP[more_style])

    for item in avoid_features:
        if item in AVOID_MAP:
            avoid.append(AVOID_MAP[item])

    if fit_preference in FIT_MAP:
        constraints["fit"] = FIT_MAP[fit_preference]

    free_text = free_text.strip()
    if free_text:
        parsed = parse_free_text_preferences(free_text)
        goals = _merge_unique(goals, parsed["goals"])
        avoid = _merge_unique(avoid, parsed["avoid"])
        constraints.update(parsed["constraints"])
        keywords.extend(parsed["keywords"])

    return {
        "goals": goals,
        "avoid": avoid,
        "constraints": constraints,
        "keywords": keywords,
        "color": color_preference if color_preference != "any" else None,
        "confidence": 1.0,
    }


# summarize active preferences for display in the UI
def summarize_preferences(pref: Dict) -> str:
    parts = []

    if pref["goals"]:
        parts.append("Goals: " + ", ".join(pref["goals"]))

    if pref["avoid"]:
        parts.append("Avoid: " + ", ".join(pref["avoid"]))

    if pref["constraints"]:
        fit = pref["constraints"].get("fit")
        if fit:
            parts.append(f"Fit: {fit}")

    if pref["keywords"]:
        parts.append("Free text: " + "; ".join(pref["keywords"]))

    if not parts:
        return "No preference selected."

    return " | ".join(parts)
