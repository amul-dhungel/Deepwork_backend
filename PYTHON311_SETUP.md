# Python 3.11 Installation Steps for RAG

## Step 1: Download Python 3.11

1. Go to: https://www.python.org/downloads/windows/
2. Download **Python 3.11.10** (latest 3.11.x version)
3. Choose: "Windows installer (64-bit)"

## Step 2: Install Python 3.11

1. Run the installer
2. ✅ **IMPORTANT**: Check "Add Python 3.11 to PATH"
3. Click "Install Now"
4. Wait for installation to complete

## Step 3: Verify Installation

Open a **NEW** PowerShell window and run:
```powershell
python3.11 --version
# Should show: Python 3.11.10
```

## Step 4: Create RAG Virtual Environment

```powershell
cd C:\Users\amul.dhungel\Downloads\Nishugrop\WordAssistantAI\backend

# Create new venv with Python 3.11
python3.11 -m venv venv_rag

# Activate it
.\venv_rag\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

## Step 5: Install RAG Packages

```powershell
# Install PyTorch (CPU version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install RAG packages
pip install chromadb sentence-transformers

# Verify installation
python -c "import chromadb; import sentence_transformers; print('✅ All packages installed!')"
```

## Step 6: Update Backend to Use New Venv

### Option A: Update your run script
If you have a script that starts the backend, update it to use `venv_rag` instead of `venv_new`.

### Option B: Always activate before running
```powershell
cd backend
.\venv_rag\Scripts\activate
python main.py
```

## Step 7: Test RAG System

Once backend is running with the new venv:

```powershell
# Ingest newspapers
curl -X POST http://localhost:8000/api/rag/ingest `
  -H "Content-Type: application/json" `
  -d '{\"directory\": \"./data/Newspaper\"}'

# Test search
curl -X POST http://localhost:8000/api/rag/search `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"Arizona 1964\", \"n_results\": 5}'

# Check status
curl http://localhost:8000/api/rag/status
```

## 📝 Notes

- **Python 3.11** is recommended over 3.12 for better package compatibility
- The new `venv_rag` will coexist with your existing `venv_new`
- Total download size: ~500MB (Python + packages)
- Installation time: ~10 minutes

## ❓ Troubleshooting

### "python3.11 not found"
- Close and reopen PowerShell after installation
- Or use full path: `C:\Users\amul.dhungel\AppData\Local\Programs\Python\Python311\python.exe`

### "pip install fails"
- Make sure you activated the venv: `.\venv_rag\Scripts\activate`
- Your prompt should show `(venv_rag)` at the start

### "Backend still uses old venv"
- Make sure to activate `venv_rag` before running `python main.py`
- Or update your startup script

---

**After completing these steps, your RAG system will be fully functional!** 🚀
