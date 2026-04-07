# ============================================================================
# BEGINNER'S GUIDE - Setting Up QuickGlance Streamlit
# ============================================================================
# Step-by-step guide for users new to Python and Streamlit
# ============================================================================

## Before You Start

### Required (free):
1. **Python 3.9+** - Download: https://www.python.org/downloads/
2. **Google Gemini API Key** - Get free: https://makersuite.google.com/app/apikey
3. **Serper Search API Key** - Get free: https://serper.dev (100 calls/month free)
4. **Text Editor** - Notepad, VS Code, or any editor

### Not Required (but helps):
- Command line experience
- Python knowledge
- API experience

---

## Step 1: Install Python

### On Windows

1. Visit: https://www.python.org/downloads/
2. Click blue button "Download Python 3.12"
3. Run the installer
4. **IMPORTANT:** Check the box "Add Python to PATH"
5. Click "Install Now"
6. Wait for completion

### Verify Installation

Open Command Prompt (search "cmd" in Start menu):

```
python --version
```

Should show: `Python 3.12.X` (or similar)

If error, restart computer and try again.

---

## Step 2: Prepare Your Workspace

### Navigate to Project

Open Command Prompt and type:

```
cd d:\Git\Visual Web Agent\Visual-web-Agent
```

Then press Enter.

Screen should now show path like:
```
d:\Git\Visual Web Agent\Visual-web-Agent>
```

---

## Step 3: Create Virtual Environment

Copy and paste this command:

```
python -m venv .venv
```

Press Enter. Wait 20-30 seconds.

You should see command prompt return. ✓

---

## Step 4: Activate Virtual Environment

Copy and paste this command:

```
.venv\Scripts\activate.bat
```

Press Enter.

Screen should now show: `(.venv)` at the start of the line. ✓

**Important:** Keep this terminal open for all next steps.

---

## Step 5: Install Dependencies

Copy and paste this command:

```
pip install -r requirements_clean.txt
```

Press Enter. There will be lots of text scrolling. This takes 2-3 minutes.

Wait for it to finish. You'll see the command prompt again. ✓

### Verify Installation

Paste this command to check:

```
pip list
```

You should see: `streamlit`, `google-generativeai`, `langchain`, etc.

---

## Step 6: Get API Keys

### Google Gemini Key (2 minutes)

1. Visit: https://makersuite.google.com/app/apikey
2. Click blue "Create API Key" button
3. It appears in a dialog box
4. Click "Copy" button
5. **Save this key somewhere** - you'll need it soon

### Serper API Key (3 minutes)

1. Visit: https://serper.dev/signup
2. Sign up with email (free tier available)
3. Login
4. Click your profile → API section
5. Copy the API Key shown
6. **Save this key** - you'll need it soon

---

## Step 7: Create .env File with Your API Keys

### Option A: Using Command Line

In the same Command Prompt, paste:

```
notepad .env
```

This opens Notepad. A message might say "File not found, create?"—click **Yes**.

### Option B: Using File Explorer

1. Open File Explorer
2. Navigate to: `d:\Git\Visual Web Agent\Visual-web-Agent`
3. Right-click → New → Text Document
4. Rename it to `.env` (including the dot)
5. Right-click → Open with → Notepad

### Fill in the .env File

In Notepad, paste this:

```
GOOGLE_API_KEY=your_google_key_here
SERPER_API_KEY=your_serper_key_here
REQUEST_TIMEOUT=30
SERPER_TIMEOUT=15
SCRAPE_TIMEOUT=10
DEBUG=false
```

**Now replace:**
- `your_google_key_here` → Paste your Google key
- `your_serper_key_here` → Paste your Serper key

Example (with dummy keys):
```
GOOGLE_API_KEY=AIzaSyD8-1234567890abcdefghijklmnopqrst
SERPER_API_KEY=5bb84fd903aa487920271c447d4b2ef245e1fa60
REQUEST_TIMEOUT=30
SERPER_TIMEOUT=15
SCRAPE_TIMEOUT=10
DEBUG=false
```

### Save the File

- Press Ctrl+S
- Close Notepad

---

## Step 8: Test Configuration

Back in Command Prompt (from Step 4), paste:

```
python -c "from config import Config; print(Config.validate())"
```

Press Enter.

