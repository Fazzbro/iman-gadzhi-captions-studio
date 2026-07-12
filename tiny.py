import sys
import asyncio

# 1. WINDOWS SELECTOR EVENT LOOP POLICY FIX (Required at top-level)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import gradio as gr
import whisper_timestamped as whisper
from moviepy import VideoFileClip, AudioFileClip, ColorClip, TextClip, CompositeVideoClip, ImageClip
import numpy as np
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

def get_spring_scale(t, duration=0.25):
    """Kinetic zoom bounce starting at 75%, overshooting to ~115%, settling at 100%."""
    if t >= duration:
        return 1.0
    p = max(0.0, min(1.0, t / duration))
    return 1.0 - 0.25 * ((1.0 - p) ** 3) + 1.5 * p * ((1.0 - p) ** 2)

def get_entry_tilt(t, duration=0.25, start_angle=-2.8):
    """Rotational tilt overshoot starting around -3 degrees and settling smoothly at 0 degrees."""
    if t >= duration:
        return 0.0
    p = max(0.0, min(1.0, t / duration))
    return start_angle * ((1.0 - p) ** 2)

def apply_wipe_filter(clip, duration=0.3, feather_width=35):
    """Applies a smooth quadratic wipe transition from left to right with horizontal alpha feathering."""
    def fl_filter(get_frame, t):
        frame = get_frame(t)
        progress = min(t / duration, 1.0)
        progress = 1 - (1 - progress) ** 2  # Quadratic ease out
        w = frame.shape[1]
        current_w = int(w * progress)
        new_frame = np.copy(frame)
        if current_w < w:
            feather_start = max(0, current_w - feather_width)
            if feather_start < current_w:
                ramp = np.linspace(1.0, 0.0, current_w - feather_start)
                if new_frame.ndim == 3:
                    for c in range(new_frame.shape[2]):
                        new_frame[:, feather_start:current_w, c] = (new_frame[:, feather_start:current_w, c] * ramp).astype(new_frame.dtype)
                else:
                    new_frame[:, feather_start:current_w] = (new_frame[:, feather_start:current_w] * ramp).astype(new_frame.dtype)
            if new_frame.ndim == 2:
                new_frame[:, current_w:] = 0
            else:
                new_frame[:, current_w:, :] = 0
        return new_frame
    
    new_clip = clip.transform(fl_filter)
    if clip.mask:
        new_clip.mask = clip.mask.transform(fl_filter)
    return new_clip

def make_gradient_text(text, font, font_size, color_top, color_mid, color_bottom, margin_x=20, margin_y=50):
    """Generates text filled with a smooth 3-stop (top-mid-bottom) RGB gradient."""
    base = TextClip(text=text, font=font, font_size=font_size, color='white', margin=(margin_x, margin_y))
    mask = base.mask.get_frame(0)
    h, w = mask.shape
    grad = np.zeros((h, w, 3), dtype=np.uint8)
    
    for y in range(h):
        effective_y = y - margin_y
        effective_h = max(h - (margin_y * 2), 1)
        ratio = max(0.0, min(1.0, effective_y / effective_h))
        
        if ratio <= 0.5:
            sub_ratio = ratio * 2.0
            smooth = 0.5 - 0.5 * np.cos(sub_ratio * np.pi)
            r = int(color_top[0] * (1 - smooth) + color_mid[0] * smooth)
            g = int(color_top[1] * (1 - smooth) + color_mid[1] * smooth)
            b = int(color_top[2] * (1 - smooth) + color_mid[2] * smooth)
        else:
            sub_ratio = (ratio - 0.5) * 2.0
            smooth = 0.5 - 0.5 * np.cos(sub_ratio * np.pi)
            r = int(color_mid[0] * (1 - smooth) + color_bottom[0] * smooth)
            g = int(color_mid[1] * (1 - smooth) + color_bottom[1] * smooth)
            b = int(color_mid[2] * (1 - smooth) + color_bottom[2] * smooth)
            
        grad[y, :, :] = [r, g, b]
        
    try:
        mask_clip = ImageClip(mask, is_mask=True)
    except TypeError:
        mask_clip = ImageClip(mask, ismask=True)
        
    return ImageClip(grad).with_mask(mask_clip)

