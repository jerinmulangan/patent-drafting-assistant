# Ollama Setup Guide for Patent Draft Generation

This guide will help you set up Ollama for local patent draft generation in the Patent NLP Project.

## Prerequisites

- Windows 10/11, macOS, or Linux
- At least 4GB RAM (8GB+ recommended)
- 2GB+ free disk space for models
- Python 3.8+ with pip

## Step 1: Install Ollama

### Windows

1. **Download Ollama for Windows:**
   - Visit [https://ollama.ai](https://ollama.ai)
   - Click "Download for Windows"
   - Run the installer as administrator

2. **Alternative: Using PowerShell (if winget is available):**
   ```powershell
   winget install Ollama.Ollama
   ```

3. **Alternative: Manual download:**
   - Download from: https://github.com/ollama/ollama/releases
   - Extract and run `ollama.exe`

### macOS

1. **Using Homebrew:**
   ```bash
   brew install ollama
   ```

2. **Manual installation:**
   - Download from: https://ollama.ai
   - Or: `curl -fsSL https://ollama.ai/install.sh | sh`

### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## Step 2: Start Ollama Service

### Windows
```cmd
ollama serve
```

### macOS/Linux
```bash
ollama serve
```

**Note:** Keep this terminal window open while using the patent draft generation feature.

## Step 3: Download Recommended Models

Open a new terminal/command prompt and run:

```bash
# Download lightweight model (recommended for first-time users)
ollama pull llama3.2:3b

# Download ultra-fast model (1B parameters)
ollama pull llama3.2:1b

# Download high-quality model (7B parameters) - requires more RAM
ollama pull mistral:7b

# Download technical model (7B parameters) - good for software patents
ollama pull codellama:7b
```

## Step 4: Verify Installation

Test that Ollama is working:

```bash
# Check if Ollama is running
ollama list

# Test with a simple prompt
ollama run llama3.2:3b "Hello, how are you?"
```

## Step 5: Install Python Dependencies

In your project directory:

```bash
pip install ollama pytest pytest-asyncio
```

## Step 6: Test the Patent Draft Generation

1. **Start the backend server:**
   ```bash
   python main.py
   ```

2. **Test the API endpoints:**
   ```bash
   # Check Ollama health
   curl http://localhost:8000/api/v1/ollama/health
   
   # Test draft generation
   curl -X POST http://localhost:8000/api/v1/generate_draft \
     -H "Content-Type: application/json" \
     -d '{
       "description": "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans.",
       "model": "llama3.2:3b",
       "template_type": "utility"
     }'
   ```

3. **Run the test suite:**
   ```bash
   python test_draft_generation.py
   ```

## Step 7: Use the Frontend

1. **Start the frontend:**
   ```bash
   cd frontend
   npm start
   ```

2. **Navigate to the Draft Assistant:**
   - Go to http://localhost:3000
   - Click on "Draft Assistant" in the navigation
   - The Ollama status should show "Online"

## Model Recommendations

### For Different Use Cases:

1. **Quick Drafts (1B parameters):**
   - Model: `llama3.2:1b`
   - RAM: 2GB
   - Speed: Very fast
   - Quality: Basic

2. **Balanced Performance (3B parameters):**
   - Model: `llama3.2:3b` (default)
   - RAM: 4GB
   - Speed: Fast
   - Quality: Good

3. **High Quality (7B parameters):**
   - Model: `mistral:7b`
   - RAM: 8GB
   - Speed: Moderate
   - Quality: High

4. **Technical Patents (7B parameters):**
   - Model: `codellama:7b`
   - RAM: 8GB
   - Speed: Moderate
   - Quality: High (technical content)

## Troubleshooting

### Ollama Not Starting

**Windows:**
```cmd
# Check if Ollama is running
tasklist | findstr ollama

# If not running, start it
ollama serve
```

**macOS/Linux:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# If not running, start it
ollama serve
```

### Model Download Issues

```bash
# Check available models
ollama list

# Re-download a model
ollama pull llama3.2:3b

# Remove and re-download
ollama rm llama3.2:3b
ollama pull llama3.2:3b
```

### API Connection Issues

1. **Check if Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Check backend logs:**
   ```bash
   python main.py
   ```

3. **Test Ollama health endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/ollama/health
   ```

### Memory Issues

If you get out-of-memory errors:

1. **Use smaller models:**
   - Switch to `llama3.2:1b` instead of `llama3.2:3b`
   - Avoid 7B parameter models on systems with <8GB RAM

2. **Close other applications:**
   - Free up RAM before running draft generation

3. **Restart Ollama:**
   ```bash
   # Stop Ollama
   pkill ollama
   
   # Start again
   ollama serve
   ```

## Performance Tips

1. **First-time model loading:**
   - The first request to a model takes longer (model loading)
   - Subsequent requests are much faster

2. **Model caching:**
   - Models stay in memory after first use
   - Keep Ollama running for better performance

3. **Batch processing:**
   - Generate multiple drafts in one session
   - Avoid restarting Ollama between requests

## Security Notes

- Ollama runs locally - no data is sent to external servers
- All patent descriptions and generated drafts stay on your machine
- No internet connection required after model download

## Support

If you encounter issues:

1. Check the [Ollama documentation](https://ollama.ai/docs)
2. Run the test suite: `python test_draft_generation.py`
3. Check backend logs for error messages
4. Verify Ollama is running: `ollama list`

## Next Steps

Once Ollama is set up:

1. Try generating different types of patents (utility, software, medical)
2. Experiment with different models
3. Use the advanced options in the frontend
4. Download and review generated drafts
