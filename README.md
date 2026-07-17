# 🎬 Iman Gadzhi Style Captions Studio — Permanent Windows Desktop & Web Pro Edition

<div align="center">

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Live%20Space-FFD21E?style=for-the-badge&logoColor=black)](https://huggingface.co/spaces/Expodecaprio/iman-gadzhi-captions-studio)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11%20Desktop-00A4EF?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Fazzbro/iman-gadzhi-captions-studio)
[![Edition](https://img.shields.io/badge/Edition-Chroma%20Key%20Green%20Screen-00FF00?style=for-the-badge&logo=adobe-premiere-pro&logoColor=black)](https://github.com/Fazzbro/iman-gadzhi-captions-studio)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6%20Native%20Desktop-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/intro)

<br>

<a href="https://huggingface.co/spaces/Expodecaprio/iman-gadzhi-captions-studio" target="_blank">
  <img src="https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-xl-dark.svg" alt="Open in Hugging Face Spaces" height="52" style="border-radius: 8px; margin: 8px 0;">
</a>

### 🌟 Permanent Modern Windows Desktop & Live Web Application!
Experience true studio performance with native drag-and-drop media dropzones, non-blocking asynchronous multi-threaded rendering (`QThread`), live style preview canvases, interactive color swatches (`QColorDialog`), and instant browser-based cloud access via Hugging Face Spaces.

</div>

---

## ✨ Key Features

- **🖥️ True Native Windows Application (`PyQt6`)**: Built specifically for Windows 10 & 11 with custom dark studio neumorphic styling, drag-and-drop file inputs, and smooth 60 FPS UI performance.
- **⚡ Asynchronous AI Processing (`QThread`)**: Runs Whisper speech recognition and MoviePy compositing in dedicated background worker threads so your interface never freezes.
- **🟩 Solid Green Screen Output (`#00FF00`)**: Perfectly colored RGB green screen background optimized for 1-click Chroma Keying in Premiere Pro, CapCut, DaVinci Resolve, and Final Cut Pro.
- **🎙️ Preserved Timeline Audio**: Keeps the original audio waveform intact in the exported `.mp4` for instant synchronization and alignment on your video editor timeline.
- **🔥 Iman Gadzhi Typography**: Dual-word kinetic animation style with custom 3-stop (Top, Middle, Bottom) RGB color gradients, specular gloss sheen, and extruded 3D block shadows.
- **📌 Permanent Windows Shortcuts & EXE Builder**: Pin the application directly to your Windows Desktop or Start Menu, or build a standalone `.exe` installer.

---

## 🚀 How to Launch on Windows

### Option 1: Double-Click Launcher (Recommended)
Simply double-click **`Launch_Studio_Captions.bat`** in Windows Explorer. It automatically activates your virtual environment and opens the sleek desktop interface.

### Option 2: Pin to Windows Desktop & Start Menu
Run the shortcut generator once to create permanent Desktop and Start Menu icons:
```powershell
.venv\Scripts\python.exe create_desktop_shortcut.py
```
After running this, an **"Iman Gadzhi Studio Captions Pro"** icon will appear on your Desktop!

### Option 3: Build Standalone Executable (.exe)
If you want to compile the entire app into a self-contained single Windows binary:
```powershell
.venv\Scripts\python.exe build_windows_exe.py
```
Your compiled application will be created inside `dist\StudioCaptionsPro\StudioCaptionsPro.exe`.

---

## 🎨 Using the Windows Studio Interface

1. **📁 Media & Typography Tab**:
   - Drag and drop your **Source Video** (`.mp4`, `.mov`, `.mkv`) or **Audio file** (`.mp3`, `.wav`, `.m4a`) directly onto the dropzones.
   - Adjust the **Typography Font Scale** slider (80px to 200px) and select custom `.ttf`/`.otf` font files.
2. **🎨 3-Stop Color Palettes Tab**:
   - Click any interactive **Color Swatch Button** to open the native Windows Color Picker and customize your Top Line (Orange Gradient) and Bottom Line (Studio White) palettes.
3. **✨ VFX & Shadow Engine Tab**:
   - Dial in **Specular Gloss Intensity** (`0.0` to `2.5`) for glass/metallic sheen and customize **3D Extrusion Depth & Direction**.
4. **🔍 Live Style Preview**:
   - Click **`🔍 LIVE STYLE PREVIEW`** to generate an instant high-resolution sample PNG inside the monitor canvas before rendering the full video.
5. **🎬 Render & Editor Integration**:
   - Click **`✨ RENDER STUDIO CAPTIONS`**. Watch real-time progress percentages and log updates.
   - When complete, click **`▶️ PLAY OUTPUT VIDEO`** or **`📂 OPEN OUTPUT FOLDER`** to import directly into Premiere Pro or CapCut!

---

## 🌐 Web / Browser Fallback (Gradio)
If you prefer running the browser-based UI locally or on Hugging Face Spaces:
```powershell
.venv\Scripts\python.exe Caption.py
```
Open `http://localhost:7860` in your browser.
