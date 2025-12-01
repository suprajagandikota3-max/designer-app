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
    
    # Always include all fonts from our dictionary
    for font_name in FONT_STYLES.keys():
        available[font_name] = FONT_STYLES[font_name]
    
    return available

def load_font(font_name, font_size):
    """Load font with fallback handling - UPDATED FOR BETTER FONT LOADING"""
    try:
        # Try to load the font using multiple methods
        font_file_base = FONT_STYLES.get(font_name, "arial")
        
        # Common variations to try
        font_variations = [
            font_file_base + ".ttf",  # Most common
            font_file_base,  # Just the name
            font_file_base.upper() + ".ttf",  # Uppercase
            font_file_base.capitalize() + ".ttf",  # Capitalized
        ]
        
        # For specific fonts, add more variations
        if "Arial" in font_name:
            font_variations.extend(["arial.ttf", "Arial.ttf", "ARIAL.TTF"])
        elif "Times" in font_name:
            font_variations.extend(["times.ttf", "Times.ttf", "timesbd.ttf"])
        elif "Comic" in font_name:
            font_variations.extend(["comic.ttf", "Comic.ttf", "comicbd.ttf"])
        
        # Try each variation
        for font_variation in font_variations:
            try:
                return ImageFont.truetype(font_variation, font_size)
            except:
                continue
        
        # If all else fails, try to create a default font with the requested size
        try:
            # Try to use a default truetype font
            return ImageFont.truetype("arial.ttf", font_size)
        except:
            # Last resort: create a bitmap font with approximate size
            # Note: load_default() doesn't accept size parameter, so we'll scale it
            default_font = ImageFont.load_default()
            # We'll use the default and hope for the best
            return default_font
            
    except Exception as e:
        # Ultimate fallback
        return ImageFont.load_default()

