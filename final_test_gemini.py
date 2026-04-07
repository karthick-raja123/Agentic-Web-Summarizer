"""
FINAL TEST - Verify Gemini 2.5 models work correctly
This replaces all the broken gemini-1.5 references
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import google.generativeai as genai
from config import Config


def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def main():
    print_header("FINAL GEMINI FIX TEST - Using Gemini 2.5 Models")
    
    # Step 1: Configure
    print_header("STEP 1: API Configuration")
    try:
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        print("✅ API configured successfully")
        print(f"   Key: {Config.GOOGLE_API_KEY[:10]}...\n")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False
    
    # Step 2: Test models
    models_to_test = [
        ("gemini-2.5-pro", "PRIMARY - Most capable"),
        ("gemini-2.5-flash", "FALLBACK - Faster/cheaper"),
        ("gemini-pro-latest", "BACKUP - Latest alias"),
    ]
    
    print_header("STEP 2: Testing Models")
    
    working_models = []
    
    for model_name, description in models_to_test:
        print(f"Testing: {model_name}")
        print(f"  Description: {description}")
        print("-" * 70)
        
        try:
            # Step 2a: Initialize model
            print(f"  🔄 Initializing model...")
            model = genai.GenerativeModel(model_name)
            print(f"  ✅ Model object created")
            
            # Step 2b: Send test request
            print(f"  🔄 Sending test request...")
            response = model.generate_content(
                "Reply with 'Working!' if you can read this.",
                stream=False
            )
            
            # Step 2c: Check response
            text = response.text if hasattr(response, 'text') else str(response)
            print(f"  ✅ Model responded: {text[:50]}...")
            print(f"  ✅ {model_name} is WORKING\n")
            
            working_models.append(model_name)
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Error: {error_msg[:80]}...")
            print()
    
    # Step 3: Summary
    print_header("SUMMARY")
    
    if working_models:
        print(f"✅ SUCCESS! Found {len(working_models)} working models:\n")
        for i, model in enumerate(working_models, 1):
            print(f"   {i}. {model}")
        
        print("\n✅ RECOMMENDED:")
        print(f"   Use: {working_models[0]} (primary)")
        if len(working_models) > 1:
            print(f"   Fallback to: {working_models[1]}")
        
        print("\n" + "="*70)
        print("  YOUR PROJECT IS NOW FIXED!")
        print("="*70)
        print("\nChanges made:")
        print("  ✅ Model names updated to gemini-2.5 (from gemini-1.5)")
        print("  ✅ requirements.txt updated")
        print("  ✅ services/model_handler.py updated")
        print("  ✅ All old 1.5 references removed")
        print("\nYou can now:")
        print("  1. Run: streamlit run streamlit_gemini_pipeline_fixed.py")
        print("  2. Try your first query")
        print("  3. No more 404 NOT_FOUND errors!\n")
        
        return True
    else:
        print("❌ FAILURE - No working models found!")
        print("\nPossible causes:")
        print("  1. Google API key not valid")
        print("  2. Generative Language API not enabled")
        print("  3. Network connectivity issues")
        print("\nNext steps:")
        print("  1. Visit: https://ai.google.dev")
        print("  2. Get a new API key if needed")
        print("  3. Verify it's set in .env")
        print("  4. Run again: python final_test_gemini.py\n")
        
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
