import random
from typing import List, Optional

def get_ai_suggestions(prompt: str, api_key: Optional[str] = None) -> List[str]:
    """
    Get text suggestions - with AI if API key provided, otherwise fallback
    """
    # Always provide fallback suggestions
    fallback_suggestions = get_fallback_suggestions(prompt)
    
    if not api_key:
        return fallback_suggestions
    
    try:
        # Try to import OpenAI
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative copywriter. Generate 3 short design text suggestions."},
                {"role": "user", "content": f"Generate design text about: {prompt}"}
            ],
            max_tokens=50,
            n=3,
            temperature=0.7
        )
        
        suggestions = [choice.message.content.strip() for choice in response.choices]
        return suggestions if suggestions else fallback_suggestions
    
    except Exception:
        return fallback_suggestions

def generate_ai_text(prompt: str, api_key: Optional[str] = None) -> str:
    """
    Generate AI response for design feedback
    """
    if not api_key:
        return "✨ **Tip:** Add your OpenAI API key in the sidebar for AI-powered design feedback!"
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful design assistant. Provide brief, constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.5
        )
        
        return response.choices[0].message.content
    
    except Exception:
        return "AI feedback is currently unavailable. Try again later or check your API key."

def get_fallback_suggestions(prompt: str) -> List[str]:
    """
    Intelligent fallback suggestions when AI is not available
    """
    prompt_lower = prompt.lower()
    
    suggestion_banks = {
        "business": [
            "Professional Excellence",
            "Innovative Solutions",
            "Quality & Precision",
            "Business Growth",
            "Trusted Partnership"
        ],
        "creative": [
            "Creative Vision",
            "Artistic Expression",
            "Design Innovation",
            "Visual Storytelling",
            "Creative Minds"
        ],
        "tech": [
            "Tech Innovation",
            "Digital Solutions",
            "Future Ready",
            "Smart Technology",
            "Code & Create"
        ],
        "general": [
            "Make It Happen",
            "Dream Big",
            "Create Impact",
            "Simple & Beautiful",
            "Design Matters"
        ]
    }
    
    # Match category based on prompt
    if any(word in prompt_lower for word in ["business", "corporate", "professional", "company"]):
        bank = suggestion_banks["business"]
    elif any(word in prompt_lower for word in ["creative", "art", "design", "color", "draw"]):
        bank = suggestion_banks["creative"]
    elif any(word in prompt_lower for word in ["tech", "digital", "software", "app", "code"]):
        bank = suggestion_banks["tech"]
    else:
        bank = suggestion_banks["general"]
    
    # Return 3 random suggestions
    return random.sample(bank, min(3, len(bank)))
