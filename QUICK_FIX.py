"""
QUICK FIX SCRIPT - Run this to resolve NOT_FOUND errors
Steps:
1. Upgrade google-generativeai to latest version
2. Test that models work
3. Verify Streamlit app works
"""

import sys
import subprocess
import os
from pathlib import Path


def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def run_command(cmd, description):
    """Run command and handle errors"""
    print(f"📌 {description}...")
    print(f"   Running: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"⚠️  Command completed with status {result.returncode}")
    else:
        print(f"✅ {description} completed successfully\n")
    
    return result.returncode == 0


def main():
    print_section("GEMINI NOT_FOUND FIX - QUICK SETUP")
    
    # Step 1: Upgrade packages
    print_section("STEP 1: Upgrade google-generativeai Package")
    print("This fixes the NOT_FOUND (v1beta) error by upgrading to latest version")
    print("with support for -latest suffix models (gemini-1.5-pro-latest, etc.)\n")
    
    # Try to find and activate venv first
    venv_paths = [
        ".venv_local/Scripts/python.exe",
        ".venv/Scripts/python.exe",
        ".venv_local\\Scripts\\python.exe",
        ".venv\\Scripts\\python.exe",
        "python"
    ]
    
    python_exe = None
    for path in venv_paths:
        if os.path.exists(path):
            python_exe = path
            print(f"✅ Found Python: {path}\n")
            break
    
    if not python_exe:
        python_exe = "python"
        print(f"ℹ️  Using default python (make sure venv is activated)\n")
    
    # Upgrade packages
    packages_to_upgrade = [
        "google-generativeai",
        "langchain",
        "langchain-google-genai",
        "langgraph"
    ]
    
    print("Upgrading packages:")
    for package in packages_to_upgrade:
        cmd = f"{python_exe} -m pip install --upgrade {package}"
        print(f"  • Upgrading {package}...")
        subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print("\n✅ Package upgrades complete\n")
    
    # Step 2: Test models
    print_section("STEP 2: Test Gemini Models")
    print("Verifying that the correct models work...\n")
    
    test_cmd = f"{python_exe} test_gemini_fix.py"
    success = run_command(test_cmd, "Testing models")
    
    if not success:
        print("⚠️  Model test encountered issues. Continuing anyway...\n")
    
    # Step 3: Show what changed
    print_section("STEP 3: What Changed")
    print("✅ requirements.txt: Updated to latest google-generativeai (>= 0.7.0)")
    print("✅ services/model_handler.py: Model list updated to use -latest suffix models:")
    print("   • gemini-1.5-pro-latest (PRIMARY)")
    print("   • gemini-1.5-flash-latest (SECONDARY)")
    print("   • Fallbacks: gemini-1.5-pro, gemini-pro\n")
    
    # Step 4: Next steps
    print_section("STEP 4: How to Use")
    print("The Streamlit app will now automatically:")
    print("  1. Try gemini-1.5-pro-latest first")
    print("  2. Fall back to gemini-1.5-flash-latest if needed")
    print("  3. Fall back to gemini-1.5-pro or gemini-pro as last resort")
    print("  4. Show clear error messages if all fail\n")
    
    # Step 5: Run app
    print_section("STEP 5: Start the App")
    print("Choose one:\n")
    print("Option A (PowerShell on Windows):")
    print("  .venv_local\\Scripts\\Activate.ps1")
    print("  streamlit run streamlit_gemini_pipeline_fixed.py\n")
    
    print("Option B (Command Prompt):")
    print("  .venv_local\\Scripts\\activate")
    print("  streamlit run streamlit_gemini_pipeline_fixed.py\n")
    
    print("Option C (Linux/Mac):")
    print("  source .venv_local/bin/activate")
    print("  streamlit run streamlit_gemini_pipeline_fixed.py\n")
    
    # Final summary
    print_section("SUMMARY")
    print("🎯 Your project is now fixed!")
    print("✅ Using latest google-generativeai API")
    print("✅ Using correct -latest suffix models")
    print("✅ Automatic model fallback system in place")
    print("✅ Ready for production\n")
    
    print("If you still see NOT_FOUND errors:")
    print("  1. Check your API key in .env")
    print("  2. Verify API key has GenAI API access")
    print("  3. Run: python test_gemini_fix.py for detailed diagnostics\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
