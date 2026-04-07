"""
Check what actual models are available in your Google Generative AI account
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import google.generativeai as genai
from config import Config


def main():
    print("\n" + "="*70)
    print("  CHECKING AVAILABLE MODELS")
    print("="*70 + "\n")
    
    # Configure
    genai.configure(api_key=Config.GOOGLE_API_KEY)
    print("✅ API configured\n")
    
    # List all models
    print("Fetching available models...")
    print("-" * 70)
    
    try:
        models_gen = genai.list_models()
        models = list(models_gen)  # Convert generator to list
        
        print(f"Found {len(models)} total models\n")
        
        # Show all models
        print("ALL AVAILABLE MODELS:")
        for i, model in enumerate(models, 1):
            # Extract model name
            name = model.name
            if name.startswith("models/"):
                name = name.replace("models/", "")
            
            # Check if supports generateContent
            supports_gen = hasattr(model, 'supported_generation_methods') 
            gen_content = False
            if supports_gen:
                gen_content = 'generateContent' in model.supported_generation_methods
            
            status = "✅" if gen_content else "⚠️"
            print(f"  {status} {i}. {name}")
            
            if supports_gen:
                print(f"      Methods: {model.supported_generation_methods}")
        
        print("\n" + "="*70)
        print("  RECOMMENDED MODELS TO USE")
        print("="*70 + "\n")
        
        # Find gemini models
        gemini_models = [m for m in models if "gemini" in m.name.lower()]
        if gemini_models:
            print(f"Found {len(gemini_models)} Gemini models:\n")
            for model in gemini_models:
                name = model.name.replace("models/", "")
                print(f"✅ Use: {name}")
        else:
            print("⚠️  No Gemini models found. This is unusual.")
        
        print("\n" + "="*70)
        print("  USAGE EXAMPLE")
        print("="*70 + "\n")
        
        if gemini_models:
            first_model = gemini_models[0].name.replace("models/", "")
            print(f"import google.generativeai as genai\n")
            print(f"genai.configure(api_key='YOUR_API_KEY')")
            print(f"model = genai.GenerativeModel('{first_model}')")
            print(f"response = model.generate_content('Hello!')")
            print(f"print(response.text)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
