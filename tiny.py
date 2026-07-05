import sys
import asyncio

# 1. WINDOWS SELECTOR EVENT LOOP POLICY FIX (Required at top-level)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import gradio as gr
import whisper_timestamped as whisper
from moviepy import VideoFileClip, ColorClip, TextClip, CompositeVideoClip, ImageClip
import numpy as np
from scipy.ndimage import gaussian_filter
import torch
import os

# ==========================================
# 2. STUDIO-GRADE GRAPHICS & ANIMATION ENGINE
# ==========================================

def ease_out_back(progress):
    """Easing function for organic bounce effect."""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * ((progress - 1) ** 3) + c1 * ((progress - 1) ** 2)

def apply_wipe_filter(clip, duration=0.3):
    """Applies a smooth quadratic wipe transition from left to right."""
    def fl_filter(get_frame, t):
        frame = get_frame(t)
        progress = min(t / duration, 1.0)
        progress = 1 - (1 - progress) ** 2  # Quadratic ease out
        w = frame.shape[1]
        current_w = int(w * progress)
        new_frame = np.copy(frame)
        if current_w < w:
            if new_frame.ndim == 2:
                new_frame[:, current_w:] = 0
            else:
                new_frame[:, current_w:, :] = 0
        return new_frame
    
    new_clip = clip.transform(fl_filter)
    if clip.mask:
        new_clip.mask = clip.mask.transform(fl_filter)
    return new_clip

def make_gradient_text(text, font, font_size, color_top, color_bottom, margin_x=20, margin_y=50):
    """Generates text filled with a smooth top-to-bottom RGB gradient."""
    base = TextClip(text=text, font=font, font_size=font_size, color='white', margin=(margin_x, margin_y))
    mask = base.mask.get_frame(0)
    h, w = mask.shape
    grad = np.zeros((h, w, 3), dtype=np.uint8)
    
    for y in range(h):
        effective_y = y - margin_y
        effective_h = max(h - (margin_y * 2), 1)
        ratio = max(0.0, min(1.0, effective_y / effective_h))
        ratio = 0.5 - 0.5 * np.cos(ratio * np.pi)  # Smooth cosine interpolation
        
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        grad[y, :, :] = [r, g, b]
        
    try:
        mask_clip = ImageClip(mask, is_mask=True)
    except TypeError:
        mask_clip = ImageClip(mask, ismask=True)
        
    return ImageClip(grad).with_mask(mask_clip)

def make_true_glow(text, font, font_size, glow_color_rgb, blur_radius=25, opacity=0.85, margin_x=20, margin_y=50):
    """Generates a blurred neon glow backdrop by applying a Gaussian filter to text outline."""
    base = TextClip(text=text, font=font, font_size=font_size, color='white', stroke_color='white', stroke_width=12, margin=(margin_x, margin_y))
    mask = base.mask.get_frame(0)
    
    # Pad mask to prevent edge clipping during blur operation
    pad = int(blur_radius * 2.5)
    padded_mask = np.pad(mask, pad, mode='constant', constant_values=0)
    blurred_mask = gaussian_filter(padded_mask, sigma=blur_radius)
    
    max_val = np.max(blurred_mask)
    if max_val > 0:
        blurred_mask = (blurred_mask / max_val) * opacity
        
    h, w = blurred_mask.shape
    glow_rgb = np.zeros((h, w, 3), dtype=np.uint8)
    glow_rgb[:, :] = glow_color_rgb
    
    try:
        mask_clip = ImageClip(blurred_mask, is_mask=True)
    except TypeError:
        mask_clip = ImageClip(blurred_mask, ismask=True)
        
    return ImageClip(glow_rgb).with_mask(mask_clip), pad

def get_solid_3d_extrusion(text, font, font_size, hex_color, depth=12, margin_x=20, margin_y=50):
    """Generates stacked, progressively darkened layers to build a clean 3D block shadow."""
    layers = []
    h_c = hex_color.lstrip('#')
    r, g, b = tuple(int(h_c[i:i+2], 16) for i in (0, 2, 4))
    
    for i in range(depth, 0, -1):
        darken = 1.0 - (i / depth) * 0.6  # Darken lower layers for depth shading
        c = f"#{int(r*darken):02x}{int(g*darken):02x}{int(b*darken):02x}"
        t = TextClip(text=text, font=font, font_size=font_size, color=c, margin=(margin_x, margin_y))
        layers.append((t, i, i))
    return layers

