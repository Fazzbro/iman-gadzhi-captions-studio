import os
import sys
import subprocess

def create_windows_shortcut(target_path, shortcut_path, description, working_dir, icon_path=None):
    """Creates a Windows .lnk shortcut using a clean VBScript bridge (works without requiring extra pywin32 dependencies)."""
    vbs_script = f"""
    Set oWS = WScript.CreateObject("WScript.Shell")
    sLinkFile = "{shortcut_path}"
    Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{target_path}"
    oLink.WorkingDirectory = "{working_dir}"
    oLink.Description = "{description}"
    """
    if icon_path and os.path.exists(icon_path):
        vbs_script += f'\n    oLink.IconLocation = "{icon_path}"\n'
    vbs_script += "\n    oLink.Save\n"
    
    vbs_file = os.path.join(working_dir, "temp_make_shortcut.vbs")
    with open(vbs_file, "w", encoding="utf-8") as f:
        f.write(vbs_script)
    
    try:
        subprocess.run(["cscript", "//Nologo", vbs_file], check=True)
    finally:
        if os.path.exists(vbs_file):
            os.remove(vbs_file)

def main():
    print("[Iman Gadzhi Studio Pro] Shortcut Generator")
    current_dir = os.path.abspath(os.path.dirname(__file__))
    launcher_path = os.path.join(current_dir, "Launch_Studio_Captions.bat")
    
    if not os.path.exists(launcher_path):
        print(f"[Error] Launcher not found at {launcher_path}", file=sys.stderr)
        sys.exit(1)
        
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desktop_dir):
        # Fallback to OneDrive Desktop if redirected
        onedrive_desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        if os.path.exists(onedrive_desktop):
            desktop_dir = onedrive_desktop
            
    shortcut_name = "Iman Gadzhi Studio Captions Pro.lnk"
    desktop_shortcut = os.path.join(desktop_dir, shortcut_name)
    
    print(f"Creating Desktop shortcut: {desktop_shortcut}")
    create_windows_shortcut(
        target_path=launcher_path,
        shortcut_path=desktop_shortcut,
        description="Iman Gadzhi Style AI Video Captions Pro (Green Screen Edition)",
        working_dir=current_dir
    )
    
    # Also create in Start Menu Programs if accessible
    start_menu_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs")
    if os.path.exists(start_menu_dir):
        start_shortcut = os.path.join(start_menu_dir, shortcut_name)
        print(f"Creating Start Menu shortcut: {start_shortcut}")
        create_windows_shortcut(
            target_path=launcher_path,
            shortcut_path=start_shortcut,
            description="Iman Gadzhi Style AI Video Captions Pro (Green Screen Edition)",
            working_dir=current_dir
        )
        
    print("\n[SUCCESS] Permanent shortcuts created! You can now launch Iman Gadzhi Studio Captions Pro from your Desktop or Start Menu.")

if __name__ == "__main__":
    main()
