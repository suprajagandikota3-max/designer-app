import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
import io
import os
from uuus.ai_text_generator import get_ai_suggestions, generate_ai_text

# Page configuration
st.set_page_config(
    page_title="Smart Designer App",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4A00E0;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        color: #8E2DE2;
        font-size: 1.3rem;
        margin-top: 1.5rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
    }
    .ai-suggestion-btn {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        margin: 5px 0;
    }
    .design-preview {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background: white;
    }
    .download-btn {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'design_count' not in st.session_state:
    st.session_state.design_count = 0
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = []
if 'selected_text' not in st.session_state:
    st.session_state.selected_text = "Smart Design"

# Header
st.markdown("<h1 class='main-header'>🎨 Smart Designer App</h1>", unsafe_allow_html=True)
st.markdown("### Create Beautiful Designs with AI Assistance")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    # API Key (optional)
    api_key = st.text_input("OpenAI API Key (optional):", type="password", 
                          help="Enter for AI features. Leave empty for demo mode.")
    
    st.markdown("---")
    
    # Quick Templates
    template = st.selectbox(
        "Choose Template:",
        ["Custom", "Social Media", "Business", "Event", "Promotion"]
    )
    
    # Apply template settings
    if template != "Custom":
        if template == "Social Media":
            st.session_state.bg_color = "#1DA1F2"
            st.session_state.text_color = "#FFFFFF"
        elif template == "Business":
            st.session_state.bg_color = "#2C3E50"
            st.session_state.text_color = "#ECF0F1"
        elif template == "Event":
            st.session_state.bg_color = "#9B59B6"
            st.session_state.text_color = "#FFFFFF"
        elif template == "Promotion":
            st.session_state.bg_color = "#E74C3C"
            st.session_state.text_color = "#FFFFFF"
    
    st.markdown("---")
    st.markdown(f"**Designs Created:** {st.session_state.design_count}")

# Main content in two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h3 class='sub-header'>✍️ Design Configuration SUPRAJA</h3>", unsafe_allow_html=True)
    
    # Text input section
    st.markdown("### Text Content")
    
    # AI Text Assistant
    with st.expander("🤖 AI Text Assistant", expanded=True):
        ai_prompt = st.text_input(
            "Describe what you need:",
            placeholder="e.g., 'slogan for bakery' or 'tech company tagline'",
            key="ai_prompt"
        )
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            if st.button("✨ Get AI Suggestions"):
                if ai_prompt:
                    with st.spinner("Generating suggestions..."):
                        suggestions = get_ai_suggestions(ai_prompt, api_key)
                        st.session_state.suggestions = suggestions
                        st.rerun()
                else:
                    st.warning("Please enter a description first")
        
        with col_a2:
            if st.button("🎲 Random Text"):
                random_texts = [
                    "Innovate. Create. Inspire.",
                    "Quality in Every Detail",
                    "Your Vision, Our Mission",
                    "Design Excellence",
                    "Simple & Effective"
                ]
                st.session_state.selected_text = random.choice(random_texts)
                st.rerun()
    
    # Display AI suggestions
    if st.session_state.suggestions:
        st.markdown("### 💡 AI Suggestions")
        for i, suggestion in enumerate(st.session_state.suggestions[:3]):
            if st.button(suggestion, key=f"sug_{i}"):
                st.session_state.selected_text = suggestion
                st.rerun()
    
    # Main text input
    design_text = st.text_area(
        "Enter your design text:",
        value=st.session_state.get('selected_text', 'Smart Design'),
        height=80,
        key="design_text"
    )
    
    # Design controls
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        font_size = st.slider("Font Size:", 20, 100, 48)
        bg_color = st.color_picker("Background:", "#FFFFFF")
    
    with col_c2:
        text_color = st.color_picker("Text Color:", "#000000")
        alignment = st.selectbox("Alignment:", ["Left", "Center", "Right"])
    
    # Generate button
    generate_btn = st.button("🚀 Generate Design", type="primary", use_container_width=True)

with col2:
    st.markdown("<h3 class='sub-header'>🎨 Design Preview</h3>", unsafe_allow_html=True)
    
    preview_container = st.container()
    
    with preview_container:
        if generate_btn and design_text:
            # Create image
            width = 600
            height = 400
            
            try:
                # Create image
                img = Image.new('RGB', (width, height), color=bg_color)
                draw = ImageDraw.Draw(img)
                
                # Try to use system font
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    # Fallback to default font
                    font = ImageFont.load_default(size=font_size)
                
                # Calculate text position
                text_bbox = draw.textbbox((0, 0), design_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # Set x position based on alignment
                x = 20
                if alignment == "Center":
                    x = (width - text_width) / 2
                elif alignment == "Right":
                    x = width - text_width - 20
                
                y = (height - text_height) / 2
                
                # Draw text
                draw.text((x, y), design_text, font=font, fill=text_color)
                
                # Convert to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                # Display
                st.image(img_bytes, use_column_width=True)
                
                # Download
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.download_button(
                        label="📥 Download PNG",
                        data=img_bytes,
                        file_name="my_design.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                with col_d2:
                    if st.button("🔄 Generate Another", use_container_width=True):
                        st.rerun()
                
                # Increment counter
                st.session_state.design_count += 1
                
                # Show AI feedback if API key provided
                if api_key:
                    with st.expander("🤖 AI Feedback", expanded=False):
                        feedback = generate_ai_text(
                            f"Design feedback for: '{design_text}' with {bg_color} background and {text_color} text",
                            api_key
                        )
                        st.info(feedback)
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Try a different font size or text")
        
        else:
            # Show placeholder
            placeholder = Image.new('RGB', (600, 400), color='#f0f2f6')
            draw = ImageDraw.Draw(placeholder)
            draw.text((100, 180), "Your design will appear here", fill="#666666")
            st.image(placeholder, use_column_width=True)
            
            # Quick tips
            st.info("💡 **Tips:** Enter text and click 'Generate Design' to start")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "🎨 **Smart Designer App** | Built with Streamlit | "
    "<a href='https://github.com/yourusername/smart-designer-app' target='_blank'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)
