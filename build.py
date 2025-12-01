import os
import subprocess
import sys

def build():
    print("="*50)
    print("SnapFlux Automation Builder")
    print("="*50)
    
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(base_dir, "web")
    chrome_dir = os.path.join(base_dir, "chrome")
    modules_dir = os.path.join(base_dir, "modules")
    
    # Check dependencies
    print("Checking dependencies...")
    try:
        import PyInstaller
        print("PyInstaller is installed.")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Build command arguments
    # separator for add-data is ; on Windows
    sep = ";" if os.name == 'nt' else ":"
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "SnapFlux",
        "--contents-directory", "SnapFlux",
        "--clean",
        # Include Web Assets
        "--add-data", f"{web_dir}{sep}web",
        # Include Modules (explicitly to be safe)
        "--add-data", f"{modules_dir}{sep}modules",
        # Hidden imports often missed
        "--hidden-import", "eel",
        "--hidden-import", "playwright",
        "--hidden-import", "playwright.sync_api",
        "--hidden-import", "playwright._impl",
        "--hidden-import", "openpyxl",
        "--hidden-import", "PIL",
        "--hidden-import", "requests",
        "--hidden-import", "logging.handlers",
        "--hidden-import", "pandas",
        "--hidden-import", "numpy",
        "main_gui.py"
    ]

    # Generate Icon from Logo
    logo_path = os.path.join(web_dir, "img", "logo.png")
    icon_path = os.path.join(base_dir, "icon.ico")
    
    if os.path.exists(logo_path):
        print(f"Found logo at: {logo_path}")
        try:
            from PIL import Image
            img = Image.open(logo_path)
            # Convert to ICO
            img.save(icon_path, format='ICO', sizes=[(256, 256)])
            print("Generated icon.ico for the application.")
            cmd.insert(4, f"--icon={icon_path}")
        except ImportError:
            print("Pillow not installed. Skipping icon generation.")
        except Exception as e:
            print(f"Warning: Could not create icon: {e}")
    
    # Add Chrome if it exists
    if os.path.exists(chrome_dir):
        print(f"Found Chrome directory at: {chrome_dir}")
        print("Bundling Chrome... (This will increase file size significantly)")
        cmd.extend(["--add-data", f"{chrome_dir}{sep}chrome"])
    else:
        print("Warning: 'chrome' directory not found. Browser will not be bundled.")

    print("\nRunning PyInstaller command:")
    print(" ".join(cmd))
    print("\nPlease wait, this may take a few minutes...")
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*50)
        print("BUILD SUCCESSFUL!")
        print("="*50)
        print("BUILD SUCCESSFUL!")
        print("="*50)
        print(f"Application folder: {os.path.join(base_dir, 'dist', 'SnapFlux')}")
        print("Run 'SnapFlux.exe' inside that folder.")
    except subprocess.CalledProcessError as e:
        print("\n" + "="*50)
        print("BUILD FAILED!")
        print("="*50)
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    build()
