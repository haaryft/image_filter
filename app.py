import streamlit as st
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import segno
import io
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PixelForge & QR Studio",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR BETTER UI ---
st.markdown("""
<style>
    .reportview-container { background: #f5f7f8; }
    .main .block-container { padding-top: 2rem; }
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stDownloadButton > button {
        width: 100%;
        background-color: #008CBA !important;
        color: white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# --- MAIN WORKSPACE NAVIGATION ---
st.sidebar.title("🛠️ Production Workspace")
workspace_mode = st.sidebar.radio(
    "Select Studio Module:",
    ["🎨 Advanced Image Studio", "🔮 Universal QR Engine"]
)
st.sidebar.markdown("---")


# =====================================================================
# MODE A: ADVANCED IMAGE STUDIO
# =====================================================================
if workspace_mode == "🎨 Advanced Image Studio":
    st.title("🎨 Advanced Image Studio")
    st.write("Perform professional image convolution, direct canvas manipulation, and asset compression.")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload Source Asset", 
        type=["jpg", "jpeg", "png"],
        key="image_uploader"
    )

    if uploaded_file is not None:
        try:
            # Load original asset
            original_image = Image.open(uploaded_file)
            
            # Create working layout tabs for organization
            filter_tab, transform_tab, compress_tab = st.tabs([
                "✨ High-Fidelity Filters", 
                "📐 Canvas Manipulation", 
                "🗜️ Compression & Export"
            ])
            
            # State Management for manipulations
            work_img = original_image.copy()
            
            # --- TAB 1: FILTERS ---
            with filter_tab:
                st.subheader("Filter Pipeline Control")
                selected_filter = st.selectbox(
                    "Choose an Advanced Filter State:",
                    [
                        "Original", "Black & White", "Sepia Tone", "Gaussian Blur", 
                        "Contour Sketch", "Vibrant Saturation", "Retro Negative", "Emboss Art"
                    ]
                )
                
                try:
                    if selected_filter == "Black & White":
                        work_img = ImageOps.grayscale(work_img)
                    elif selected_filter == "Sepia Tone":
                        gray = ImageOps.grayscale(work_img)
                        work_img = ImageOps.colorize(gray, "#704214", "#C0B283")
                    elif selected_filter == "Gaussian Blur":
                        work_img = work_img.filter(ImageFilter.GaussianBlur(radius=5))
                    elif selected_filter == "Contour Sketch":
                        work_img = work_img.filter(ImageFilter.CONTOUR)
                    elif selected_filter == "Vibrant Saturation":
                        converter = ImageEnhance.Color(work_img)
                        work_img = converter.enhance(2.5)
                    elif selected_filter == "Retro Negative":
                        # Convert to RGB if RGBA to safely apply invert
                        if work_img.mode == 'RGBA':
                            r, g, b, a = work_img.split()
                            rgb_img = Image.merge('RGB', (r, g, b))
                            inverted = ImageOps.invert(rgb_img)
                            r2, g2, b2 = inverted.split()
                            work_img = Image.merge('RGBA', (r2, g2, b2, a))
                        else:
                            work_img = ImageOps.invert(work_img)
                    elif selected_filter == "Emboss Art":
                        work_img = work_img.filter(ImageFilter.EMBOSS)
                except Exception as filter_error:
                    st.error(f"Filter Execution Failure: {str(filter_error)}")

            # --- TAB 2: CANVAS MANIPULATION ---
            with transform_tab:
                col_crop, col_resize = st.columns(2)
                
                with col_crop:
                    st.markdown("### ✂️ Boundary Slicing (Crop)")
                    w, h = work_img.size
                    crop_left = st.number_input("Left Cut (px)", min_value=0, max_value=w-1, value=0)
                    crop_top = st.number_input("Top Cut (px)", min_value=0, max_value=h-1, value=0)
                    crop_right = st.number_input("Right Cut (px)", min_value=1, max_value=w, value=w)
                    crop_bottom = st.number_input("Bottom Cut (px)", min_value=1, max_value=h, value=h)
                    
                    if crop_left < crop_right and crop_top < crop_bottom:
                        try:
                            work_img = work_img.crop((crop_left, crop_top, crop_right, crop_bottom))
                        except Exception as crop_error:
                            st.error(f"Cropping Engine Error: {str(crop_error)}")
                    else:
                        st.warning("Invalid crop boundaries. Left must be less than Right, and Top less than Bottom.")

                with col_resize:
                    st.markdown("### 📐 Structural Resizing")
                    curr_w, curr_h = work_img.size
                    st.text(f"Current Size: {curr_w}x{curr_h} px")
                    
                    maintain_aspect = st.checkbox("Maintain Aspect Ratio", value=True)
                    
                    if maintain_aspect:
                        scale_percent = st.slider("Scale Ratio (%)", min_value=5, max_value=200, value=100)
                        new_w = int(curr_w * (scale_percent / 100))
                        new_h = int(curr_h * (scale_percent / 100))
                    else:
                        new_w = st.number_input("Target Width (px)", min_value=1, value=curr_w)
                        new_h = st.number_input("Target Height (px)", min_value=1, value=curr_h)
                    
                    try:
                        work_img = work_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    except Exception as resize_error:
                        st.error(f"Resampling Engine Error: {str(resize_error)}")

            # --- TAB 3: COMPRESSION & EXPORT ---
            with compress_tab:
                st.subheader("Image Compression Optimization Engine")
                quality_val = st.slider("Output Save Quality Metric (1-100)", min_value=1, max_value=100, value=85)
                
                # Dynamic optimization calculation
                try:
                    img_buffer = io.BytesIO()
                    # Determine save format based on mode or default to PNG/JPEG
                    save_format = "JPEG" if work_img.mode in ["RGB", "L"] else "PNG"
                    
                    if save_format == "JPEG":
                        work_img.save(img_buffer, format=save_format, quality=quality_val)
                    else:
                        # PNG handles compression differently via optimize
                        work_img.save(img_buffer, format=save_format, optimize=True)
                        
                    byte_weight = len(img_buffer.getvalue())
                    kb_weight = byte_weight / 1024
                    
                    # Metrics Display Panel
                    st.metric(
                        label="Dynamic Payload Optimization Size", 
                        value=f"{kb_weight:.2f} KB", 
                        delta=f"{(kb_weight - (uploaded_file.size/1024)):.2f} KB vs Source"
                    )
                except Exception as compress_error:
                    st.error(f"Compression Diagnostic Failure: {str(compress_error)}")

            # --- DIRECT SCREEN GRID COMPARISON ---
            st.markdown("---")
            view_col1, view_col2 = st.columns(2)
            
            with view_col1:
                st.markdown("### 📸 Original Production Asset")
                st.image(original_image, use_container_width=True)
                st.caption(f"Dimensions: {original_image.size[0]}x{original_image.size[1]} | Size: {uploaded_file.size/1024:.2f} KB")
                
            with view_col2:
                st.markdown(f"### ✨ Processed Matrix Layout ({selected_filter})")
                st.image(work_img, use_container_width=True)
                st.caption(f"Dimensions: {work_img.size[0]}x{work_img.size[1]}")
                
                # Active Export Button Engagement
                st.download_button(
                    label="📥 Download Filtered & Optimized Asset",
                    data=img_buffer.getvalue(),
                    file_name=f"processed_studio_asset.{save_format.lower()}",
                    mime=f"image/{save_format.lower()}"
                )

        except Exception as global_studio_error:
            st.error(f"Critical Studio System Intercept: {str(global_studio_error)}")
            
    else:
        st.info("💡 Standby Validation Loop: Please drop an engineering image file into the sidebar to spin up the canvas canvas workspace.")


# =====================================================================
# MODE B: UNIVERSAL QR ENGINE
# =====================================================================
elif workspace_mode == "🔮 Universal QR Engine":
    st.title("🔮 Universal QR Engine")
    st.write("Generate standardized high-capacity QR Code symbologies with isolated data pipeline rules.")

    # Design Overrides Styling Panel
    st.sidebar.header("🎨 Matrix Design Tokens")
    dark_color = st.sidebar.color_picker("Line Color (Dark Modules)", "#000000")
    light_color = st.sidebar.color_picker("Canvas Color (Light Modules)", "#FFFFFF")
    scale_factor = st.sidebar.slider("QR Scale Density Factor", min_value=1, max_value=20, value=10)

    # Architectural Pipeline Tabs
    text_tab, link_tab, base64_tab = st.tabs([
        "🔤 Text to QR Pipeline", 
        "🔗 Link to QR Pipeline", 
        "🖼️ Image to QR Pipeline"
    ])

    qr_payload = None
    pipeline_active = False

    # --- PIPELINE 1: TEXT TO QR ---
    with text_tab:
        st.subheader("Literal Text Processing Grid")
        text_input = st.text_area(
            "Raw Paragraph Input String", 
            placeholder="Type structured raw text intended for display standard viewscreen output...",
            key="text_input_area"
        )
        if text_input:
            qr_payload = text_input
            pipeline_active = True

    # --- PIPELINE 2: LINK TO QR ---
    with link_tab:
        st.subheader("Absolute URL Absolute Redirect")
        url_input = st.text_input(
            "Target Web Address (URI)", 
            placeholder="https://example-production-domain.com",
            key="url_input_field"
        )
        if url_input:
            if not url_input.startswith(("http://", "https://")):
                st.warning("⚠️ Formatting Warning: Target URI should contain absolute web headers (http:// or https://).")
            qr_payload = url_input
            pipeline_active = True

    # --- PIPELINE 3: IMAGE TO QR ---
    with base64_tab:
        st.subheader("Image Conversion Payload Matrix")
        st.caption("Converts a source graphic down to binary Base64 Data URI blocks injected directly inside QR capacity storage limits.")
        
        qr_image_file = st.file_uploader(
            "Upload Target Frame Matrix Asset", 
            type=["png", "jpg", "jpeg"], 
            key="qr_image_uploader"
        )
        
        if qr_image_file is not None:
            try:
                # Execution shield for processing optimization metrics
                img_bytes = qr_image_file.read()
                if len(img_bytes) > 20000:
                    st.warning("⚠️ Capacity Warning: File size exceeds typical high-capacity QR bounds. Scan resolution might decay drastically.")
                
                base64_encoded = base64.b64encode(img_bytes).decode('utf-8')
                mime_type = f"image/{qr_image_file.type.split('/')[-1]}"
                data_uri = f"data:{mime_type};base64,{base64_encoded}"
                
                qr_payload = data_uri
                pipeline_active = True
                st.success("Successfully generated structured asset Base64 data string payload.")
            except Exception as b64_error:
                st.error(f"Base64 Dynamic Generation Intercept Failure: {str(b64_error)}")

    # --- ENGINE MATRIX GENERATION AND RENDERING ---
    st.markdown("---")
    st.subheader("Matrix Construction Layout Display")

    if pipeline_active and qr_payload:
        try:
            # Shielded QR compiling logic blocks via Segno 
            # Micro-calculation fallback override checking payload limits
            qr_matrix = segno.make(qr_payload, error='M')
            
            # Export via buffer engine
            qr_buffer = io.BytesIO()
            qr_matrix.save(
                qr_buffer, 
                kind='png', 
                scale=scale_factor, 
                dark=dark_color, 
                light=light_color
            )
            
            # Render layout output UI
            out_col1, out_col2 = st.columns([1, 2])
            with out_col1:
                st.image(qr_buffer.getvalue(), caption="Compiled Production QR Output Canvas", use_container_width=True)
            
            with out_col2:
                st.markdown("### 🗃️ Symbology Deployment Logistics")
                st.text_area("Encoded Internal Target Payload", value=qr_payload, height=150, disabled=True)
                
                # Download Action Output Block
                st.download_button(
                    label="📥 Download Compiled QR Matrix Output",
                    data=qr_buffer.getvalue(),
                    file_name="universal_qr_matrix.png",
                    mime="image/png"
                )
                
        except segno.DataOverflowError:
            st.error("🚨 Matrix Structural Crash: Input payload block size scales wider than maximum limits for standard High-Capacity QR version arrays.")
        except Exception as qr_engine_error:
            st.error(f"Isolated Matrix Construction Runtime Fault: {str(qr_engine_error)}")
    else:
        st.info("💡 Standby Matrix Monitor: Awaiting structural validation metrics across one of the active input pipelines above.")
