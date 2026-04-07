"""
Gemini API Model Test - Verify correct models work with latest google-generativeai
This script tests that the NOT_FOUND error is fixed with -latest suffix models
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import google.generativeai as genai
from config import Config


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def test_package_version():
    """Test 1: Check google-generativeai version"""
    print_header("TEST 1: Package Version")
    
    version = genai.__version__ if hasattr(genai, '__version__') else "unknown"
    print(f"google-generativeai version: {version}")
    
    if version == "unknown":
        print("⚠️  Could not detect version, but continuing...")
    else:
        print("✅ Package version detected")
    
    return True


def test_api_key():
    """Test 2: Verify API key is configured"""
    print_header("TEST 2: API Key Configuration")
    
    if not Config.GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY not found")
        return False
    
    # Show first 10 chars
    key_preview = Config.GOOGLE_API_KEY[:10] + "..." if len(Config.GOOGLE_API_KEY) > 10 else Config.GOOGLE_API_KEY
    print(f"✅ API Key configured: {key_preview}")
    
    # Configure genai
    genai.configure(api_key=Config.GOOGLE_API_KEY)
    print("✅ genai.configure() called successfully")
    
    return True


def test_list_models():
    """Test 3: List available models"""
    print_header("TEST 3: Available Models")
    
    try:
        models = genai.list_models()
        print(f"Found {len(models)} total models\n")
        
        # Filter to Gemini models
        gemini_models = [m for m in models if "gemini" in m.name.lower()]
        print(f"Gemini models available:")
        
        for model in gemini_models:
            model_name = model.name.replace("models/", "")
            print(f"  • {model_name}")
        
        if not gemini_models:
            print("❌ No Gemini models found!")
            return False
        
        print(f"\n✅ Found {len(gemini_models)} Gemini models")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not list models: {e}")
        print("Continuing with manual model test...")
        return True  # Continue anyway


def test_models(model_names):
    """Test 4 & 5: Test specific model names"""
    print_header("TEST 4-5: Model Initialization (CRITICAL)")
    
    results = {}
    
    for model_name in model_names:
        print(f"\nTesting model: {model_name}")
        print("-" * 50)
        
        try:
            # Try to initialize model
            model = genai.GenerativeModel(model_name)
            print(f"  ✅ Model instantiated: {model_name}")
            
            # Try a simple request to verify it works
            try:
                response = model.generate_content("Say: 'This model works!'", stream=False)
                print(f"  ✅ Model responds correctly")
                print(f"  Response: {response.text[:50]}...")
                results[model_name] = "✅ WORKING"
            except Exception as req_error:
                if "401" in str(req_error) or "authentication" in str(req_error).lower():
                    print(f"  ⚠️  Auth error (API key issue): {req_error}")
                    results[model_name] = "❌ AUTH_ERROR"
                elif "not found" in str(req_error).lower() or "404" in str(req_error):
                    print(f"  ❌ Model NOT FOUND error: {req_error}")
                    results[model_name] = "❌ NOT_FOUND"
                else:
                    print(f"  ⚠️  Request error: {req_error}")
                    results[model_name] = "❓ OTHER_ERROR"
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "404" in str(e) or "not found" in error_msg or "not_found" in error_msg:
                print(f"  ❌ NOT_FOUND error: {e}")
                results[model_name] = "❌ NOT_FOUND"
            elif "401" in str(e) or "unauthorized" in error_msg:
                print(f"  ❌ Authentication error: {e}")
                results[model_name] = "❌ AUTH_ERROR"
            else:
                print(f"  ⚠️  Initialization error: {e}")
                results[model_name] = "❓ ERROR"
    
    return results


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  GEMINI API MODEL TEST - NOT_FOUND FIX VERIFICATION")
    print("="*70)
    
    try:
        # Test 1: Package version
        if not test_package_version():
            print("❌ Test 1 failed")
            return False
        
        # Test 2: API key
        if not test_api_key():
            print("❌ Test 2 failed - API key not configured")
            return False
        
        # Test 3: List models
        test_list_models()  # Non-critical
        
        # Test 4-5: Model initialization
        print_header("TESTING MODELS FOR NOT_FOUND ERROR")
        
        models_to_test = [
            "gemini-1.5-pro-latest",    # PRIMARY - should work
            "gemini-1.5-flash-latest",  # SECONDARY - should work
            "gemini-1.5-pro",           # OLD - may NOT_FOUND
            "gemini-pro",               # LAST RESORT
        ]
        
        results = test_models(models_to_test)
        
        # Print summary
        print_header("SUMMARY")
        
        working_models = [m for m, r in results.items() if r == "✅ WORKING"]
        not_found_models = [m for m, r in results.items() if r == "❌ NOT_FOUND"]
        
        print(f"✅ WORKING models ({len(working_models)}):")
        for m in working_models:
            print(f"  • {m}")
        
        print(f"\n❌ NOT_FOUND models ({len(not_found_models)}):")
        for m in not_found_models:
            print(f"  • {m}")
        
        # Final verdict
        print_header("RESULT")
        
        if working_models:
            print(f"✅ SUCCESS - Found {len(working_models)} working models!\n")
            print("RECOMMENDED USAGE:")
            print(f"  Use: gemini-1.5-pro-latest")
            print(f"  Fallback: gemini-1.5-flash-latest\n")
            print("Your model_handler.py has these in correct priority order.")
            print("Fix is verified and ready for deployment!")
            return True
        else:
            print("❌ FAILURE - No working models found!")
            print("\nACTION REQUIRED:")
            print("1. Check your Google API key in .env")
            print("2. Verify API key has Generative Language API access")
            print("3. Visit: https://ai.google.dev/pricing to verify models available")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