# Page configuration
st.set_page_config(
    page_title="Smart Designer App",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS with larger font sizes
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem !important;
        color: #4A00E0;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        color: #8E2DE2;
        font-size: 2rem !important;
        margin-top: 1.5rem;
        font-weight: 600;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 16px !important;
    }
    .font-option {
        padding: 12px;
        border-radius: 8px;
        margin: 5px 0;
        border: 2px solid #e0e0e0;
        cursor: pointer;
        transition: all 0.3s;
        font-size: 16px !important;
    }
    .font-option:hover {
        background-color: #f5f5f5;
        transform: translateY(-2px);
        border-color: #667eea;
    }
    .font-option.selected {
        background: linear-gradient(135deg, #667eea30 0%, #764ba230 100%);
        border-color: #667eea;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
    }
    .font-preview-box {
        padding: 20px;
        margin: 15px 0;
        border-radius: 10px;
        background: white;
        border: 3px solid #e0e0e0;
        min-height: 100px;
        font-size: 18px !important;
    }
    .design-preview-container {
        border: 3px solid #8E2DE2;
        border-radius: 15px;
        padding: 20px;
        background: white;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 24px !important;
        font-weight: bold;
    }
    .stSlider {
        font-size: 16px !important;
    }
    .stSelectbox, .stTextArea, .stTextInput {
        font-size: 16px !important;
    }
    .info-text {
        font-size: 16px !important;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'design_count' not in st.session_state:
    st.session_state.design_count = 0
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = []
if 'selected_text' not in st.session_state:
    st.session_state.selected_text = "DESIGN YOUR VISION"
if 'selected_font' not in st.session_state:
    st.session_state.selected_font = "Arial Bold"
if 'available_fonts' not in st.session_state:
    st.session_state.available_fonts = detect_available_fonts()

# Header
st.markdown("<h1 class='main-header'>🎨 SMART DESIGNER APP</h1>", unsafe_allow_html=True)
st.markdown("### Create Beautiful Designs with AI Assistance")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ SETTINGS")
    
    # API Key (optional)
    api_key = st.text_input("OpenAI API Key (optional):", type="password", 
                          help="Enter for AI features. Leave empty for demo mode.")
    
    st.markdown("---")
    
    # Quick Templates
    template = st.selectbox(
        "Choose Template:",
        ["Custom", "Modern Business", "Creative Arts", "Tech Startup", "Elegant", "Bold & Bright", "Large Text"]
    )
    
    # Apply template settings - UPDATED WITH LARGER DEFAULT SIZES
    if template != "Custom":
        if template == "Modern Business":
            bg_color = "#2C3E50"
            text_color = "#ECF0F1"
            selected_font = "Arial Bold"
            font_size = 72
        elif template == "Creative Arts":
            bg_color = "#9B59B6"
            text_color = "#FFFFFF"
            selected_font = "Impact"
            font_size = 68
        elif template == "Tech Startup":
            bg_color = "#3498DB"
            text_color = "#FFFFFF"
            selected_font = "Courier New"
            font_size = 64
        elif template == "Elegant":
            bg_color = "#7F8C8D"
            text_color = "#F7F9F9"
            selected_font = "Georgia"
            font_size = 70
        elif template == "Bold & Bright":
            bg_color = "#E74C3C"
            text_color = "#FFFFFF"
            selected_font = "Impact"
            font_size = 80
        elif template == "Large Text":  # New template for extra large text
            bg_color = "#000000"
            text_color = "#FFFFFF"
            selected_font = "Arial Bold"
            font_size = 100
        
        # Apply template to variables
        if 'bg_color' not in locals():
            bg_color = "#FFFFFF"
        if 'text_color' not in locals():
            text_color = "#000000"
        if 'font_size' not in locals():
            font_size = 72  # Default large size
        
        # Store in session state
        st.session_state.template_bg = bg_color
        st.session_state.template_text = text_color
        st.session_state.template_font = selected_font
        st.session_state.template_size = font_size
        st.session_state.selected_font = selected_font
    
    st.markdown("---")
    st.markdown(f"**Designs Created:** {st.session_state.design_count}")
    st.markdown(f"**Available Fonts:** {len(st.session_state.available_fonts)}")

# Main content in two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h3 class='sub-header'>✍️ DESIGN CONFIGURATION</h3>", unsafe_allow_html=True)
    
    # Text input section
    st.markdown("### TEXT CONTENT")
    
    # AI Text Assistant
    with st.expander("🤖 AI TEXT ASSISTANT", expanded=True):
        ai_prompt = st.text_input(
            "Describe what you need:",
            placeholder="e.g., 'CATCHY SLOGAN FOR BAKERY' or 'TECH COMPANY TAGLINE'",
            key="ai_prompt"
        )
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            if st.button("✨ GET AI SUGGESTIONS"):
                if ai_prompt:
                    with st.spinner("Generating suggestions..."):
                        suggestions = get_ai_suggestions(ai_prompt, api_key)
                        st.session_state.suggestions = suggestions
                        st.rerun()
                else:
                    st.warning("Please enter a description first")
        
        with col_a2:
            if st.button("🎲 RANDOM TEXT"):
                random_texts = [
                    "INNOVATE. CREATE. INSPIRE.",
                    "QUALITY IN EVERY DETAIL",
                    "YOUR VISION, OUR MISSION",
                    "DESIGN EXCELLENCE",
                    "SIMPLE & EFFECTIVE",
                    "THINK BIG. DESIGN BOLD.",
                    "CREATIVE SOLUTIONS",
                    "MAKE IT HAPPEN"
                ]
                st.session_state.selected_text = random.choice(random_texts)
                st.rerun()
    
    # Display AI suggestions
    if st.session_state.suggestions:
        st.markdown("### 💡 AI SUGGESTIONS")
        for i, suggestion in enumerate(st.session_state.suggestions[:3]):
            if st.button(suggestion.upper(), key=f"sug_{i}", use_container_width=True):
                st.session_state.selected_text = suggestion
                st.rerun()
    
    # Main text input
    design_text = st.text_area(
        "ENTER YOUR DESIGN TEXT:",
        value=st.session_state.get('selected_text', 'DESIGN YOUR VISION'),
        height=100,
        key="design_text"
    )
    
    # Design controls in tabs
    tab1, tab2, tab3 = st.tabs(["📝 TEXT & FONT", "🎨 COLORS", "⚙️ LAYOUT"])
    
    with tab1:
        col_t1, col_t2 = st.columns([2, 1])
        
        with col_t1:
            # Font size slider - INCREASED RANGE
            font_size = st.slider(
                "FONT SIZE:", 
                min_value=40, 
                max_value=150, 
                value=72,  # Much larger default
                step=5,
                help="RECOMMENDED: 60-100 for large text, 40-60 for normal"
            )
            
            # Display current font size prominently
            st.markdown(f"### 📏 CURRENT SIZE: **{font_size}px**")
            
            # Font style selection
            st.markdown("### 🖋️ FONT STYLE")
            
            # Font category selector
            font_category = st.selectbox(
                "Filter by category:",
                ["All Fonts", "Sans-serif", "Serif", "Monospace", "Casual", "Bold Fonts"]
            )
            
            # Filter fonts based on category
            if font_category == "All Fonts":
                font_options = list(FONT_STYLES.keys())
            elif font_category == "Bold Fonts":
                font_options = ["Arial Bold", "Impact", "Georgia", "Times New Roman"]
            else:
                font_options = FONT_CATEGORIES.get(font_category, list(FONT_STYLES.keys()))
            
            # Display font options in a more compact way
            for font_name in font_options:
                is_selected = font_name == st.session_state.selected_font
                selected_class = "selected" if is_selected else ""
                
                # Display each font option
                col_font1, col_font2 = st.columns([4, 1])
                with col_font1:
                    st.markdown(
                        f"""
                        <div class="font-option {selected_class}">
                            <div style="font-family: '{font_name}', sans-serif; font-size: 16px;">
                                {font_name}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with col_font2:
                    if st.button("✓", key=f"btn_{font_name}", 
                               type="primary" if is_selected else "secondary",
                               help=f"Select {font_name}"):
                        st.session_state.selected_font = font_name
                        st.rerun()
        
        with col_t2:
            # Font preview box
            st.markdown("### 👀 FONT PREVIEW")
            preview_html = f"""
            <div class="font-preview-box" style="font-family: '{st.session_state.selected_font}', sans-serif; font-size: 20px;">
                <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">
                    {st.session_state.selected_font}
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>Sample Text:</strong><br>
                    The quick brown fox jumps
                </div>
                <div style="color: #666;">
                    <strong>Your Text Preview:</strong><br>
                    {design_text[:30]}...
                </div>
            </div>
            """
            st.markdown(preview_html, unsafe_allow_html=True)
            
            # Font size preview
            st.markdown(f"**Selected Font Size:** {font_size}px")
            if font_size < 50:
                st.warning("⚠️ Font size is small. Consider increasing for better visibility.")
            elif font_size > 90:
                st.success("✅ Large font selected - Good for banners and headers!")
    
    with tab2:
        st.markdown("### 🎨 COLOR SETTINGS")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            bg_color = st.color_picker("BACKGROUND COLOR:", "#FFFFFF")
            # Show current color
            st.markdown(f"<div style='background-color:{bg_color}; padding:10px; border-radius:5px;'>Background: {bg_color}</div>", unsafe_allow_html=True)
        
        with col_c2:
            text_color = st.color_picker("TEXT COLOR:", "#000000")
            # Show current color
            st.markdown(f"<div style='color:{text_color}; padding:10px; border-radius:5px; border:2px solid {text_color};'>Text Color: {text_color}</div>", unsafe_allow_html=True)
        
        # Color scheme suggestions
        col_scheme1, col_scheme2 = st.columns(2)
        with col_scheme1:
            if st.button("🎨 SUGGEST COLORS", use_container_width=True):
                color_schemes = [
                    ("#2C3E50", "#FFFFFF"),  # Dark blue / White
                    ("#000000", "#FFD700"),   # Black / Gold
                    ("#FFFFFF", "#FF0000"),   # White / Red
                    ("#000080", "#FFFFFF"),   # Navy / White
                    ("#008000", "#FFFFFF"),   # Green / White
                    ("#800080", "#FFFFFF"),   # Purple / White
                ]
                scheme = random.choice(color_schemes)
                bg_color = scheme[0]
                text_color = scheme[1]
                st.success(f"Applied: {scheme[0]} / {scheme[1]}")
        
        with col_scheme2:
            if st.button("🔄 HIGH CONTRAST", use_container_width=True):
                # High contrast combinations
                contrasts = [
                    ("#000000", "#FFFFFF"),  # Black/White
                    ("#FFFFFF", "#000000"),  # White/Black
                    ("#0000FF", "#FFFF00"),  # Blue/Yellow
                    ("#FF0000", "#00FF00"),  # Red/Green
                ]
                scheme = random.choice(contrasts)
                bg_color = scheme[0]
                text_color = scheme[1]
                st.success("High contrast scheme applied!")
    
    with tab3:
        st.markdown("### ⚙️ LAYOUT SETTINGS")
        alignment = st.selectbox("TEXT ALIGNMENT:", ["Left", "Center", "Right"])
        
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            padding = st.slider("PADDING:", 20, 150, 50, 
                              help="Space around text (higher = less text area)")
        with col_l2:
            line_spacing = st.slider("LINE SPACING:", 1.0, 3.0, 1.5, 0.1,
                                   help="Space between lines of text")
        
        # Alignment preview
        align_symbol = "←" if alignment == "Left" else "↑" if alignment == "Center" else "→"
        st.markdown(f"**Current Alignment:** {alignment} {align_symbol}")
    
    # Generate button - LARGE AND PROMINENT
    col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
    with col_gen2:
        generate_btn = st.button("🚀 **GENERATE DESIGN NOW!** 🚀", 
                                type="primary", 
                                use_container_width=True,
                                help="Click to create your design with current settings")

with col2:
    st.markdown("<h3 class='sub-header'>🎨 DESIGN PREVIEW</h3>", unsafe_allow_html=True)
    
    preview_container = st.container()
    
    with preview_container:
        if generate_btn and design_text:
            # Create image with larger dimensions for big text
            width = 800  # Increased from 600
            height = 500  # Increased from 400
            
            try:
                # Create image
                img = Image.new('RGB', (width, height), color=bg_color)
                draw = ImageDraw.Draw(img)
                
                # Load selected font
                font = load_font(st.session_state.selected_font, font_size)
                
                # Handle multiline text for large fonts
                lines = design_text.split('\n')
                total_height = 0
                line_heights = []
                
                # Calculate total height for all lines
                for line in lines:
                    if line.strip():  # Only calculate for non-empty lines
                        text_bbox = draw.textbbox((0, 0), line, font=font)
                        line_height = text_bbox[3] - text_bbox[1]
                        line_heights.append(line_height)
                        total_height += line_height * line_spacing
                    else:
                        line_heights.append(0)
                
                # If no lines with text, use single line
                if total_height == 0:
                    text_bbox = draw.textbbox((0, 0), design_text, font=font)
                    total_height = (text_bbox[3] - text_bbox[1]) * line_spacing
                    lines = [design_text]
                    line_heights = [text_bbox[3] - text_bbox[1]]
                
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
                
                # Display with border
                st.markdown("<div class='design-preview-container'>", unsafe_allow_html=True)
                st.image(img_bytes, use_column_width=True, caption="YOUR GENERATED DESIGN")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Show design info in large text
                with st.expander("📊 DESIGN DETAILS", expanded=True):
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.markdown(f"### 🖋️ **Font:** {st.session_state.selected_font}")
                        st.markdown(f"### 📏 **Size:** {font_size}px")
                    with col_info2:
                        st.markdown(f"### 🎯 **Alignment:** {alignment}")
                        st.markdown(f"### 🎨 **Colors:** BG: {bg_color}")
                
                # Download buttons - LARGE
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.download_button(
                        label="📥 **DOWNLOAD PNG** 📥",
                        data=img_bytes,
                        file_name=f"design_{st.session_state.design_count+1}.png",
                        mime="image/png",
                        use_container_width=True,
                        type="primary"
                    )
                
                with col_d2:
                    if st.button("🔄 **NEW DESIGN**", use_container_width=True):
                        st.session_state.selected_text = ""
                        st.rerun()
                
                # Increment counter
                st.session_state.design_count += 1
                
                # Show AI feedback if API key provided
                if api_key:
                    with st.expander("🤖 AI DESIGN ANALYSIS", expanded=False):
                        feedback = generate_ai_text(
                            f"Design analysis for: '{design_text}' with {font_size}px {st.session_state.selected_font} font, {bg_color} background and {text_color} text. Is the font size appropriate?",
                            api_key
                        )
                        st.info(feedback)
                else:
                    # Give font size feedback
                    if font_size > 80:
                        st.success("✅ **Great!** Large font size is perfect for banners and headers.")
                    elif font_size > 50:
                        st.info("💡 **Good size** - Clear and readable for most purposes.")
                    else:
                        st.warning("⚠️ **Consider** increasing font size for better visibility.")
            
            except Exception as e:
                st.error(f"❌ **Error generating design:** {str(e)}")
                st.info("💡 **Tip:** Try a different font or reduce the font size slightly.")
        
        else:
            # Show placeholder with larger preview
            placeholder = Image.new('RGB', (800, 500), color='#f0f2f6')
            draw = ImageDraw.Draw(placeholder)
            
            # Draw placeholder text
            try:
                # Try with a large font for the placeholder
                font = load_font(st.session_state.selected_font, 48)
                draw.text((100, 150), "DESIGN PREVIEW AREA", fill="#4A00E0", font=font)
                draw.text((100, 220), "Enter text and click", fill="#666666", font=font)
                draw.text((100, 270), "'GENERATE DESIGN NOW!'", fill="#8E2DE2", font=font)
                draw.text((100, 350), f"Font: {st.session_state.selected_font}", fill="#888888", font=font)
            except:
                # Fallback
                draw.text((100, 200), "ENTER TEXT AND CLICK GENERATE", fill="#4A00E0")
            
            st.markdown("<div class='design-preview-container'>", unsafe_allow_html=True)
            st.image(placeholder, use_column_width=True, caption="PREVIEW AREA - YOUR DESIGN WILL APPEAR HERE")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Quick tips in large text
            st.markdown("""
            ### 💡 **QUICK START GUIDE:**
            1. **ENTER YOUR TEXT** - Type what you want to display
            2. **CHOOSE A FONT** - Select from 14+ font styles
            3. **SET FONT SIZE** - Use 60-100px for large text
            4. **SELECT COLORS** - Pick background and text colors
            5. **CLICK GENERATE** - Create your design instantly!
            
            **🎯 TIP:** For banners and posters, use font sizes above **70px**!
            """)

# Footer
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns([1, 3, 1])
with col_f2:
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 1.1rem; padding: 20px;'>
        <p style='font-size: 1.3rem; font-weight: bold;'>🎨 <b>SMART DESIGNER APP</b> 🎨</p>
        <p>Create stunning designs with <b>LARGE, BOLD TEXT</b> | Fonts: {font_count} available</p>
        <p style='font-size: 0.9rem; color: #888;'>Perfect for banners, posters, social media graphics, and more!</p>
        </div>
        """.format(font_count=len(st.session_state.available_fonts)),
        unsafe_allow_html=True
    )

# Add some JavaScript for better interaction
st.markdown("""
<script>
// Auto-focus on text input
document.addEventListener('DOMContentLoaded', function() {
    // Make font options more interactive
    const fontOptions = document.querySelectorAll('.font-option');
    fontOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all
            fontOptions.forEach(opt => opt.classList.remove('selected'));
            // Add to clicked
            this.classList.add('selected');
            // Find and click the corresponding button
            const fontName = this.textContent.trim();
            const button = document.querySelector(`button[data-testid*="${fontName}"]`);
            if (button) button.click();
        });
    });
    
    // Highlight large font sizes in preview
    const fontSizeInput = document.querySelector('input[type="range"]');
    if (fontSizeInput) {
        fontSizeInput.addEventListener('input', function() {
            const size = this.value;
            if (size > 80) {
                this.style.border = "2px solid #4CAF50";
                this.style.boxShadow = "0 0 10px #4CAF50";
            } else {
                this.style.border = "";
                this.style.boxShadow = "";
            }
        });
    }
});
</script>
""", unsafe_allow_html=True)
