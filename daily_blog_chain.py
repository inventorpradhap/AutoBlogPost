import subprocess
import sys
import os

# Linux paths for GitHub Actions
PROJECT_DIR = os.getcwd()  # Current repo dir
VENV_PYTHON = sys.executable  # Python from actions setup
SCRIPT1 = 'Blog_generator.py'
SCRIPT2 = 'Automation_Working.py'

def run_script(script_path):
    result = subprocess.run([VENV_PYTHON, script_path], 
                          cwd=PROJECT_DIR, 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ {script_path} failed: {result.stderr}")
        sys.exit(1)
    print(f"✅ {script_path} completed")

if __name__ == '__main__':
    print("🚀 Starting daily Kindle blog automation...")
    run_script(SCRIPT1)
    run_script(SCRIPT2)
    print("🎉 Daily blog post complete!")
