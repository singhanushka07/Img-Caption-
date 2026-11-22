STYLE_PROMPTS = {
    "descriptive": (
        "Generate a detailed, factual description of this image. "
        "Describe the main subjects, their actions, the setting, colors, "
        "lighting, and spatial relationships. Be thorough and objective."
    ),
    "creative": (
        "Write a creative, artistic caption for this image. "
        "Use vivid language, metaphors, and storytelling elements. "
        "Evoke emotions and paint a narrative around what you see."
    ),
    "technical": (
        "Provide a precise, analytical description of this image. "
        "Focus on composition, color palette, objects present, "
        "their positions, textures, and any notable visual patterns."
    ),
    "concise": (
        "Write a single, concise sentence that captures the essence "
        "of this image. Be brief but informative."
    ),
    "social_media": (
        "Write an engaging social media caption for this image. "
        "Make it catchy and shareable. Include relevant emojis "
        "and 3-5 popular hashtags at the end."
    ),
}

AVAILABLE_STYLES = list(STYLE_PROMPTS.keys())


def get_style_prompt(style: str) -> str:
    return STYLE_PROMPTS.get(style, STYLE_PROMPTS["descriptive"])
