---
title: Iman Gadzhi Auto-Captions Studio
emoji: 🎬
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 4.44.0
app_file: tiny.py
pinned: false
python_version: "3.10"
---
# 🎬 Iman Gadzhi Style Captions Studio (Green Screen Chroma Key Edition)

<div align="center">

[![Open in HF Spaces](https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-xl-dark.svg)](https://huggingface.co/spaces/Expodecaprio/iman-gadzhi-captions-studio)
[![Edition](https://img.shields.io/badge/Edition-Green%20Screen%20Chroma%20Key-00FF00?style=for-the-badge&logo=adobe-premiere-pro&logoColor=black)](https://github.com/Fazzbro/iman-gadzhi-captions-studio)
[![Gradio](https://img.shields.io/badge/Gradio-4.44.0-FF4B2B?style=for-the-badge&logo=gradio&logoColor=white)](https://gradio.app/)

### 🌟 Try the Live Web Application Instantly on Hugging Face Spaces!
Click the official badge banner above to run the AI studio directly in your browser without installing anything locally.

</div>

---

## ✨ Features
- **🟩 Solid Green Screen Output (`#00FF00`)**: Perfectly colored RGB green background optimized for 1-click Chroma Keying in Premiere Pro, CapCut, DaVinci Resolve, and Final Cut Pro.
- **🎙️ Preserved Timeline Audio**: Keeps the original audio waveform intact in the exported `.mp4` for instant synchronization and alignment with your video editor timeline.
- **🔥 Iman Gadzhi Typography**: Dual-word kinetic animation style with custom 3-stop (Top, Middle, Bottom) RGB color gradients, neon back-glows, and extruded 3D block shadows.
- **🎨 Neumorphic Soft UI**: Sleek embossed UI theme built on Gradio with customizable typography sizes and color palettes.

---

## 🛠️ How to Use in Video Editors
1. **Generate**: Upload your video to the [Live Hugging Face Space](https://huggingface.co/spaces/Expodecaprio/iman-gadzhi-captions-studio) and click **`✨ Render Captions`**.
2. **Download**: Save the generated green screen video (`gui_output_captions.mp4`).
3. **Import**: Place your original video on **Track 1** and the green screen caption video on **Track 2** (directly above it).
4. **Align**: Use the audio track waveforms to synchronize Track 2 with Track 1 with 100% precision.
5. **Chroma Key**: Apply the **Chroma Key / Ultra Key / Green Screen Removal** effect to Track 2, selecting the `#00FF00` green color.
6. **Done**: The green background disappears, leaving only your glowing 3D typography captions animated cleanly over your video!

---

## 💻 Run Locally
If you prefer running this application on your local machine:

```bash
# 1. Clone the repository
git clone https://github.com/Fazzbro/iman-gadzhi-captions-studio.git
cd iman-gadzhi-captions-studio

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the studio
python tiny.py
```
Open `http://localhost:7860` in your web browser!
