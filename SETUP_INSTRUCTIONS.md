# Patent NLP Project - Setup Instructions

## Quick Start

```bash
# 1. Clone the repository with Git LFS
git clone <https://github.com/jerinmulangan/patent-drafting-assistant/tree/feature/semantic-search>
cd patent-nlp-project

# 2. Run the automated setup
python setup.py
```

## Manual Setup (Alternative)

### 1. Prerequisites

- **Python 3.8+** (check with `python --version`)
- **Git LFS** (for large XML files)

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install all required packages
pip install -r requirements.txt
```

### 3. Download NLTK Data

```bash
python -c "
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
"
```

### 4. Ensure Data Files

Make sure you have the patent XML files:
- `data/grants/ipg250916.xml`
- `data/applications/ipa250918.xml`

If missing, ensure you cloned with Git LFS:
```bash
git lfs pull
```

### 5. Run Pipeline

```bash
# Complete pipeline (parse → preprocess → build indices)
python run_pipeline.py --build_index
```

## Verify Installation

Test that everything works:

```bash
# Test search functionality
python search_cli_enhanced.py "machine learning" --mode tfidf --top_k 3

# Run the demo
python demo_enhanced_features.py
```

## Troubleshooting

### Memory Issues
If encountering memory errors during processing:
- The code now includes memory-efficient processing for large texts
- Try running individual steps: `python preprocess_patents.py` then `python setup_indices.py`

### Missing Dependencies
If packages fail to install:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### NLTK Download Issues
If NLTK data fails to download:
```bash
python -c "import nltk; nltk.download('all')"
```

### Git LFS Issues
If XML files are missing:
```bash
git lfs install
git lfs pull
```

## What Gets Installed

The `requirements.txt` includes:

- **numpy** - Numerical computing
- **scikit-learn** - Machine learning (TF-IDF)
- **nltk** - Natural language processing
- **sentence-transformers** - Semantic embeddings
- **faiss-cpu** - Vector similarity search

## Available Commands

After setup, you can use:

```bash
# Enhanced search with snippets and re-ranking
python search_cli_enhanced.py "neural network" --mode semantic --rerank

# Batch processing
python batch_search.py sample_queries.txt --mode hybrid

# Log analysis
python analyze_logs.py query_log.jsonl

# Compare search modes
python compare_search_modes.py --queries "AI" "machine learning"
```
