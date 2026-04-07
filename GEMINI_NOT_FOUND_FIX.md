"""
GEMINI NOT_FOUND FIX - COMPLETE GUIDE
=====================================

ERROR: "models/gemini-1.5-pro NOT_FOUND (v1beta)"

ROOT CAUSE:
- Old google-generativeai library (< 0.7.0)
- Model names without -latest suffix no longer valid
- API version incompatibility


SOLUTION IMPLEMENTED
====================

1. UPGRADED PACKAGES
   Old:  google-generativeai==0.3.0
   New:  google-generativeai>=0.7.0
   
   Other packages also upgraded:
   - langchain>=0.2.0
   - langchain-google-genai>=0.1.0
   - langgraph>=0.1.0

2. UPDATED MODEL NAMES
   Old models (DEPRECATED):
   ❌ "gemini-1.5-pro"        → NOT_FOUND error
   ❌ "gemini-1.5-flash"      → NOT_FOUND error
   
   New models (WORKING):
   ✅ "gemini-1.5-pro-latest"     → Use this (PRIMARY)
   ✅ "gemini-1.5-flash-latest"   → Use this (BACKUP)

3. FALLBACK SYSTEM (services/model_handler.py)
   Priority order:
   1. gemini-1.5-pro-latest      (PRIMARY - most capable)
   2. gemini-1.5-flash-latest    (SECONDARY - faster)
   3. gemini-1.5-pro            (FALLBACK - may not work)
   4. gemini-pro                (LAST RESORT)
   
   If primary fails → automatically tries next

4. ERROR HANDLING
   - 404 NOT_FOUND → Falls back automatically
   - Shows clear error message to user
   - Retries with fallback model


FILES CHANGED
=============

Modified:
✅ requirements.txt
   - Updated google-generativeai version

✅ services/model_handler.py  
   - Changed model list to use -latest suffix
   - Reordered priority for reliability

✅ agentic_browser_pipeline_fixed.py
   - Changed "gemini-1.5-flash" → "gemini-1.5-pro-latest"

New files created:
✅ test_gemini_fix.py
   - Comprehensive model testing script
   - Verifies which models work

✅ QUICK_FIX.py
   - One-click setup script
   - Upgrades packages automatically


HOW TO APPLY FIX
=================

OPTION 1: QUICK AUTOMATED FIX (Recommended)
-------------------------------------------
1. Open PowerShell in project root
2. Activate venv: .\.venv_local\Scripts\Activate.ps1
3. Run: python QUICK_FIX.py
4. Done!

OPTION 2: MANUAL FIX
-------------------
1. Upgrade packages:
   pip install --upgrade google-generativeai langchain langchain-google-genai langgraph

2. Test models work:
   python test_gemini_fix.py

3. Run Streamlit:
   streamlit run streamlit_gemini_pipeline_fixed.py


VERIFICATION
=============

After applying fix, run:
  python test_gemini_fix.py

Expected output:
  ✅ WORKING models (2+)
  • gemini-1.5-pro-latest
  • gemini-1.5-flash-latest

If NOT_FOUND errors persist:
  1. Check .env has valid GOOGLE_API_KEY
  2. Verify API key has GenAI API access
  3. Check internet connection
  4. Try: pip install --upgrade google-generativeai


CODE EXAMPLES
==============

Before (WRONG - causes NOT_FOUND):
-----------------------------------
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")  # ❌ NOT_FOUND

response = model.generate_content("Hello")


After (CORRECT - works):
-----------------------
import google.generativeai as genai
from services.model_handler import ModelHandler

genai.configure(api_key=api_key)
handler = ModelHandler(api_key)
model, model_name = handler.get_model("gemini-1.5-pro-latest")  # ✅ Works

response = model.generate_content("Hello")


Using in Streamlit (AUTO FALLBACK):
----------------------------------
from services.model_handler import ModelHandler

model_handler = ModelHandler(Config.GOOGLE_API_KEY)

# In your function:
try:
    model, model_name = model_handler.get_model("gemini-1.5-pro-latest")
    
    # If primary fails, automatically falls back to next
    response = model.generate_content(prompt)
    
except Exception as e:
    if "404" in str(e):
        st.warning("Model temporarily unavailable, using fallback...")
        # Handler already tried fallback
    else:
        st.error(f"Error: {e}")


TROUBLESHOOTING
================

Problem: Still getting NOT_FOUND error
Solution:
  1. Verify upgrade: pip list | grep google-generativeai
  2. Should show: google-generativeai >= 0.7.0
  3. If not, run: pip install --upgrade google-generativeai
  4. Restart Streamlit: CTRL+C, then re-run

Problem: Wrong API key
Solution:
  1. Check .env file
  2. Verify GOOGLE_API_KEY is set
  3. Visit: https://ai.google.dev/pricing
  4. Get new key if needed

Problem: Tests pass but Streamlit still fails
Solution:
  1. Clear Streamlit cache: rm -r .streamlit/
  2. Stop Streamlit: CTRL+C
  3. Restart: streamlit run streamlit_gemini_pipeline_fixed.py

Problem: "models/gemini-1.5-pro-latest NOT_FOUND"
Solution:
  1. Try gemini-1.5-flash-latest instead
  2. Handler will auto-fallback
  3. Check Model list: python test_gemini_fix.py


FAQ
====

Q: Which model should I use?
A: gemini-1.5-pro-latest (primary), gemini-1.5-flash-latest (backup)

Q: What if -latest models are deprecated too?
A: Handler has fallback chain - will auto-try next model

Q: Performance impact of fallback?
A: Minimal - only happens on error, cached after success

Q: Can I use gemini-1.5-pro (without -latest)?
A: NOT RECOMMENDED - causes NOT_FOUND. Use -latest suffix.

Q: Does this require code changes?
A: No! Handler manages it automatically. Just upgrade package.

Q: When should I use gemini-1.5-flash-latest?
A: When you want faster responses, lower cost, or need fallback


IMPORTANT NOTES
================

✅ DO:
  • Use model names with -latest suffix
  • Keep model_handler.py updated
  • Test with test_gemini_fix.py
  • Use fallback system for reliability

❌ DON'T:
  • Use gemini-1.5-pro (without -latest)
  • Use old gemini-1.5-flash (without -latest)
  • Hardcode model names in multiple places
  • Ignore fallback system


NEXT STEPS
==========

1. Run QUICK_FIX.py OR manually upgrade packages
2. Run test_gemini_fix.py to verify
3. Restart Streamlit
4. Test first query in browser
5. Monitor console for errors
6. All done!


CONTACT / MORE HELP
===================

- Google GenAI API: https://ai.google.dev
- Model docs: https://ai.google.dev/models
- Pricing: https://ai.google.dev/pricing
- Status: https://status.cloud.google.com


Last Updated: 2024
For latest info, visit: https://ai.google.dev/docs
"""

if __name__ == "__main__":
    print(__doc__)