def get_solid_3d_extrusion(text, font, font_size, hex_color, depth=9, margin_x=20, margin_y=50):
    """Generates stacked, progressively darkened layers to build a punchy 3D block shadow with faster render times."""
    layers = []
    h_c = hex_color.lstrip('#')
    r, g, b = tuple(int(h_c[i:i+2], 16) for i in (0, 2, 4))
    
    for i in range(depth, 0, -1):
        darken = max(0.15, 1.0 - (i / depth) * 0.75)  # Steeper darkening on lower layers for punchy depth
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
        anim_dur = min(0.25, chunk_duration)
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
    audio_path,
    audio_aspect_ratio,
    font_file, 
    font_size, 
    show_shadow, 
    t1_top_hex, 
    t1_mid_hex, 
    t1_bot_hex, 
    t2_top_hex, 
    t2_mid_hex, 
    t2_bot_hex, 
    progress=gr.Progress()
):
    has_video = video_path is not None and os.path.exists(str(video_path))
    has_audio = audio_path is not None and os.path.exists(str(audio_path))
    
    if not has_video and not has_audio:
        raise gr.Error("Please upload either a Source Video (Option A) OR an Audio file (Option B)!")
        
    progress(0.1, desc="Loading Media & Extracting Audio Track...")
    print("\n[AI Studio] Step 1: Loading media track...", flush=True)
    
    temp_audio = "temp_gui_audio.wav"
    
    if has_video:
        print("[AI Studio] Mode: Video Input detected. Extracting audio...", flush=True)
        media_clip = VideoFileClip(video_path)
        if media_clip.audio is None:
            media_clip.close()
            raise gr.Error("The uploaded video has no audio channel! Audio is required for transcription.")
        canvas_w, canvas_h = media_clip.w, media_clip.h
        duration = media_clip.duration
        audio_clip = media_clip.audio
        try:
            audio_clip.write_audiofile(temp_audio, logger=None)
        except Exception as e:
            media_clip.close()
            raise gr.Error(f"Failed to extract audio from video: {e}")
    else:
        print("[AI Studio] Mode: Direct Audio File Input detected...", flush=True)
        try:
            audio_clip = AudioFileClip(audio_path)
        except Exception as e:
            raise gr.Error(f"Failed to load audio file: {e}")
            
        media_clip = audio_clip
        duration = audio_clip.duration
        try:
            audio_clip.write_audiofile(temp_audio, logger=None)
        except Exception as e:
            audio_clip.close()
            raise gr.Error(f"Failed to convert audio: {e}")
            
        # Determine canvas size from aspect ratio selection
        if audio_aspect_ratio and "16:9" in audio_aspect_ratio:
            canvas_w, canvas_h = 1920, 1080
        elif audio_aspect_ratio and "1:1" in audio_aspect_ratio:
            canvas_w, canvas_h = 1080, 1080
        else:
            canvas_w, canvas_h = 1080, 1920
            
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
        media_clip.close()
        raise gr.Error("No speech detected in the media. Please verify the audio level and try again.")
        
    progress(0.3, desc="Building Canvas & Typography Elements...")
    print("[AI Studio] Step 3: Preparing layers and formatting typography...", flush=True)
    
    # Create a solid green screen backdrop (#00FF00) for chroma keying in video editors
    green_bg = ColorClip(size=(canvas_w, canvas_h), color=(0, 255, 0), duration=duration)
    video_layers = [green_bg]
    
    # Select font: custom, workspace fallback, or system fallback
    if font_file and os.path.exists(font_file):
        FONT = font_file
    elif os.path.exists("Poppins-Bold.ttf"):
        FONT = "Poppins-Bold.ttf"
    else:
        FONT = "Impact"
        
    FONT_SIZE = int(font_size)
    BASE_Y = int(canvas_h * 0.6)  # Set captions in the lower third
    
    T1_TOP = hex_to_rgb(t1_top_hex)
    T1_MID = hex_to_rgb(t1_mid_hex)
    T1_BOT = hex_to_rgb(t1_bot_hex)
    T1_3D = "#3D1400"
    
    T2_TOP = hex_to_rgb(t2_top_hex)
    T2_MID = hex_to_rgb(t2_mid_hex)
    T2_BOT = hex_to_rgb(t2_bot_hex)
    T2_3D = "#222225"
    
    def format_caption_text(s):
        s = s.strip()
        if not s:
            return ""
        return s[0].upper() + s[1:]
    
    progress(0.4, desc="Compositing Graphic & Animation Layers...")
    
    for segment in segments:
        words_list = segment.get("words", [])
        if not words_list:
            continue
            
        for i in range(0, len(words_list), 4):
            chunk = words_list[i:i+4]
            start_time = chunk[0]["start"]
            end_time = chunk[-1]["end"]
            chunk_duration = end_time - start_time
            if chunk_duration <= 0:
                chunk_duration = 0.1
                
            if len(chunk) <= 2:
                word1_text = format_caption_text(chunk[0]["text"])
                word2_text = format_caption_text(chunk[1]["text"]) if len(chunk) > 1 else ""
            else:
                mid_idx = (len(chunk) + 1) // 2
                word1_text = format_caption_text(" ".join(w["text"].strip() for w in chunk[:mid_idx]))
                word2_text = format_caption_text(" ".join(w["text"].strip() for w in chunk[mid_idx:]))
            
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
            
            max_line_w = max(w1, w2)
            max_allowed_w = int(canvas_w * 0.9)
            
            if max_line_w > max_allowed_w:
                scale_factor = max_allowed_w / max_line_w
                chunk_font_size = int(chunk_font_size * scale_factor)
                margin_x = int(20 * scale_factor)
                margin_y = int(50 * scale_factor)
                try:
                    w1 = TextClip(text=word1_text, font=FONT, font_size=chunk_font_size, margin=(margin_x, margin_y)).size[0]
                    w2 = TextClip(text=word2_text, font=FONT, font_size=chunk_font_size, margin=(margin_x, margin_y)).size[0] if word2_text else 0
                except Exception as e:
                    print(f"[Warning] Dynamic resizing calculation failed: {e}", flush=True)
            
            start_x_t1 = (canvas_w - w1) // 2
            start_x_t2 = (canvas_w - w2) // 2
            
            if word2_text:
                base_y_t1 = BASE_Y - int(chunk_font_size * 0.52)
                base_y_t2 = BASE_Y + int(chunk_font_size * 0.42)
            else:
                base_y_t1 = BASE_Y
                base_y_t2 = BASE_Y
            
            wipe_dur = min(0.35, chunk_duration * 0.8)
            travel_dist = int(chunk_font_size * 1.1)
            
            # --- LINE 1 (Top Line: Orange Gradient + Soft Feathered Wipe + 3D Shadow) ---
            if show_shadow:
                t1_3d_layers = get_solid_3d_extrusion(word1_text, FONT, chunk_font_size, T1_3D, depth=9, margin_x=margin_x, margin_y=margin_y)
                for clip, ox, oy in t1_3d_layers:
                    c = apply_wipe_filter(clip, duration=wipe_dur, feather_width=35).with_start(start_time).with_end(end_time).with_position((start_x_t1 + ox, base_y_t1 + oy))
                    video_layers.append(c)
                    
            t1_core = make_gradient_text(word1_text, FONT, chunk_font_size, T1_TOP, T1_MID, T1_BOT, margin_x=margin_x, margin_y=margin_y)
            t1_core = apply_wipe_filter(t1_core, duration=wipe_dur, feather_width=35).with_start(start_time).with_end(end_time).with_position((start_x_t1, base_y_t1))
            video_layers.append(t1_core)
            
            # --- LINE 2 (Bottom Line: Crisp White + Pop-in Rise + Kinetic Zoom Bounce + Rotational Tilt) ---
            if word2_text:
                rise_anim_core = make_rise_anim(start_x_t2, base_y_t2, chunk_duration, travel_dist, offset_x=0, offset_y=0)
                
                if show_shadow:
                    t2_3d_layers = get_solid_3d_extrusion(word2_text, FONT, chunk_font_size, T2_3D, depth=9, margin_x=margin_x, margin_y=margin_y)
                    for clip, ox, oy in t2_3d_layers:
                        c = clip.resized(lambda t: get_spring_scale(t)).rotated(lambda t: get_entry_tilt(t), expand=True)
                        t2_3d_anim = make_rise_anim(start_x_t2, base_y_t2, chunk_duration, travel_dist, offset_x=ox, offset_y=oy)
                        c = c.with_start(start_time).with_end(end_time).with_position(t2_3d_anim)
                        video_layers.append(c)
                        
                t2_core = make_gradient_text(word2_text, FONT, chunk_font_size, T2_TOP, T2_MID, T2_BOT, margin_x=margin_x, margin_y=margin_y)
                t2_core = t2_core.resized(lambda t: get_spring_scale(t)).rotated(lambda t: get_entry_tilt(t), expand=True)
                t2_core = t2_core.with_start(start_time).with_end(end_time).with_position(rise_anim_core)
                video_layers.append(t2_core)
                
    progress(0.8, desc="Compositing Canvas & Exporting Video...")
    output_path = "gui_output_captions.mp4"
    print(f"[AI Studio] Step 4: Exporting final video composited structure to '{output_path}'...", flush=True)
    
    final_video = CompositeVideoClip(video_layers).with_audio(audio_clip)
    
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
    media_clip.close()
    
    print(f"\n[AI Studio] SUCCESS! Rendered video output written to '{output_path}'!", flush=True)
    progress(1.0, desc="Done!")
    return output_path


