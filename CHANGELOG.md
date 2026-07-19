# Changelog

All notable changes to the Iman Gadzhi Style Captions Studio Pro project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.6.0] - 2026-07-19
### Added
- `.gitignore` file covering virtual environments, `__pycache__`, environment secrets (`.env`), and temporary/rendered media files (`*.mp4`, `*.mov`, `gui_output_captions.mp4`, `live_style_preview.png`).
- `tiny_local_studio.py` standalone local studio execution script (created pursuant to our Core Directive on File Preservation During Major Modifications) optimized for pure local execution without external cloud or Hugging Face Spaces hooks.
### Changed
- Updated `README.md` to remove Hugging Face Spaces YAML metadata headers (`sdk: gradio`, `app_file`, etc.), Hugging Face Spaces live badges, and cloud deployment descriptions.
- Updated launch documentation to guide users directly to running `python tiny_local_studio.py` locally while preserving `tiny.py` as an untouched fallback.
### Removed
- Removed `huggingface_hub<0.26.0` dependency requirement from `requirements.txt`.
- Removed `demo = app` Hugging Face Spaces global entrypoint assignment in `tiny_local_studio.py`.
- Gently removed the `deploy_dist/` Hugging Face cloud deployment distribution directory.
