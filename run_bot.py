import os
import subprocess
import sys

def run():
    root = r"C:\Users\user\Desktop\Проект телега"
    os.chdir(root)
    
    python_exe = os.path.join(root, "venv", "Scripts", "python.exe")
    
    # Use 'Знакомство' if no arg provided, or pass sys.argv[1]
    theme = sys.argv[1] if len(sys.argv) > 1 else "Знакомство"
    
    cmd = [python_exe, "main.py", theme]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    run()