# ==========================================
# 4. CUSTOM NEUMORPHIC INTERFACE LAYOUT & CSS
# ==========================================

custom_css = """
/* Studio Dark Theme Reset */
body, .gradio-container {
    background-color: #0B0D10 !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif !important;
}

/* Header Navbar Bar */
.studio-header {
    background: linear-gradient(180deg, #161A22 0%, #11141A 100%);
    border-bottom: 1px solid #232834;
    padding: 20px 32px;
    margin-bottom: 24px;
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

/* Studio Panels & Cards */
.studio-panel {
    background: #14171F !important;
    border: 1px solid #232834 !important;
    border-radius: 12px !important;
    padding: 24px !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5) !important;
}

/* Tabs styling */
.gradio-tabs {
    background: transparent !important;
}
.gradio-tabs button {
    font-weight: 600 !important;
    color: #94A3B8 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
}
.gradio-tabs button.selected {
    color: #FF5A36 !important;
    border-bottom: 2px solid #FF5A36 !important;
    background: #191D28 !important;
}

/* Input Fields & Upload Boxes */
.studio-input input, .studio-input textarea, .studio-input select, .studio-input div[class*="upload"] {
    background-color: #0E1017 !important;
    border: 1px solid #232834 !important;
    border-radius: 8px !important;
    color: #F8FAFC !important;
    transition: border-color 0.2s ease !important;
}
.studio-input input:focus, .studio-input textarea:focus {
    border-color: #FF5A36 !important;
    outline: none !important;
}

/* Color Pickers */
.color-box {
    background: #191D28 !important;
    border: 1px solid #2A303F !important;
    border-radius: 8px !important;
    padding: 14px !important;
    margin-bottom: 12px !important;
}

/* Action Button (Broadcast Studio Red/Orange) */
button.primary-btn {
    background: linear-gradient(135deg, #FF5A36 0%, #FF2E00 100%) !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    border: 1px solid #FF7456 !important;
    box-shadow: 0 4px 15px rgba(255, 46, 0, 0.4) !important;
    padding: 16px 24px !important;
    cursor: pointer !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    margin-top: 16px !important;
}
button.primary-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(255, 46, 0, 0.6) !important;
    background: linear-gradient(135deg, #FF6A48 0%, #FF3E14 100%) !important;
}

/* Checkboxes */
.studio-checkbox input[type="checkbox"] {
    accent-color: #FF5A36 !important;
}
.studio-checkbox label span {
    color: #E2E8F0 !important;
    font-weight: 500 !important;
}
"""

