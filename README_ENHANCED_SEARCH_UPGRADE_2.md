## Overview

The patent search system has been enhanced to provide better relevance, richer context, and more flexible search options for researchers and patent analysts.

## Completed Stories

### Add Snippet Generation

- Updated `embed_tfidf.py` and `embed_semantic.py` to return contextual snippets.
- Modified `search_cli_enhanced.py` to display snippets for each result.
- Added utility in `search_utils.py` to extract and highlight relevant sections.

**Result:**  
Each search result now shows a short, contextually relevant snippet of the patent text with highlighted query terms.

---

### Improve Metadata in Results

- Ensured `chunks.jsonl` includes metadata such as `doc_id`, `title`, and `pub_date`.
- Updated search functions to include this metadata in their output.
- Improved CLI output formatting for better readability.

**Result:**  
Search results now display the title, document type (grant/application), and document ID.

---

### Add Re-Ranking Step

- Implemented keyword overlap scoring (Jaccard similarity).
- Combined semantic and keyword scores with tunable weighting.
- Benchmarked results against baseline semantic search.

**Result:**  
Improved relevance by prioritizing documents that match both conceptually and with keyword overlap.

---

### Add Query Logging and Evaluation

- Implemented query logging to JSONL files with timestamps and modes.
- Added CLI flag `--log` to toggle logging.
- Built log analysis script to generate query usage statistics.

**Result:**  
Developers and analysts can track search trends and evaluate system performance over time.

---

### Add Batch Query Support

- Enabled batch query processing from a file.
- Results can be saved in CSV or JSON format.
- Added performance benchmarking and summary statistics.

**Result:**  
Allows testing multiple queries at once, collecting data for performance and relevance evaluation.

---

## New and Updated Files

|File|Purpose|
|---|---|
|`search_utils.py`|Snippet generation, metadata loading, re-ranking logic|
|`search_cli_enhanced.py`|CLI supporting snippets, re-ranking, logging|
|`batch_search.py`|Batch query processor|
|`analyze_logs.py`|Query log analysis tool|
|`demo_enhanced_features.py`|Demo script showing new features|
|`test_enhanced_search.py`|Automated tests for new features|

---

## Key Features

- Contextual snippet generation with term highlighting
- Rich metadata for results (titles, IDs, types)
- Semantic + keyword re-ranking with configurable weights
- Query logging and analysis tools
- Batch query processing and benchmarking

---

## Usage Examples

**Search with snippets:**

`python search_cli_enhanced.py "machine learning" --mode tfidf --top_k 3`

**Semantic search with re-ranking:**

`python search_cli_enhanced.py "neural network" --mode semantic --rerank`

**Batch processing:**

`python batch_search.py sample_queries.txt --mode hybrid --top_k 5`

**Log analysis:**

`python analyze_logs.py query_log.jsonl`
