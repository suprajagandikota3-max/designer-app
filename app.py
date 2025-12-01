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

# Custom CSS with font previews
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4A00E0;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Arial', sans-serif;
    }
    .sub-header {
        color: #8E2DE2;
        font-size: 1.3rem;
        margin-top: 1.5rem;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        font-family: 'Arial', sans-serif;
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
    .font-option {
        padding: 8px;
        border-radius: 5px;
        margin: 3px 0;
        border: 1px solid #e0e0e0;
        cursor: pointer;
    }
    .font-option:hover {
        background-color: #f5f5f5;
    }
    .font-option.selected {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        border-color: #667eea;
    }
    .font-preview {
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        background: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# Available fonts dictionary with fallbacks
FONT_STYLES = {
    "Arial": "arial.ttf",
    "Arial Bold": "arialbd.ttf",
    "Times New Roman": "times.ttf",
    "Georgia": "georgia.ttf",
    "Verdana": "verdana.ttf",
    "Courier New": "cour.ttf",
    "Trebuchet MS": "trebuc.ttf",
    "Comic Sans MS": "comic.ttf",
    "Impact": "impact.ttf",
    "Tahoma": "tahoma.ttf",
    "Lucida Console": "lucon.ttf",
    "Palatino": "pala.ttf",
    "Garamond": "gara.ttf",
    "Bookman": "bookman.ttf"
}

# Font categories for better organization
FONT_CATEGORIES = {
    "Sans-serif": ["Arial", "Arial Bold", "Verdana", "Tahoma", "Trebuchet MS"],
    "Serif": ["Times New Roman", "Georgia", "Palatino", "Garamond", "Bookman"],
    "Monospace": ["Courier New", "Lucida Console"],
    "Casual": ["Comic Sans MS", "Impact"]
}

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

def detect_available_fonts():
    """Detect which fonts are available on the system"""
    available = {}
    system_fonts = [
        "arial.ttf", "arialbd.ttf", "times.ttf", "georgia.ttf", 
        "verdana.ttf", "cour.ttf", "trebuc.ttf", "comic.ttf",
        "impact.ttf", "tahoma.ttf", "lucon.ttf", "pala.ttf",
        "gara.ttf", "bookman.ttf"
    ]
    
    # Common font paths for different OS
    font_paths = [
        "/usr/share/fonts/truetype/",
        "/usr/share/fonts/TTF/",
        "C:/Windows/Fonts/",
        "/Library/Fonts/",
        "/System/Library/Fonts/"
    ]
    
    for font_name, font_file in FONT_STYLES.items():
        available[font_name] = font_file
    
    return available

def load_font(font_name, font_size):
    """Load font with fallback handling"""
    try:
        # First try to load from system
        if font_name in st.session_state.available_fonts:
            font_file = st.session_state.available_fonts[font_name]
            font_paths_to_try = [
                font_file,
                f"C:/Windows/Fonts/{font_file}",
                f"/usr/share/fonts/truetype/{font_file}",
                f"/Library/Fonts/{font_file}"
            ]
            
            for font_path in font_paths_to_try:
                try:
                    return ImageFont.truetype(font_path, font_size)
                except:
                    continue
        
        # Try direct loading for common fonts
        try:
            return ImageFont.truetype(font_name.lower().replace(" ", ""), font_size)
        except:
            # Fallback to default font
            return ImageFont.load_default()
            
    except Exception as e:
        st.warning(f"Font '{font_name}' not found. Using default font.")
        return ImageFont.load_default()

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
            st.session_state.bg_color = "#2C3E50"
            st.session_state.text_color = "#ECF0F1"
            st.session_state.selected_font = "Arial"
        elif template == "Creative Arts":
            st.session_state.bg_color = "#9B59B6"
            st.session_state.text_color = "#FFFFFF"
            st.session_state.selected_font = "Comic Sans MS"
        elif template == "Tech Startup":
            st.session_state.bg_color = "#3498DB"
            st.session_state.text_color = "#FFFFFF"
            st.session_state.selected_font = "Courier New"
        elif template == "Elegant":
            st.session_state.bg_color = "#7F8C8D"
            st.session_state.text_color = "#F7F9F9"
            st.session_state.selected_font = "Georgia"
        elif template == "Bold & Bright":
            st.session_state.bg_color = "#E74C3C"
            st.session_state.text_color = "#FFFFFF"
            st.session_state.selected_font = "Impact"
    
    st.markdown("---")
    st.markdown(f"**Designs Created:** {st.session_state.design_count}")

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
            font_size = st.slider("Font Size:", 20, 120, 48, help="Adjust text size")
            
            # Font style selection with preview
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
            
            # Display fonts in columns for better layout
            font_cols = st.columns(2)
            for idx, font_name in enumerate(font_options):
                col_idx = idx % 2
                with font_cols[col_idx]:
                    font_class = "selected" if font_name == st.session_state.selected_font else ""
                    st.markdown(
                        f"""
                        <div class="font-option {font_class}" onclick="
                            this.style.backgroundColor='#f0f0f0';
                            setTimeout(() => {{
                                document.getElementById('font_{font_name}').click();
                            }}, 100);
                        ">
                            <div style="font-family: '{font_name}', sans-serif; padding: 5px;">
                                {font_name}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Hidden radio button
                    if st.button(f"Select {font_name}", key=f"font_{font_name}", type="secondary", use_container_width=True):
                        st.session_state.selected_font = font_name
                        st.rerun()
        
        with col_t2:
            # Font preview
            st.markdown("**Preview:**")
            preview_text = design_text[:30] + "..." if len(design_text) > 30 else design_text
            preview_html = f"""
            <div class="font-preview" style="
                font-family: '{st.session_state.selected_font}', sans-serif;
                font-size: 16px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
            ">
                {preview_text}
            </div>
            """
            st.markdown(preview_html, unsafe_allow_html=True)
            
            # Show current selection
            st.info(f"Selected: **{st.session_state.selected_font}**")
    
    with tab2:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            bg_color = st.color_picker("Background Color:", "#FFFFFF")
        with col_c2:
            text_color = st.color_picker("Text Color:", "#000000")
        
        # Color scheme suggestions
        if st.button("🎨 Suggest Colors"):
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
            st.success(f"Applied: {scheme[0]} / {scheme[1]}")
    
    with tab3:
        alignment = st.selectbox("Text Alignment:", ["Left", "Center", "Right"], 
                               help="Align text within the design")
        
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            padding = st.slider("Padding:", 10, 100, 30, 
                              help="Space around text")
        with col_l2:
            line_spacing = st.slider("Line Spacing:", 1.0, 2.5, 1.2, 0.1,
                                   help="Space between lines")
    
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
                
                # Handle multiline text
                lines = design_text.split('\n')
                total_height = 0
                line_heights = []
                
                # Calculate total height
                for line in lines:
                    if line.strip():  # Only calculate for non-empty lines
                        text_bbox = draw.textbbox((0, 0), line, font=font)
                        line_height = text_bbox[3] - text_bbox[1]
                        line_heights.append(line_height)
                        total_height += line_height * line_spacing
                    else:
                        line_heights.append(0)
                
                # Calculate starting Y position
                start_y = (height - total_height) / 2
                current_y = start_y
                
                # Draw each line
                for i, line in enumerate(lines):
                    if line.strip():  # Only draw non-empty lines
                        text_bbox = draw.textbbox((0, 0), line, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        line_height = line_heights[i]
                        
                        # Set x position based on alignment
                        if alignment == "Left":
                            x = padding
                        elif alignment == "Center":
                            x = (width - text_width) / 2
                        else:  # Right
                            x = width - text_width - padding
                        
                        # Draw text
                        draw.text((x, current_y), line, font=font, fill=text_color)
                        current_y += line_height * line_spacing
                
                # Convert to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                # Display
                st.image(img_bytes, use_column_width=True)
                
                # Show design info
                with st.expander("📊 Design Details", expanded=False):
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.metric("Font", st.session_state.selected_font)
                        st.metric("Font Size", f"{font_size}px")
                    with col_info2:
                        st.metric("Alignment", alignment)
                        st.metric("Colors", f"BG: {bg_color}")
                
                # Download buttons
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.download_button(
                        label="📥 Download PNG",
                        data=img_bytes,
                        file_name=f"design_{st.session_state.design_count+1}.png",
                        mime="image/png",
                        use_container_width=True,
                        type="primary"
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
                        feedback_prompt = f"""
                        Design Analysis:
                        - Text: "{design_text}"
                        - Font: {st.session_state.selected_font} ({font_size}px)
                        - Colors: {bg_color} background, {text_color} text
                        - Alignment: {alignment}
                        
                        Give brief, constructive feedback on this design.
                        """
                        feedback = generate_ai_text(feedback_prompt, api_key)
                        st.info(feedback)
            
            except Exception as e:
                st.error(f"Error generating design: {str(e)}")
                st.info("Try adjusting font size or using a different font")
        
        else:
            # Show placeholder with current font preview
            placeholder = Image.new('RGB', (600, 400), color='#f0f2f6')
            draw = ImageDraw.Draw(placeholder)
            
            # Try to draw with selected font
            try:
                font = load_font(st.session_state.selected_font, 24)
                draw.text((100, 180), "Your design will appear here", fill="#666666", font=font)
            except:
                draw.text((100, 180), "Your design will appear here", fill="#666666")
            
            st.image(placeholder, use_column_width=True)
            
            # Quick tips
            with st.expander("💡 Design Tips", expanded=True):
                st.markdown("""
                1. **Font Selection**: Choose a font that matches your message
                2. **Color Contrast**: Ensure text is readable against background
                3. **Font Size**: Larger sizes for headings, smaller for details
                4. **Alignment**: Center for formal, left for casual
                5. **AI Assistant**: Use AI for creative text suggestions
                """)

# Footer
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
with col_f2:
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>🎨 <b>Smart Designer App</b> | Fonts Available: {font_count} | 
        <a href='https://github.com/yourusername/smart-designer-app' target='_blank'>GitHub</a></p>
        <p style='font-size: 0.8rem; color: #888;'>
        Supports: {font_list}
        </p>
        </div>
        """.format(
            font_count=len(st.session_state.available_fonts),
            font_list=", ".join(list(st.session_state.available_fonts.keys())[:5])
        ),
        unsafe_allow_html=True
    )

# Add JavaScript for better font selection
st.markdown("""
<script>
// Add click handlers for font options
document.addEventListener('DOMContentLoaded', function() {
    const fontOptions = document.querySelectorAll('.font-option');
    fontOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all
            fontOptions.forEach(opt => opt.classList.remove('selected'));
            // Add selected class to clicked
            this.classList.add('selected');
        });
    });
});
</script>
""", unsafe_allow_html=True)