def hex_to_rgb(hex_color):
    """Translates hex string representations to RGB tuples."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def make_rise_anim(base_x, base_y, chunk_duration, travel_dist, offset_x=0, offset_y=0):
    """Constructs position callback function for the pop-in rise animation."""
    def anim(t):
        anim_dur = min(0.35, chunk_duration)
        progress = min(t / anim_dur, 1.0)
        eased = ease_out_back(progress) if progress < 1.0 else 1.0
        start_y = base_y + travel_dist
        current_y = start_y - (travel_dist * eased)
        return (base_x + offset_x, current_y + offset_y)
    return anim


# ==========================================
# 3. VIDEO PROCESSING PIPELINE
# ==========================================

def render_video_gui(
    video_path, 
    font_file, 
    font_size, 
    show_shadow, 
    show_glow, 
    t1_top_hex, 
    t1_bot_hex, 
    t2_top_hex, 
    t2_bot_hex, 
    progress=gr.Progress()
):
    if not video_path:
        raise gr.Error("Please upload a video file first!")
        
    progress(0.1, desc="Extracting Audio & Initializing AI Models...")
    print("\n[AI Studio] Step 1: Loading video and extracting audio track...", flush=True)
    video = VideoFileClip(video_path)
    
    if video.audio is None:
        video.close()
        raise gr.Error("The uploaded video has no audio channel! Audio is required for transcription.")
        
    temp_audio = "temp_gui_audio.wav"
    try:
        video.audio.write_audiofile(temp_audio, logger=None)
    except Exception as e:
        video.close()
        raise gr.Error(f"Failed to extract audio from video: {e}")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[AI Studio] Step 2: Loading Whisper 'tiny' model on {device.upper()}...", flush=True)
    
    if device == "cuda":
        torch.cuda.empty_cache()
        
    model = whisper.load_model("tiny", device=device)
    
    print("[AI Studio] Executing: Speech-to-Text Transcription with word-level timestamps...", flush=True)
    result = whisper.transcribe(model, temp_audio, language="en")
    
    # Clean up AI model from memory immediately
    del model
    if device == "cuda":
        torch.cuda.empty_cache()
        
    if os.path.exists(temp_audio):
        os.remove(temp_audio)
    
    segments = result.get("segments", [])
    if not segments:
        video.close()
        raise gr.Error("No speech detected in the video. Please verify the voice audio level and try again.")
        
    progress(0.3, desc="Building Canvas & Typography Elements...")
    print("[AI Studio] Step 3: Preparing layers and formatting typography...", flush=True)
    
    # Create a solid green screen backdrop (#00FF00) for chroma keying in video editors
    green_bg = ColorClip(size=(video.w, video.h), color=(0, 255, 0), duration=video.duration)
    video_layers = [green_bg]
    
    # Select font: custom, workspace fallback, or system fallback
    if font_file and os.path.exists(font_file):
        FONT = font_file
    elif os.path.exists("Poppins-Bold.ttf"):
        FONT = "Poppins-Bold.ttf"
    else:
        FONT = "Impact"
        
    FONT_SIZE = int(font_size)
    BASE_Y = int(video.h * 0.6)  # Set captions in the lower third
    
    T1_TOP = hex_to_rgb(t1_top_hex)
    T1_BOT = hex_to_rgb(t1_bot_hex)
    T1_GLOW = T1_TOP
    T1_3D = "#333335"
    
    T2_TOP = hex_to_rgb(t2_top_hex)
    T2_BOT = hex_to_rgb(t2_bot_hex)
    T2_GLOW = T2_BOT
    T2_3D = "#4A1800"
    
    progress(0.4, desc="Compositing Graphic & Animation Layers...")
    
    for segment in segments:
        words_list = segment.get("words", [])
        if not words_list:
            continue
            
        for i in range(0, len(words_list), 2):
            chunk = words_list[i:i+2]
            start_time = chunk[0]["start"]
            end_time = chunk[-1]["end"]
            chunk_duration = end_time - start_time
            if chunk_duration <= 0:
                chunk_duration = 0.1
                
            word1_text = chunk[0]["text"].upper() + " "
            word2_text = chunk[1]["text"].upper() if len(chunk) > 1 else ""
            
            # Auto-scaling logic to prevent text overflowing the video width
            chunk_font_size = FONT_SIZE
            margin_x = 20
            margin_y = 50
            
            try:
                w1 = TextClip(text=word1_text, font=FONT, font_size=chunk_font_size, margin=(margin_x, margin_y)).size[0]
                w2 = TextClip(text=word2_text, font=FONT, font_size=chunk_font_size, margin=(margin_x, margin_y)).size[0] if word2_text else 0
            except Exception as e:
                print(f"[Warning] TextClip size check failed: {e}. Retrying with system Impact font...", flush=True)
                FONT = "Impact"
                try:
                    w1 = TextClip(text=word1_text, font=FONT, font_size=chunk_font_size, margin=(margin_x, margin_y)).size[0]
                    w2 = TextClip(text=word2_text, font=FONT, font_size=chunk_font_size, margin=(margin_x, margin_y)).size[0] if word2_text else 0
                except Exception as e2:
                    print(f"[Error] TextClip sizing failed completely: {e2}", flush=True)
                    continue
            
            total_width = w1 + w2
            max_allowed_w = int(video.w * 0.9)
            
            # Linear scaling helper if bounds are exceeded
            if total_width > max_allowed_w:
                scale_factor = max_allowed_w / total_width
                chunk_font_size = int(chunk_font_size * scale_factor)
                margin_x = int(20 * scale_factor)
                margin_y = int(50 * scale_factor)
                try:
                    w1 = TextClip(text=word1_text, font=FONT, font_size=chunk_font_size, margin=(margin_x, margin_y)).size[0]
                    w2 = TextClip(text=word2_text, font=FONT, font_size=chunk_font_size, margin=(margin_x, margin_y)).size[0] if word2_text else 0
                    total_width = w1 + w2
                except Exception as e:
                    print(f"[Warning] Dynamic resizing calculation failed: {e}", flush=True)
            
            start_x_t1 = (video.w - total_width) // 2
            start_x_t2 = start_x_t1 + w1 - int(30 * (chunk_font_size / FONT_SIZE) if FONT_SIZE > 0 else 30)
            
            wipe_dur = min(0.35, chunk_duration * 0.8)
            travel_dist = int(chunk_font_size * 1.1)
            
            # --- WORD 1 (Wipe Animation) ---
            if show_glow:
                t1_glow, t1_pad = make_true_glow(word1_text, FONT, chunk_font_size, T1_GLOW, blur_radius=20, opacity=0.4, margin_x=margin_x, margin_y=margin_y)
                t1_glow = apply_wipe_filter(t1_glow, duration=wipe_dur).with_start(start_time).with_end(end_time).with_position((start_x_t1 - t1_pad, BASE_Y - t1_pad))
                video_layers.append(t1_glow)
                
            if show_shadow:
                t1_3d_layers = get_solid_3d_extrusion(word1_text, FONT, chunk_font_size, T1_3D, depth=8, margin_x=margin_x, margin_y=margin_y)
                for clip, ox, oy in t1_3d_layers:
                    c = apply_wipe_filter(clip, duration=wipe_dur).with_start(start_time).with_end(end_time).with_position((start_x_t1 + ox, BASE_Y + oy))
                    video_layers.append(c)
                    
            t1_core = make_gradient_text(word1_text, FONT, chunk_font_size, T1_TOP, T1_BOT, margin_x=margin_x, margin_y=margin_y)
            t1_core = apply_wipe_filter(t1_core, duration=wipe_dur).with_start(start_time).with_end(end_time).with_position((start_x_t1, BASE_Y))
            video_layers.append(t1_core)
            
            # --- WORD 2 (Pop-in Rise Animation) ---
            if word2_text:
                rise_anim_core = make_rise_anim(start_x_t2, BASE_Y, chunk_duration, travel_dist, offset_x=0, offset_y=0)
                
                if show_glow:
                    t2_glow, t2_pad = make_true_glow(word2_text, FONT, chunk_font_size, T2_GLOW, blur_radius=35, opacity=0.9, margin_x=margin_x, margin_y=margin_y)
                    t2_glow_anim = make_rise_anim(start_x_t2, BASE_Y, chunk_duration, travel_dist, offset_x=-t2_pad, offset_y=-t2_pad)
                    t2_glow = t2_glow.with_start(start_time).with_end(end_time).with_position(t2_glow_anim)
                    video_layers.append(t2_glow)
                    
                if show_shadow:
                    t2_3d_layers = get_solid_3d_extrusion(word2_text, FONT, chunk_font_size, T2_3D, depth=14, margin_x=margin_x, margin_y=margin_y)
                    for clip, ox, oy in t2_3d_layers:
                        t2_3d_anim = make_rise_anim(start_x_t2, BASE_Y, chunk_duration, travel_dist, offset_x=ox, offset_y=oy)
                        c = clip.with_start(start_time).with_end(end_time).with_position(t2_3d_anim)
                        video_layers.append(c)
                        
                t2_core = make_gradient_text(word2_text, FONT, chunk_font_size, T2_TOP, T2_BOT, margin_x=margin_x, margin_y=margin_y)
                t2_core = t2_core.with_start(start_time).with_end(end_time).with_position(rise_anim_core)
                video_layers.append(t2_core)
                
    progress(0.8, desc="Compositing Canvas & Exporting Video...")
    output_path = "gui_output_captions.mp4"
    print(f"[AI Studio] Step 4: Exporting final video composited structure to '{output_path}'...", flush=True)
    
    final_video = CompositeVideoClip(video_layers).with_audio(video.audio)
    
    # Renders with percentage progress bar printed inside terminal stdout
    final_video.write_videofile(
        output_path, 
        fps=30, 
        codec="libx264", 
        audio_codec="aac", 
        logger="bar"
    )
    
    final_video.close()
    green_bg.close()
    video.close()
    
    print(f"\n[AI Studio] SUCCESS! Rendered video output written to '{output_path}'!", flush=True)
    progress(1.0, desc="Done!")
    return output_path


# ==========================================
# 4. CUSTOM NEUMORPHIC INTERFACE LAYOUT & CSS
# ==========================================

custom_css = """
body, .gradio-container {
    background-color: #ECEFF1 !important;
    font-family: 'Outfit', 'Inter', sans-serif !important;
}

