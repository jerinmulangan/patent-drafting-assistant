#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    # Run a command and handle errors
    print(f"\n{description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed:")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    # Check if Python version is compatible
    print("Checking Python version")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"Python {version.major}.{version.minor} is not supported")
        print("   Please install Python 3.8 or higher.")
        return False
    print(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_requirements():
    # Install required packages
    if not Path("requirements.txt").exists():
        print("requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python packages"
    )

def download_nltk_data():
    # Download required NLTK data
    print("\nDownloading NLTK data")
    nltk_script = """
import nltk
try:
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)
    print("NLTK data downloaded successfully")
except Exception as e:
    print(f"NLTK download failed: {e}")
    exit(1)
"""
    
    try:
        result = subprocess.run([sys.executable, "-c", nltk_script], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"NLTK data download failed: {e.stderr}")
        return False

def check_data_files():
    # Check if data files exist
    print("\nChecking data files")
    
    required_files = [
        "data/grants/ipg250916.xml",
        "data/applications/ipa250918.xml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("Missing required data files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nMake sure the following is completed:")
        print("   1. Cloned the repository with Git LFS")
        print("   2. Downloaded the large XML files")
        print("   3. Placed them in the correct directories")
        return False
    
    print("All required data files found")
    return True

def run_pipeline():
    # Run the complete pipeline
    return run_command(
        f"{sys.executable} run_pipeline.py --build_index",
        "Running complete pipeline (parse → preprocess → build indices)"
    )

def test_installation():
    # Test that everything works
    print("\nTesting installation")
    
    test_script = """
try:
    # Test imports
    import numpy as np
    import sklearn
    import nltk
    import sentence_transformers
    import faiss
    
    # Test NLTK data
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    
    # Test project modules
    from search_utils import load_patent_metadata
    from embed_tfidf import load_texts
    from embed_semantic import load_semantic_index
    
    print("All imports successful")
    print("Installation test passed")
    
except ImportError as e:
    print(f"Import error: {e}")
    exit(1)
except Exception as e:
    print(f"Test error: {e}")
    exit(1)
"""
    
    try:
        result = subprocess.run([sys.executable, "-c", test_script], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Installation test failed: {e.stderr}")
        return False

def main():
    # Main setup function
    print("Patent Project - Complete Setup")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\nSetup failed at package installation")
        print("Try running: pip install --upgrade pip")
        sys.exit(1)
    
    # Download NLTK data
    if not download_nltk_data():
        print("\nSetup failed at NLTK data download")
        sys.exit(1)
    
    # Check data files
    if not check_data_files():
        print("\nSetup failed - missing data files")
        print("Please ensure you have the patent XML files")
        sys.exit(1)
    
    # Run pipeline
    if not run_pipeline():
        print("\nSetup failed during pipeline execution")
        print("Check the error messages above")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\nSetup failed during testing")
        sys.exit(1)
    
    print("\nSetup completed successfully")
    print("\nNext steps:")
    print("   1. Try a search: python search_cli_enhanced.py 'machine learning' --mode tfidf")
    print("   2. Run the demo: python demo_enhanced_features.py")
    print("   3. Check the README files for more examples")
    
    print("\nAvailable commands:")
    print("   - Search: python search_cli_enhanced.py 'query' --mode semantic --rerank")
    print("   - Batch: python batch_search.py sample_queries.txt --mode hybrid")
    print("   - Analysis: python analyze_logs.py query_log.jsonl")

if __name__ == "__main__":
    main()
