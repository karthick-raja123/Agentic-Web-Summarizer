# 🚀 Quick Start Guide

## Prerequisites
- Python 3.9+
- Virtual environment activated
- Dependencies installed

---

## 1️⃣ Setup (One-Time)

### Option A: Fresh Installation
```bash
# Navigate to project
cd "D:\Git\Visual Web Agent\Visual-web-Agent"

# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies (clean version, no LangChain)
pip install -r requirements.txt
```

### Option B: Fix Existing Installation
```bash
# Remove old LangChain packages
pip uninstall langchain langchain-google-genai -y

# Install clean requirements
pip install -r requirements.txt
```

---

## 2️⃣ Configure API Keys

Edit `.env` file:
```
GOOGLE_API_KEY=your_key_from_makersuite.google.com
SERPER_API_KEY=your_key_from_serper.dev
```

---

## 3️⃣ Run the App

### Using PowerShell (Windows)
```powershell
cd "D:\Git\Visual Web Agent\Visual-web-Agent"
& ".\.venv\Scripts\Activate.ps1"
python -m streamlit run streamlit_gemini_pipeline.py
```

### Using Python Module
```bash
python -m streamlit run streamlit_gemini_pipeline.py
```

### Open Browser
```
http://localhost:8501
```

---

## 4️⃣ Using the App

1. **Enter a topic** in the text input
2. **Click "Search, Scrape, and Summarize"**
3. **Wait for results** (30-60 seconds)
4. **View the summary** displayed on screen
5. **Download as CSV** or **Listen to audio**

---

## 5️⃣ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### Error: "GOOGLE_API_KEY not found"
- Check `.env` file exists
- Verify API key is correct
- Restart Streamlit after editing `.env`

### Error: "Connection refused on 8501"
```bash
# Use different port
streamlit run streamlit_gemini_pipeline.py --server.port=8502
```

### Slow responses
- Check internet connection
- Verify API quotas
- API keys might have limits

---

## 📊 What's Different (Fixed Version)

| Feature | Old (LangChain) | New (Direct API) |
|---------|-----------------|-----------------|
| Dependencies | 45+ | 7 |
| Error Handling | Basic | Comprehensive |
| Performance | Slower | Faster |
| Setup Time | Long | Quick |
| Maintainability | Complex | Simple |

---

## ✅ Verification Checklist

- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip show streamlit` works)
- [ ] `.env` file configured with API keys
- [ ] `streamlit_gemini_pipeline.py` updated (no LangChain imports)
- [ ] Streamlit starts without errors
- [ ] Browser opens to http://localhost:8501

---

## 🔗 Important Links

- **Google Gemini API**: https://makersuite.google.com/app/apikey
- **Serper API**: https://serper.dev/api
- **Streamlit Docs**: https://docs.streamlit.io
- **Python-dotenv**: https://github.com/theskumar/python-dotenv

---

## 📞 Support

**If you get errors:**
1. Check that all dependencies installed: `pip list | grep -E "streamlit|google-generativeai"`
2. Verify `.env` file exists in project directory
3. Ensure API keys are not expired
4. Check internet connection
5. Try restarting Streamlit

---

**Status**: ✅ Ready to use
**Last Updated**: April 8, 2026
