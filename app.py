import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
import io
import os
from uuus.ai_text_generator import get_ai_suggestions, generate_ai_text

# Available fonts dictionary
FONT_STYLES = {
    "Arial": "arial",
    "Arial Bold": "arialbd",
    "Times New Roman": "times",
    "Georgia": "georgia",
    "Verdana": "verdana",
    "Courier New": "cour",
    "Trebuchet MS": "trebuc",
    "Comic Sans MS": "comic",
    "Impact": "impact",
    "Tahoma": "tahoma",
    "Lucida Console": "lucon",
    "Palatino": "pala",
    "Garamond": "gara",
    "Bookman": "bookman"
}

# Font categories for better organization
FONT_CATEGORIES = {
    "Sans-serif": ["Arial", "Arial Bold", "Verdana", "Tahoma", "Trebuchet MS"],
    "Serif": ["Times New Roman", "Georgia", "Palatino", "Garamond", "Bookman"],
    "Monospace": ["Courier New", "Lucida Console"],
    "Casual": ["Comic Sans MS", "Impact"]
}

def detect_available_fonts():
    """Detect which fonts are available on the system"""
    available = {}
    
    # Common fonts that are usually available
    common_fonts = {
        "Arial": ["arial.ttf", "arial"],
        "Times New Roman": ["times.ttf", "times"],
        "Verdana": ["verdana.ttf", "verdana"],
        "Georgia": ["georgia.ttf", "georgia"],
        "Courier New": ["cour.ttf", "cour"],
        "Comic Sans MS": ["comic.ttf", "comic"],
        "Impact": ["impact.ttf", "impact"]
    }
    
    # Always include default fonts that should work
    for font_name in FONT_STYLES.keys():
        available[font_name] = FONT_STYLES[font_name]
    
    return available

def load_font(font_name, font_size):
    """Load font with fallback handling"""
    try:
        # Try to load the font
        font_file = FONT_STYLES.get(font_name, "arial")
        
        # Common font paths to try
        font_paths = [
            font_file + ".ttf",
            font_file,
            "arial.ttf",  # Fallback
            None  # Will trigger default font
        ]
        
        for font_path in font_paths:
            try:
                if font_path:
                    return ImageFont.truetype(font_path, font_size)
            except:
                continue
        
        # Fallback to default font
        return ImageFont.load_default()
            
    except Exception as e:
        # If everything fails, use default font
        return ImageFont.load_default()

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
    .font-option {
        padding: 8px;
        border-radius: 5px;
        margin: 3px 0;
        border: 1px solid #e0e0e0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .font-option:hover {
        background-color: #f5f5f5;
        transform: translateY(-2px);
    }
    .font-option.selected {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        border-color: #667eea;
        box-shadow: 0 2px 5px rgba(102, 126, 234, 0.2);
    }
    .font-preview-box {
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        background: white;
        border: 2px solid #e0e0e0;
        min-height: 80px;
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
if 'selected_font' not in st.session_state:
    st.session_state.selected_font = "Arial"
if 'available_fonts' not in st.session_state:
    st.session_state.available_fonts = detect_available_fonts()

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
        ["Custom", "Modern Business", "Creative Arts", "Tech Startup", "Elegant", "Bold & Bright"]
    )
    
    # Apply template settings
    if template != "Custom":
        if template == "Modern Business":
            bg_color = "#2C3E50"
            text_color = "#ECF0F1"
            selected_font = "Arial"
        elif template == "Creative Arts":
            bg_color = "#9B59B6"
            text_color = "#FFFFFF"
            selected_font = "Comic Sans MS"
        elif template == "Tech Startup":
            bg_color = "#3498DB"
            text_color = "#FFFFFF"
            selected_font = "Courier New"
        elif template == "Elegant":
            bg_color = "#7F8C8D"
            text_color = "#F7F9F9"
            selected_font = "Georgia"
        elif template == "Bold & Bright":
            bg_color = "#E74C3C"
            text_color = "#FFFFFF"
            selected_font = "Impact"
        
        # Apply template to session state
        if 'bg_color' not in st.session_state:
            st.session_state.bg_color = bg_color
        if 'text_color' not in st.session_state:
            st.session_state.text_color = text_color
        st.session_state.selected_font = selected_font
    
    st.markdown("---")
    st.markdown(f"**Designs Created:** {st.session_state.design_count}")
    st.markdown(f"**Available Fonts:** {len(st.session_state.available_fonts)}")

