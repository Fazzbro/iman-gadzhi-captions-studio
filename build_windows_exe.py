import os
import sys
import subprocess

def main():
    print("[Iman Gadzhi Studio Pro] Standalone Executable (.exe) Builder")
    current_dir = os.path.abspath(os.path.dirname(__file__))
    main_script = os.path.join(current_dir, "tiny.py")
    font_path = os.path.join(current_dir, "Poppins-Bold.ttf")
    
    if not os.path.exists(main_script):
        print(f"[Error] Main application script not found at {main_script}", file=sys.stderr)
        sys.exit(1)
        
    pyinstaller_args = [
        main_script,
        "--name=StudioCaptionsPro",
        "--noconfirm",
        "--clean",
        f"--add-data={font_path};." if os.path.exists(font_path) else "",
        "--hidden-import=whisper_timestamped",
        "--hidden-import=moviepy",
        "--hidden-import=PIL",
        "--hidden-import=gradio",
        "--hidden-import=torch",
    ]
    # Filter out empty args
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    print(f"Running PyInstaller with arguments:\n  " + "\n  ".join(pyinstaller_args))
    
    try:
        import PyInstaller.__main__
        PyInstaller.__main__.run(pyinstaller_args)
        print("\n[SUCCESS] Build complete! Your standalone Windows app is located in:")
        print(f"  {os.path.join(current_dir, 'dist', 'StudioCaptionsPro', 'StudioCaptionsPro.exe')}")
    except ImportError:
        print("[Notice] PyInstaller not imported directly. Running via subprocess...")
        cmd = [sys.executable, "-m", "PyInstaller"] + pyinstaller_args
        subprocess.run(cmd, check=True)
        print("\n[SUCCESS] Build complete! Your standalone Windows app is located in:")
        print(f"  {os.path.join(current_dir, 'dist', 'StudioCaptionsPro', 'StudioCaptionsPro.exe')}")

if __name__ == "__main__":
    main()
