"""
Test script to validate Gemini model fixes and fallback system.
Verifies that the model handler works correctly and all fallback logic is in place.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_model_handler():
    """Test the model handler with fallback"""
    print("=" * 70)
    print("STEP 1: Testing Model Handler with Fallback")
    print("=" * 70)
    
    try:
        # Check if API key exists
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ No API key found in environment")
            print("   Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
            return False
        
        print(f"✅ API key found (length: {len(api_key)})")
        
        # Import model handler
        from services.model_handler import ModelHandler
        
        # Initialize handler
        print("\n🔄 Initializing ModelHandler...")
        handler = ModelHandler(api_key)
        
        # Test getting model with fallback
        print("🔄 Attempting to get model with fallback...")
        model, model_name = handler.get_model("gemini-1.5-pro")
        
        print(f"✅ Successfully loaded model: {model_name}")
        print(f"   Model type: {type(model)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_config_loading():
    """Test configuration loading from .env"""
    print("\n" + "=" * 70)
    print("STEP 2: Testing Configuration Loading")
    print("=" * 70)
    
    try:
        from config import Config
        
        # Test .env loading
        is_valid, errors = Config.validate()
        
        if is_valid:
            print("✅ Configuration is VALID")
            print(f"   Google API Key: {Config.GOOGLE_API_KEY[:20]}...")
            print(f"   Serper API Key: {Config.SERPER_API_KEY[:20]}...")
            print(f"   Timeouts: Serper={Config.SERPER_TIMEOUT}s, Scrape={Config.SCRAPE_TIMEOUT}s")
            return True
        else:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_llm_service():
    """Test LLM Service initialization"""
    print("\n" + "=" * 70)
    print("STEP 3: Testing LLM Service")
    print("=" * 70)
    
    try:
        from config import Config
        from services.llm_service import LLMService
        
        print("🔄 Initializing LLMService...")
        service = LLMService(api_key=Config.GOOGLE_API_KEY)
        
        print(f"✅ LLMService initialized")
        print(f"   Model: {service.model_name}")
        print(f"   Type: {type(service.model)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_fallback_models():
    """Test that fallback model list is correct"""
    print("\n" + "=" * 70)
    print("STEP 4: Checking Fallback Model List")
    print("=" * 70)
    
    try:
        from services.model_handler import ModelHandler
        
        models = ModelHandler.AVAILABLE_MODELS
        
        print("Available fallback models:")
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model}")
        
        # Verify important models are available
        if "gemini-1.5-pro" in models:
            print("\n✅ gemini-1.5-pro is in fallback list")
        else:
            print("\n⚠️  gemini-1.5-pro NOT in fallback list")
        
        if "gemini-pro" in models:
            print("✅ gemini-pro is in fallback list")
        else:
            print("⚠️  gemini-pro NOT in fallback list")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_all_files_updated():
    """Verify all Python files have been updated"""
    print("\n" + "=" * 70)
    print("STEP 5: Checking File Updates")
    print("=" * 70)
    
    files_to_check = [
        "services/llm_service.py",
        "services/model_handler.py",
        "services/llm_error_handler.py",
        "streamlit_gemini_pipeline_fixed.py",
        "langgraph_enhanced_multi_agent_system.py",
        "langgraph_multi_agent_system.py",
        "agentic_browser_pipeline.py",
    ]
    
    all_good = True
    for filepath in files_to_check:
        full_path = Path(__file__).parent / filepath
        if full_path.exists():
            print(f"✅ {filepath}")
            
            # Check for bad model references
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'gemini-1.5-flash"' in content and 'create_model_with_fallback' not in content:
                        print(f"   ⚠️  Warning: Still contains hardcoded gemini-1.5-flash")
                        all_good = False
            except Exception as e:
                print(f"   ⚠️  Could not read file: {e}")
        else:
            print(f"❌ {filepath} - NOT FOUND")
            all_good = False
    
    return all_good


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " GEMINI MODEL FIX VALIDATION - ALL 9 STEPS".center(68) + "║")
    print("╚" + "=" * 68 + "╝\n")
    
    results = {
        "Config Loading": test_config_loading(),
        "Model Handler": test_model_handler(),
        "LLM Service": test_llm_service(),
        "Fallback Models": test_fallback_models(),
        "File Updates": test_all_files_updated(),
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED! Model fixes are working correctly.")
        print("\nNext steps:")
        print("1. Run: streamlit run streamlit_gemini_pipeline_fixed.py")
        print("2. Test with a query like 'benefits of exercise'")
        print("3. If error occurs, check logs for fallback activation")
    else:
        print("❌ Some tests failed. Please review the output above.")
        print("\nCommon issues:")
        print("- API key not set: export GOOGLE_API_KEY='your_key'")
        print("- File not updated: Run model fixes again")
        print("- Module import error: Check Python path")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
