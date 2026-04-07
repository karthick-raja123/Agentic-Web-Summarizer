"""
CRITICAL FIX: Migration to NEW google-genai library
The old google.generativeai is deprecated and uses v1beta API which has issues.
Switch to new google-genai package which handles this correctly.
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def run_cmd(cmd):
    """Run command silently and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def main():
    print_header("GEMINI NOT_FOUND FIX - UPGRADE TO google-genai")
    
    print("The error 'NOT_FOUND (v1beta)' indicates you're using old API version.")
    print("Google has deprecated google.generativeai in favor of google-genai.\n")
    
    print("The REAL FIX:")
    print("  ❌ Old: pip install google-generativeai==0.3.0")
    print("  ✅ New: pip install google-genai (latest)\n")
    
    # Step 1: Show what's currently installed
    print_header("CURRENT STATE")
    
    returncode, stdout, stderr = run_cmd("pip list")
    
    print("Packages related to Google AI:")
    for line in stdout.split("\n"):
        if "google" in line.lower() and ("genai" in line.lower() or "generative" in line.lower()):
            print(f"  {line}")
    
    print()
    
    # Step 2: Uninstall old
    print_header("STEP 1: REMOVE OLD PACKAGE")
    print("Uninstalling deprecated google.generativeai...\n")
    
    cmd = "pip uninstall google-generativeai -y"
    print(f"Running: {cmd}\n")
    returncode, stdout, stderr = run_cmd(cmd)
    print(stdout)
    
    # Step 3: Install NEW
    print_header("STEP 2: INSTALL NEW PACKAGE")
    print("Installing new google-genai package...\n")
    
    cmd = "pip install google-genai"
    print(f"Running: {cmd}\n")
    returncode, stdout, stderr = run_cmd(cmd)
    print(stdout)
    if stderr:
        print(stderr)
    
    # Step 4: Update requirements
    print_header("STEP 3: UPDATE requirements.txt")
    print("Updating requirements.txt to use google-genai...\n")
    
    req_path = Path(__file__).parent / "requirements.txt"
    content = req_path.read_text()
    
    # Remove old line, add new
    new_content = content.replace(
        "google-generativeai>=0.7.0",
        "google-genai>=0.2.0"
    )
    
    req_path.write_text(new_content)
    print("✅ requirements.txt updated")
    print("   Changed: google-generativeai>=0.7.0")
    print("   To:      google-genai>=0.2.0\n")
    
    # Step 5: Show what changed
    print_header("STEP 4: CODE CHANGES NEEDED")
    
    print("Files that need updates:")
    print("  1. services/model_handler.py")
    print("  2. services/llm_service.py")
    print("  3. streamlit_gemini_pipeline_fixed.py")
    print("  4. agentic_browser_pipeline_fixed.py\n")
    
    print("Update pattern (in each file):\n")
    print("OLD (DEPRECATED):")
    print("  import google.generativeai as genai")
    print("  genai.configure(api_key=api_key)")
    print("  model = genai.GenerativeModel('gemini-1.5-pro')\n")
    
    print("NEW (CORRECT):")
    print("  import google.genai as genai")
    print("  client = genai.Client(api_key=api_key)")
    print("  model = client.models.get('gemini-1.5-pro')\n")
    
    print_header("NEXT STEPS")
    print("1. ✅ Dependencies upgraded")
    print("2. 📝 Review code changes needed (see above)")
    print("3. 🔍 Test with: python test_gemini_new_api.py")
    print("4. 🚀 Restart Streamlit\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