/* Raised Embossed soft UI container */
.neumorphic-card {
    background: #ECEFF1 !important;
    border-radius: 24px !important;
    box-shadow: 9px 9px 18px #CFD8DC, -9px -9px 18px #FFFFFF !important;
    border: none !important;
    padding: 24px !important;
    margin-bottom: 24px !important;
}

/* Sleek obsidian neumorphic container */
.dark-obsidian-card {
    background: #1C1F26 !important;
    color: #FFFFFF !important;
    box-shadow: 10px 10px 20px #0F1115, -10px -10px 20px #292D37 !important;
    border-radius: 24px !important;
    padding: 24px !important;
    border: none !important;
    margin-bottom: 24px !important;
}

.dark-obsidian-card * {
    color: #FFFFFF !important;
}
.dark-obsidian-card span, .dark-obsidian-card p, .dark-obsidian-card h1, .dark-obsidian-card h2, .dark-obsidian-card h3 {
    color: #FFFFFF !important;
}

/* Primary Button (Sunset Cyberpunk Gradient) */
button.primary-btn {
    background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%) !important;
    border-radius: 50px !important;
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
    box-shadow: 0 10px 20px -5px rgba(255, 75, 43, 0.5), 6px 6px 12px #CFD8DC, -6px -6px 12px #FFFFFF !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    padding: 14px 28px !important;
    cursor: pointer !important;
    font-size: 1.1rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