# Main content in two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h3 class='sub-header'>✍️ Design Configuration</h3>", unsafe_allow_html=True)
    
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
    
    # Design controls in tabs
    tab1, tab2, tab3 = st.tabs(["📝 Text & Font", "🎨 Colors", "⚙️ Layout"])
    
    with tab1:
        col_t1, col_t2 = st.columns([2, 1])
        
        with col_t1:
            font_size = st.slider("Font Size:", 20, 120, 48)
            
            # Font style selection
            st.markdown("**Font Style:**")
            
            # Font category selector
            font_category = st.selectbox(
                "Filter by category:",
                ["All Fonts", "Sans-serif", "Serif", "Monospace", "Casual"]
            )
            
            # Filter fonts based on category
            if font_category == "All Fonts":
                font_options = list(FONT_STYLES.keys())
            else:
                font_options = FONT_CATEGORIES.get(font_category, list(FONT_STYLES.keys()))
            
            # Display font options
            for font_name in font_options:
                col_f1, col_f2 = st.columns([3, 1])
                with col_f1:
                    # Font preview
                    font_style = f"font-family: '{font_name}', sans-serif;"
                    is_selected = font_name == st.session_state.selected_font
                    selected_class = "selected" if is_selected else ""
                    
                    st.markdown(
                        f"""
                        <div class="font-option {selected_class}" onclick="
                            document.getElementById('select_{font_name}').click();
                        ">
                            <div style="{font_style} font-size: 14px; padding: 5px;">
                                {font_name}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with col_f2:
                    if st.button("Select", key=f"select_{font_name}", type="primary" if is_selected else "secondary"):
                        st.session_state.selected_font = font_name
                        st.rerun()
        
        with col_t2:
            # Font preview box
            st.markdown("**Font Preview:**")
            preview_html = f"""
            <div class="font-preview-box" style="font-family: '{st.session_state.selected_font}', sans-serif; font-size: 16px;">
                <strong>Selected Font:</strong><br>
                {st.session_state.selected_font}<br><br>
                <strong>Sample:</strong><br>
                The quick brown fox jumps
            </div>
            """
            st.markdown(preview_html, unsafe_allow_html=True)
            
            # Font info
            st.info(f"**Current:** {st.session_state.selected_font}")
    
    with tab2:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            bg_color = st.color_picker("Background Color:", "#FFFFFF")
        with col_c2:
            text_color = st.color_picker("Text Color:", "#000000")
        
        # Color scheme suggestions
        if st.button("🎨 Suggest Color Scheme"):
            color_schemes = [
                ("#2C3E50", "#ECF0F1"),  # Dark blue / Light gray
                ("#E74C3C", "#FFFFFF"),   # Red / White
                ("#27AE60", "#FFFFFF"),   # Green / White
                ("#8E44AD", "#FFFFFF"),   # Purple / White
                ("#F39C12", "#2C3E50"),   # Orange / Dark blue
                ("#000000", "#F1C40F"),   # Black / Yellow
            ]
            scheme = random.choice(color_schemes)
            bg_color = scheme[0]
            text_color = scheme[1]
            st.success(f"Applied color scheme!")
    
    with tab3:
        alignment = st.selectbox("Text Alignment:", ["Left", "Center", "Right"])
        padding = st.slider("Padding:", 10, 100, 30)
    
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
                
                # Load selected font
                font = load_font(st.session_state.selected_font, font_size)
                
                # Calculate text position
                text_bbox = draw.textbbox((0, 0), design_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # Set x position based on alignment
                x = padding
                if alignment == "Center":
                    x = (width - text_width) / 2
                elif alignment == "Right":
                    x = width - text_width - padding
                
                y = (height - text_height) / 2
                
                # Draw text
                draw.text((x, y), design_text, font=font, fill=text_color)
                
                # Convert to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                # Display
                st.image(img_bytes, use_column_width=True, caption="Your Generated Design")
                
                # Show design info
                with st.expander("📊 Design Details", expanded=False):
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.metric("Font", st.session_state.selected_font)
                        st.metric("Font Size", f"{font_size}px")
                    with col_info2:
                        st.metric("Alignment", alignment)
                        st.metric("Background", bg_color)
                
                # Download buttons
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
                    if st.button("🔄 New Design", use_container_width=True):
                        st.session_state.selected_text = ""
                        st.rerun()
                
                # Increment counter
                st.session_state.design_count += 1
                
                # Show AI feedback if API key provided
                if api_key:
                    with st.expander("🤖 AI Design Analysis", expanded=False):
                        feedback = generate_ai_text(
                            f"Design feedback for: '{design_text}' with {st.session_state.selected_font} font, {bg_color} background and {text_color} text",
                            api_key
                        )
                        st.info(feedback)
            
            except Exception as e:
                st.error(f"Error generating design: {str(e)}")
                st.info("Try adjusting the font size or using a different font")
        
        else:
            # Show placeholder
            placeholder = Image.new('RGB', (600, 400), color='#f0f2f6')
            draw = ImageDraw.Draw(placeholder)
            
            # Draw placeholder text
            try:
                font = load_font(st.session_state.selected_font, 24)
                draw.text((100, 180), "Design Preview", fill="#666666", font=font)
                draw.text((100, 220), f"Font: {st.session_state.selected_font}", fill="#888888", font=font)
            except:
                draw.text((100, 180), "Enter text and click 'Generate Design'", fill="#666666")
            
            st.image(placeholder, use_column_width=True, caption="Preview Area")
            
            # Quick tips
            st.info("💡 **Quick Start:**\n1. Enter your text\n2. Choose a font\n3. Select colors\n4. Click 'Generate Design'")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "🎨 **Smart Designer App** | Fonts: {font_count} available | "
    "Built with Streamlit"
    "</div>".format(font_count=len(st.session_state.available_fonts)),
    unsafe_allow_html=True
)