with gr.Blocks(title="Iman Gadzhi Studio Captions Pro", css=custom_css) as app:
    # Studio Top Navbar
    gr.HTML("""
    <div class="studio-header">
        <div>
            <h1 style="color: #FFFFFF; font-weight: 800; font-size: 1.6rem; margin: 0; display: inline-flex; align-items: center; gap: 10px;">
                <span style="background: #FF5A36; padding: 4px 10px; border-radius: 6px; font-size: 1rem; font-weight: 900; color: #000;">REC</span>
                IMAN GADZHI <span style="color: #94A3B8; font-weight: 400; font-size: 1.2rem;">| STUDIO CAPTIONS PRO</span>
            </h1>
        </div>
        <div style="display: flex; gap: 12px; align-items: center;">
            <span style="background: rgba(0, 255, 0, 0.15); color: #00FF66; border: 1px solid #00FF66; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">🟢 CHROMA KEY GREEN SCREEN</span>
            <span style="background: #232834; color: #CBD5E1; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; font-family: monospace;">v2.5 PRO</span>
        </div>
    </div>
    """)
    
    with gr.Row(equal_height=False):
        # Left Panel: Controls & Settings
        with gr.Column(scale=6, elem_classes=["studio-panel"]):
            gr.HTML("<h3 style='color: #F8FAFC; font-weight: 700; font-size: 1.1rem; margin-top: 0; margin-bottom: 12px; border-bottom: 1px solid #232834; padding-bottom: 10px;'>⚡ STUDIO CONFIGURATION</h3>")
            
            with gr.Tabs():
                with gr.TabItem("📁 1. Media & Typography"):
                    gr.HTML("<p style='color: #94A3B8; font-size: 0.85rem; margin-bottom: 12px;'>Upload EITHER a Source Video (Option A) OR an Audio File (.mp3/.wav/.m4a) if your video file is too large!</p>")
                    input_video = gr.Video(label="Option A: Upload Source Video (Auto-detects Resolution)", sources=["upload"], elem_classes=["studio-input"])
                    input_audio = gr.Audio(label="Option B: Upload Audio File (Fast for Huge Videos)", sources=["upload"], type="filepath", elem_classes=["studio-input"])
                    audio_aspect = gr.Dropdown(
                        label="Green Screen Aspect Ratio (Required for Option B Audio Uploads)", 
                        choices=["9:16 Vertical Shorts (1080x1920)", "16:9 Horizontal Landscape (1920x1080)", "1:1 Square (1080x1080)"], 
                        value="9:16 Vertical Shorts (1080x1920)",
                        elem_classes=["studio-input"]
                    )
                    with gr.Row():
                        font_upload = gr.File(label="Custom Typography Font (.ttf/.otf)", file_types=[".ttf", ".otf"], type="filepath", elem_classes=["studio-input"])
                        font_size_slider = gr.Slider(minimum=80, maximum=200, value=145, step=5, label="Typography Font Scale (px)", elem_classes=["studio-input"])
                        
                with gr.TabItem("🎨 2. 3-Stop Color Palettes"):
                    gr.HTML("<p style='color: #94A3B8; font-size: 0.85rem; margin-bottom: 12px;'>Configure 3-stop (Top ➔ Middle ➔ Bottom) RGB gradients for dual-word kinetic animation.</p>")
                    with gr.Group(elem_classes=["color-box"]):
                        gr.HTML("<div style='color: #FF7300; font-weight: 600; font-size: 0.9rem; margin-bottom: 8px;'>🔥 Top Line Palette (Orange Gradient)</div>")
                        with gr.Row():
                            t1_top = gr.ColorPicker(label="Top Stop", value="#FFBD59")
                            t1_mid = gr.ColorPicker(label="Middle Stop", value="#FF7300")
                            t1_bot = gr.ColorPicker(label="Bottom Stop", value="#E53900")
                            
                    with gr.Group(elem_classes=["color-box"]):
                        gr.HTML("<div style='color: #F8FAFC; font-weight: 600; font-size: 0.9rem; margin-bottom: 8px;'>💬 Bottom Line Palette (Studio White)</div>")
                        with gr.Row():
                            t2_top = gr.ColorPicker(label="Top Stop", value="#FFFFFF")
                            t2_mid = gr.ColorPicker(label="Middle Stop", value="#FFFFFF")
                            t2_bot = gr.ColorPicker(label="Bottom Stop", value="#E2E8F0")
                            
                with gr.TabItem("✨ 3. VFX & Rendering Engine"):
                    gr.HTML("<p style='color: #94A3B8; font-size: 0.85rem; margin-bottom: 12px;'>Hardware acceleration and kinetic extrusion settings.</p>")
                    show_shadow = gr.Checkbox(label="🧊 Render 3D Extruded Block Shadow (Punchy 9-Layer Depth)", value=True, elem_classes=["studio-checkbox"])
                    
            render_btn = gr.Button("✨ RENDER STUDIO CAPTIONS", elem_classes=["primary-btn"])
            
        # Right Panel: Broadcast Output Monitor
        with gr.Column(scale=6, elem_classes=["studio-panel"]):
            gr.HTML("""
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #232834; padding-bottom: 10px; margin-bottom: 14px;">
                <h3 style="color: #F8FAFC; font-weight: 700; font-size: 1.1rem; margin: 0;">📺 BROADCAST PREVIEW MONITOR</h3>
                <span style="color: #64748B; font-size: 0.8rem; font-family: monospace;">COLORSPACE: RGB #00FF00</span>
            </div>
            """)
            output_video = gr.Video(label="Chroma Key Green Screen Output", interactive=False, elem_classes=["studio-input"])
            
            gr.HTML("""
            <div style="background: #1A1E29; border: 1px solid #283042; border-radius: 8px; padding: 16px; margin-top: 16px;">
                <div style="color: #FF5A36; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">💡 Editor Workflow Guide</div>
                <ol style="color: #CBD5E1; font-size: 0.85rem; margin: 0; padding-left: 18px; line-height: 1.6;">
                    <li>Place original video on <b>Track 1</b> and this output on <b>Track 2</b>.</li>
                    <li>Align using the preserved timeline audio waveforms.</li>
                    <li>Apply <b>Ultra Key / Chroma Key</b> effect to Track 2 and sample the <font color="#00FF66"><b>#00FF00</b></font> green background.</li>
                </ol>
            </div>
            """)
            
    render_btn.click(
        fn=render_video_gui,
        inputs=[
            input_video, 
            input_audio,
            audio_aspect,
            font_upload, 
            font_size_slider, 
            show_shadow, 
            t1_top, 
            t1_mid, 
            t1_bot, 
            t2_top, 
            t2_mid, 
            t2_bot
        ],
        outputs=[output_video]
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)