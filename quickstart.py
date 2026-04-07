#!/usr/bin/env python3
"""
QUICKSTART SCRIPT - Ready-to-Run Project Setup
Validates everything and gives you a ready action items list
"""

import sys
from pathlib import Path
from config import Config

def banner():
    """Print welcome banner"""
    print("\n" + "=" * 80)
    print("✅ QUICKGLANCE - PRODUCTION-READY LOCAL SETUP")
    print("=" * 80 + "\n")

def check_files():
    """Check all required files exist"""
    print("📁 CHECKING PROJECT FILES...")
    
    files_needed = [
        ("config.py", "Configuration module"),
        ("agentic_browser_pipeline_fixed.py", "CLI version"),
        ("streamlit_gemini_pipeline_fixed.py", "Web UI version"),
        ("test_search.py", "Search API tests"),
        ("test_scraper.py", "Scraper tests"),
        ("test_summarizer.py", "Summarizer tests"),
        ("test_pipeline.py", "Pipeline tests"),
        (".env.clean", "Environment template"),
        ("requirements_clean.txt", "Dependencies"),
        ("LOCAL_RUN_GUIDE.md", "Setup guide"),
        ("TROUBLESHOOTING_GUIDE.md", "Troubleshooting"),
    ]
    
    all_exist = True
    for filename, description in files_needed:
        path = Path(filename)
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {filename:40} ({description})")
        if not exists:
            all_exist = False
    
    print()
    return all_exist

def check_config():
    """Check configuration"""
    print("⚙️  CHECKING CONFIGURATION...")
    
    is_valid, errors = Config.validate()
    
    if is_valid:
        print(f"  ✅ Environment configuration valid\n")
        return True
    else:
        print(f"  ❌ Configuration errors:\n")
        for error in errors:
            print(f"     {error}")
        print()
        return False

def check_dependencies():
    """Check dependencies"""
    print("📦 CHECKING DEPENDENCIES...")
    
    required = [
        ("google-generativeai", "Gemini API"),
        ("requests", "HTTP requests"),
        ("beautifulsoup4", "HTML parsing"),
        ("streamlit", "Web UI"),
        ("langchain", "LLM orchestration"),
        ("langgraph", "Agent graphs"),
        ("pytest", "Testing framework"),
    ]
    
    try:
        import pkg_resources
        installed = {pkg.key for pkg in pkg_resources.working_set}
        
        all_ok = True
        for package, description in required:
            package_key = package.lower().replace("-", "_").replace(".", "_")
            exists = any(package_key in str(pkg).lower() for pkg in pkg_resources.working_set)
            status = "✅" if exists else "❌"
            print(f"  {status} {package:30} ({description})")
            if not exists:
                all_ok = False
        
        print()
        return all_ok
    except Exception as e:
        print(f"  ⚠️  Could not verify dependencies: {str(e)}\n")
        return False

def show_next_steps():
    """Show next steps"""
    print("🎯 NEXT STEPS:\n")
    
    print("1. CREATE .env FILE")
    print("   • Copy .env.clean to .env")
    print("   • Edit .env and add your API keys:")
    print("     - GOOGLE_API_KEY: https://makersuite.google.com/app/apikey")
    print("     - SERPER_API_KEY: https://serper.dev")
    print()
    
    print("2. VALIDATE CONFIGURATION")
    print("   • Run: python config.py")
    print("   • Should show: ✅ All configurations valid!")
    print()
    
    print("3. RUN CLI VERSION")
    print('   • Run: python agentic_browser_pipeline_fixed.py "your query"')
    print("   • Or: python agentic_browser_pipeline_fixed.py (interactive)")
    print()
    
    print("4. RUN WEB VERSION")
    print("   • Run: streamlit run streamlit_gemini_pipeline_fixed.py")
    print("   • Open: http://localhost:8501")
    print()
    
    print("5. RUN TESTS")
    print("   • Run: pytest -v")
    print("   • Or: pytest test_search.py -v")
    print()

def show_commands():
    """Show useful commands"""
    print("📋 USEFUL COMMANDS:\n")
    
    commands = [
        ("Setup", [
            "python -m venv .venv",
            ".\\venv\\Scripts\\Activate.ps1",
            "pip install -r requirements_clean.txt",
        ]),
        ("Run", [
            'python agentic_browser_pipeline_fixed.py "machine learning"',
            "streamlit run streamlit_gemini_pipeline_fixed.py",
        ]),
        ("Test", [
            "pytest -v",
            "pytest test_search.py -v",
            "pytest test_pipeline.py::TestFullPipeline -v",
        ]),
        ("Validate", [
            "python config.py",
        ]),
    ]
    
    for category, cmds in commands:
        print(f"{category}:")
        for cmd in cmds:
            print(f"  $ {cmd}")
        print()

def show_documentation():
    """Show documentation files"""
    print("📚 DOCUMENTATION:\n")
    
    docs = [
        ("LOCAL_RUN_GUIDE.md", "Complete step-by-step setup (READ FIRST)", "📖"),
        ("TROUBLESHOOTING_GUIDE.md", "Solutions for 20+ common issues", "🔧"),
        ("PRODUCTION_READY_CHECKLIST.md", "Features and deployment guide", "✅"),
    ]
    
    for filename, description, icon in docs:
        print(f"{icon} {filename}")
        print(f"   {description}\n")

def main():
    """Main execution"""
    banner()
    
    # Check files
    files_ok = check_files()
    
    # Check config
    config_ok = check_config()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Show guidance
    if not config_ok:
        print("⚠️  CONFIGURATION ISSUE DETECTED\n")
        print("ACTION: Edit .env file with your API keys\n")
    
    if not deps_ok:
        print("⚠️  MISSING DEPENDENCIES\n")
        print("ACTION: Run: pip install -r requirements_clean.txt\n")
    
    if files_ok and config_ok and deps_ok:
        print("🎉 ALL CHECKS PASSED! YOU'RE READY TO GO!\n")
    
    # Show documentation
    show_documentation()
    
    # Show next steps
    show_next_steps()
    
    # Show commands
    show_commands()
    
    # Summary
    print("=" * 80)
    if files_ok and config_ok and deps_ok:
        print("STATUS: ✅ READY FOR PRODUCTION")
        print("\nStart with:")
        print('  python agentic_browser_pipeline_fixed.py "machine learning"')
        print("\nOr read documentation:")
        print("  LOCAL_RUN_GUIDE.md → TROUBLESHOOTING_GUIDE.md")
    else:
        print("STATUS: ⚠️ SETUP NEEDED")
        print("\nFix the issues above, then run this script again.")
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nFor help, see TROUBLESHOOTING_GUIDE.md")
        sys.exit(1)
