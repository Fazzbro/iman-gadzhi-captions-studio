# 🎬 Iman Gadzhi Style Captions Studio — Pro Edition (Local Studio)

<div align="center">

[![Platform](https://img.shields.io/badge/Platform-Windows%20%2F%20Mac%20%2F%20Linux-00A4EF?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Fazzbro/iman-gadzhi-captions-studio)
[![Edition](https://img.shields.io/badge/Edition-Chroma%20Key%20Green%20Screen-00FF00?style=for-the-badge&logo=adobe-premiere-pro&logoColor=black)](https://github.com/Fazzbro/iman-gadzhi-captions-studio)
[![Gradio](https://img.shields.io/badge/GUI-Gradio%20Studio%20Pro-FF4B2B?style=for-the-badge&logo=gradio&logoColor=white)](https://gradio.app/)

<br>

### 🌟 Unified Modern Studio Experience for Local Execution
Experience true studio performance with dual-word kinetic animations, custom 3-stop RGB gradients, specular gloss sheen controls, 3D extruded block shadows, live style preview canvases, and solid green screen output for video editing.

</div>

---

## ✨ Key Features

- **⚡ Asynchronous & Fast AI Processing**: Runs Whisper speech recognition and MoviePy compositing smoothly with real-time progress indicators.
- **📁 Flexible Media Dropzones (Option A & B)**: Upload your full **Source Video (Option A)** (`.mp4`, `.mov`, `.mkv`) OR upload direct **Audio Files (Option B)** (`.mp3`, `.wav`, `.m4a`) for ultra-fast processing when working with huge video files.
- **🟩 Solid Green Screen Output (`#00FF00`)**: Perfectly colored RGB green screen background optimized for 1-click Chroma Keying in Premiere Pro, CapCut, DaVinci Resolve, and Final Cut Pro (`9:16 Shorts`, `16:9 Landscape`, `1:1 Square`).
- **🎙️ Preserved Timeline Audio**: Keeps the original audio waveform intact in the exported `.mp4` for instant synchronization and alignment on your video editor timeline.
- **🔥 Iman Gadzhi Typography & VFX Engine**: Dual-word kinetic animation style (`REC` / `STUDIO CAPTIONS PRO`) with custom 3-stop (Top, Middle, Bottom) RGB color gradients, specular gloss sheen slider (`0.0` to `2.5`), and 3D extruded block shadow depth (`0` to `25` layers) with X/Y directional control.
- **🔍 Live Style Preview**: Test and sample your font, color palette, and VFX parameters instantly on a high-resolution canvas before rendering the full video.

---

## 🚀 How to Launch Locally

### 1. Install Dependencies
Ensure you have Python 3.10+ installed and install the required packages:
```powershell
pip install -r requirements.txt
```

### 2. Run the Studio Application (`tiny_local_studio.py`)
Launch the standalone Gradio web studio directly from your terminal:
```powershell
python tiny_local_studio.py
```
*(Note: Per our file preservation policy during major modifications, `tiny.py` is preserved as an unmodified original fallback while `tiny_local_studio.py` runs cleanly without any Hugging Face Spaces cloud dependencies).*

Open `http://localhost:7860` in your browser. You will see the feature-rich `v2.6 PRO LOCAL` studio interface running smoothly on your machine!

---

## 🎨 Using the Studio Interface

1. **📁 Media & Typography Tab**:
   - Upload either your **Source Video** (`Option A`) or **Audio file** (`Option B`). If using Option B, select the matching **Green Screen Aspect Ratio** (`9:16`, `16:9`, or `Square`).
   - Adjust the **Typography Font Scale** slider (`80px` to `200px`) and upload custom `.ttf`/`.otf` font files if desired.
2. **🎨 3-Stop Color Palettes Tab**:
   - Customize your **Top Line Palette (Orange Gradient)** and **Bottom Line Palette (Studio White)** across Top, Middle, and Bottom stops.
3. **✨ VFX & Shadow Engine Tab**:
   - Dial in **Specular Gloss Intensity** (`0.0` to `2.5`) for glass/metallic sheen and adjust **3D Extrusion Depth & Direction**.
4. **🔍 Live Style Preview**:
   - Click **`🔍 LIVE STYLE PREVIEW`** to generate an instant sample PNG inside the monitor canvas before rendering your video.
5. **🎬 Render & Video Editor Integration**:
   - Click **`✨ RENDER STUDIO CAPTIONS`**.
   - Import the output into Premiere Pro, CapCut, or DaVinci Resolve on **Track 2** above your video (`Track 1`), and apply **Ultra Key / Chroma Key** using `#00FF00`.