### Expected Result:

Should show:
```
(True, [])
```

This means ✓ Everything is configured correctly!

### If You See Error:

```
(False, ['...'])
```

Check:
1. Is `.env` in the same folder as `streamlit_gemini_pipeline_fixed.py`?
2. Did you paste actual API keys (not "your_api_key_here")?
3. Are the keys valid (20+ characters)?

---

## Step 9: Run the App!

In Command Prompt, paste:

```
streamlit run streamlit_gemini_pipeline_fixed.py
```

Press Enter. Wait 10-15 seconds.

### You Should See:

1. Chrome/Edge browser opens automatically
2. Page shows "QuickGlance" at the top
3. No error messages visible
4. A text box saying "Enter your research query..."

✓ **Success!** The app is running!

---

## Step 10: Try Your First Query

1. In the text box, type: `What are the benefits of exercise?`
2. Press Enter or click Submit
3. Wait 5-10 seconds
4. You should see:
   - A summary (5 bullet points)
   - A "Sources" section with links
   - Execution time

✓ **It works!**

---

## Troubleshooting

### App Won't Start

**Error: "python is not recognized"**
- Solution: Restart computer after installing Python

**Error: "no module named streamlit"**
- Solution: Did you activate venv? Should see `(.venv)` in command prompt
- Run: `.venv\Scripts\activate.bat` again

**Error: "no .env file"**
- Solution: Make sure you created `.env` in step 7
- Make sure it's in: `d:\Git\Visual Web Agent\Visual-web-Agent`

### App Crashes During Query

**Error: "Configuration Error"**
- Did you fill in real API keys in .env?
- Did you press Ctrl+S to save .env?

**Error: "GOOGLE_API_KEY is invalid"**
- Go back to https://makersuite.google.com/app/apikey
- Generate a NEW key
- Update .env
- Restart app (press Ctrl+C in command prompt, then re-run command)

**Error: "No results found"**
- Try a different query
- Check internet connection
- Enable Debug Mode (see below)

---

## Debug Mode (If Something's Wrong)

1. In Streamlit app, look for "⚙️ Settings & Status" (left sidebar)
2. Check box: "🐛 Debug Mode"
3. Try your query again
4. Watch Command Prompt window:
   - You'll see URLs being searched
   - Content being pulled
   - API responses
   - Error messages

**Share this output** if you need help!

---

## Stopping the App

1. Go to Command Prompt
2. Press Ctrl+C
3. Type: yes
4. Command prompt returns to normal

---

## Running It Again (Next Time)

1. Open Command Prompt
2. `cd d:\Git\Visual Web Agent\Visual-web-Agent`
3. `.venv\Scripts\activate.bat`
4. `streamlit run streamlit_gemini_pipeline_fixed.py`

**Tip:** You can create a `.bat` file with these commands so you just double-click next time!

---

## Next Steps

Once everything works:

1. **Try different queries** - News, research topics, how-to questions
2. **Enable Debug Mode** - See what's happening behind the scenes
3. **Customize timeout** - If queries timeout, increase `SERPER_TIMEOUT` in .env
4. **Setup FastAPI** - For metrics dashboard (see advanced docs)

---

## Getting Help

1. **Check output** - Read what the app printed when it failed
2. **Enable Debug** - See detailed information
3. **See TROUBLESHOOTING.md** - Common issues and fixes
4. **Check API services:**
   - Is Google API working? https://status.cloud.google.com
   - Is Serper API working? https://serper.dev

---

## Common Beginner Questions

**Q: Where do I get my API keys from again?**
A: Google - https://makersuite.google.com/app/apikey | Serper - https://serper.dev

**Q: Why do I need a `.env` file?**
A: It stores your secret API keys locally without putting them in version control

**Q: Can I share my API key?**
A: NO! Anyone with your key can use your quotas. Keep it secret—treat it like a password

**Q: What if I see "Chrome not found"?**
A: You have Edge installed instead. App will use Edge—that's fine!

**Q: Can I run the app without internet?**
A: No, it needs internet to search and use Gemini API

**Q: How long should queries take?**
A: 5-15 seconds depending on internet speed and result complexity

---

**Version:** 1.0  
**Tested:** Python 3.9-3.12 on Windows 10/11  
**Status:** Beginner Friendly ✓

