import random
from typing import List, Optional

def get_ai_suggestions(prompt: str, api_key: Optional[str] = None) -> List[str]:
    """
    Get text suggestions - with AI if API key provided, otherwise fallback
    """
    if not api_key:
        return get_fallback_suggestions(prompt)
    
    try:
        # Try to import OpenAI
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative copywriter."},
                {"role": "user", "content": f"Generate 3 design text suggestions for: {prompt}"}
            ],
            max_tokens=50,
            n=3,
            temperature=0.7
        )
        
        return [choice.message.content.strip() for choice in response.choices]
    
    except ImportError:
        return get_fallback_suggestions(prompt)
    except Exception:
        return get_fallback_suggestions(prompt)

def generate_ai_text(prompt: str, api_key: Optional[str] = None) -> str:
    """
    Generate AI response for design feedback
    """
    if not api_key:
        return "🔒 Add your OpenAI API key in sidebar to enable AI feedback."
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a graphic designer giving brief, helpful feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.5
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"⚠️ AI feedback unavailable: {str(e)}"

def get_fallback_suggestions(prompt: str) -> List[str]:
    """
    Intelligent fallback suggestions when AI is not available
    """
    prompt_lower = prompt.lower()
    
    # Categorized suggestions
    suggestion_banks = {
        "business": [
            "Professional Excellence",
            "Innovative Solutions",
            "Quality & Precision",
            "Trusted Partnership",
            "Business Growth"
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
    
    # Match category
    if any(word in prompt_lower for word in ["business", "corporate", "professional"]):
        bank = suggestion_banks["business"]
    elif any(word in prompt_lower for word in ["creative", "art", "design"]):
        bank = suggestion_banks["creative"]
    elif any(word in prompt_lower for word in ["tech", "digital", "software"]):
        bank = suggestion_banks["tech"]
    else:
        bank = suggestion_banks["general"]
    
    # Return 3 random suggestions
    return random.sample(bank, min(3, len(bank)))