button.primary-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 24px -5px rgba(255, 75, 43, 0.6), 4px 4px 8px #CFD8DC, -4px -4px 8px #FFFFFF !important;
}

button.primary-btn:active {
    transform: translateY(1px) !important;
}

/* Inset dual shadows for input fields & upload panels */
.neumorphic-input input, 
.neumorphic-input textarea, 
.neumorphic-input select,
.neumorphic-input div[class*="upload"],
.neumorphic-input div[class*="box"],
.neumorphic-input .file-preview,
.neumorphic-input .upload-button {
    box-shadow: inset 4px 4px 8px #CFD8DC, inset -4px -4px 8px #FFFFFF !important;
    border: none !important;
    background-color: #ECEFF1 !important;
    border-radius: 12px !important;
    color: #37474F !important;
}

/* Sliders layout color override */
.neumorphic-slider input[type="range"] {
    accent-color: #FF4B2B !important;
}

/* Toggles & Checkbox Accent styling */
.neumorphic-checkbox input[type="checkbox"] {
    accent-color: #FF4B2B !important;
}
.neumorphic-checkbox label span {
    color: #37474F !important;
    font-weight: 600 !important;
}

/* Internal palette sub-group */
.style-group {
    background: #ECEFF1 !important;
    border-radius: 18px !important;
    padding: 16px !important;
    margin-top: 15px !important;
    margin-bottom: 15px !important;
    box-shadow: inset 4px 4px 8px #CFD8DC, inset -4px -4px 8px #FFFFFF !important;
    border: none !important;
}
"""

with gr.Blocks(title="Iman Gadzhi Studio Captions", css=custom_css) as app:
    
    # Premium Header Block
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 30px; padding: 10px;">
        <h1 style="background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; font-size: 2.8rem; margin: 0; letter-spacing: -1px;">🎬 IMAN GADZHI</h1>
        <h2 style="color: #37474F; font-weight: 800; font-size: 1.8rem; margin: 5px 0 0 0; text-transform: uppercase; letter-spacing: 2px;">AI Studio Captions</h2>
        <p style="color: #78909C; font-weight: 500; font-size: 1.1rem; margin: 8px 0 0 0;">Neumorphic Soft UI • 🟩 Green Screen Chroma Key Output</p>
    </div>
    """)
    
    with gr.Row():
        # Configuration Control Panel
        with gr.Column(scale=1, elem_classes=["neumorphic-card"]):
            gr.HTML("<h3 style='color: #263238; font-weight: 800; border-bottom: 2px solid #CFD8DC; padding-bottom: 8px; margin-bottom: 15px;'>⚙️ CONFIGURATION PANEL</h3>")
            
            input_video = gr.Video(label="Upload Media (English Speech)", sources=["upload"], elem_classes=["neumorphic-input"])
            font_upload = gr.File(label="Upload Typography Font (.ttf / .otf)", file_types=[".ttf", ".otf"], type="filepath", elem_classes=["neumorphic-input"])
            font_size_slider = gr.Slider(minimum=80, maximum=200, value=145, step=5, label="Typography Font Size", elem_classes=["neumorphic-slider"])
            
            # Speed Optimization Checkboxes
            show_shadow = gr.Checkbox(label="🧊 Render 3D Block Shadow (Extrusion)", value=True, elem_classes=["neumorphic-checkbox"])
            show_glow = gr.Checkbox(label="✨ Render Neon Background Glow", value=True, elem_classes=["neumorphic-checkbox"])
            
            # Palette Colors Sub-groups
            with gr.Group(elem_classes=["style-group"]):
                gr.HTML("<span style='color: #37474F; font-weight: 700; font-size: 0.9rem;'>🎨 Context Word Palette (Word 1)</span>")
                with gr.Row():
                    t1_top = gr.ColorPicker(label="Top Color", value="#FFFFFF", elem_classes=["neumorphic-input"])
                    t1_bot = gr.ColorPicker(label="Bottom Color", value="#BEBEC8", elem_classes=["neumorphic-input"])
                    
            with gr.Group(elem_classes=["style-group"]):
                gr.HTML("<span style='color: #37474F; font-weight: 700; font-size: 0.9rem;'>🔥 Punch Word Palette (Word 2)</span>")
                with gr.Row():
                    t2_top = gr.ColorPicker(label="Top Color", value="#FFE600", elem_classes=["neumorphic-input"])
                    t2_bot = gr.ColorPicker(label="Bottom Color", value="#FF7800", elem_classes=["neumorphic-input"])
                    
            render_btn = gr.Button("✨ Render Captions", elem_classes=["primary-btn"])
            
        # Preview Output Screen
        with gr.Column(scale=1, elem_classes=["dark-obsidian-card"]):
            gr.HTML("<h3 style='color: #FFFFFF; font-weight: 800; border-bottom: 2px solid #37474F; padding-bottom: 8px; margin-bottom: 15px;'>🟩 CHROMA KEY GREEN SCREEN PREVIEW</h3>")
            output_video = gr.Video(label="Green Screen Captions Output (Ready for Chroma Key)", interactive=False)
            
    render_btn.click(
        fn=render_video_gui,
        inputs=[
            input_video, 
            font_upload, 
            font_size_slider, 
            show_shadow, 
            show_glow, 
            t1_top, 
            t1_bot, 
            t2_top, 
            t2_bot
        ],
        outputs=[output_video]
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)