# PDF Download and Extraction Pipeline

This project consists of Python scripts for downloading PDFs from DigiKey's product pages, organizing them, and extracting text, images, and tables from each PDF. Below is a description of each script and its usage.

---

## Scripts Overview

### 00-download_pdfs.py

**Purpose**:  
Downloads PDFs from DigiKey product pages and cleans any corrupted files (e.g., files that aren't actual PDFs).

**Process**:
1. Reads URLs from `urls.txt`, which contains links to various product categories on DigiKey (e.g., [Controller Accessories](https://www.digikey.com/en/products/filter/controllers/controller-accessories/816)).
2. Generates links for each page in the product category, with pagination in the format:  
   `link1,page1`, `link1,page2`, `link1,page3`, etc.  
   Each page is assumed to contain up to 100 PDFs.
3. Downloads the PDFs to the specified output path, handling errors as necessary.

**Dependencies**:  
Uses helper functions in `aux_download_pdfs.py`.

---

### 01-extract_pdf.py

**Purpose**:  
Processes downloaded PDFs, extracting their text, images, and tables into a structured folder format.

**Process**:
1. Reads from the PDF directory.
2. Creates a corresponding directory structure for text output:
   ```
          data
          ├── pdfs
          │   ├── label1..n
          │        ├── pdf1..n
          └── txt
              ├── label1..n
                   ├── pdf1..n
                        ├── text
                        ├── images1..n
                        ├── tables
   ```

4. Each PDF file’s content is saved separately, with text, images, and tables extracted into their respective subfolders.

**Dependencies**:  
Uses helper functions in `aux_extract_pdf.py`.

---


01-image to text

01 table to text


-----------------

# Text Retrieval Utilities

This repository contains two utility modules for text retrieval:

- **`bm25_utils.py`**: Build, query, and manage a BM25 index over a corpus of text files.
- **`word2vec_utils.py`**: Expand queries via Word2Vec, compute TF-IDF–weighted embeddings, and retrieve top-K documents by cosine similarity in a VSM space.

---

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [BM25 Utilities](#bm25-utilities)
   - [Overview](#overview)
   - [Functions](#functions)
   - [Usage Example](#usage-example)
4. [Word2Vec Utilities](#word2vec-utilities)
   - [Overview](#overview-1)
   - [Functions](#functions-1)
   - [Usage Example](#usage-example-1)
5. [License](#license)

---

## Requirements

- Python 3.8+
- `bm25s` (BM25 library)
- `scikit-learn`
- `numpy`
- Custom module `aux_vsm` (for Word2Vec & TF-IDF utilities)

```bash
pip install bm25s scikit-learn numpy
# ensure aux_vsm is in your PYTHONPATH or installed as a package
```

## Word2Vec Utilities

```python
# Overview
# word2vec_utils.py offers methods to:
# 1. Filter candidate terms by similarity and IDF
# 2. Expand a query by retrieving similar words per token
# 3. Embed a query using TF-IDF weighted average of vectors
# 4. Retrieve top-K documents by cosine similarity
# 5. Run an end-to-end query with run_word2vec_query

# Functions
# - filter_expansion_candidates(sims: List[Tuple[str, float]], idf: Dict[str, float], ...) -> List[str]
# - expand_query_terms(query_tokens: List[str], model: Any, idf: Dict[str, float], ...) -> List[str]
# - embed_query(model: Any, query: str, idf_cached: Dict[str, float], tokenize_fn: Callable, ...) -> Dict[str, Any]
# - retrieve_top_k_documents(query_vector: np.ndarray, corpus_vectors: Dict[str, np.ndarray], top_k: int) -> List[Dict[str, Any]]
# - run_word2vec_query(paths: Dict[str, Path], query: str, top_k: int, use_expansion: bool) -> List[Dict[str, Any]]

# Usage Example
from pathlib import Path
from word2vec_utils import run_word2vec_query

paths = {
    'word2vec': Path('models/word2vec-google-news.bin'),
    'idf_cache': Path('data/idf_cache.pkl'),
    'word2vec_vsm': Path('data/corpus_vectors.pkl'),
    'pdf_folder': Path('data/text_corpus')
}

results = run_word2vec_query(paths, query='battery temperature behavior', top_k=5)
for r in results:
    print(f"Rank {r['rank']} (doc: {r['doc_id']}, score: {r['score']:.4f})")
```

## BM25 Utilities

```python
# Overview
# bm25_utils.py provides tools to:
# 1. Load a corpus of text files where each subfolder contains a file named after the folder.
# 2. Create and persist a BM25 index along with metadata (corpus and file mappings).
# 3. Query the index and obtain structured results (rank, score, directory names, document text).
# 4. Run an end-to-end BM25 query with run_bm25_query

# Functions
# - load_corpus_bm25(corpus_path: Path) -> Tuple[List[str], List[str]]
# - create_bm25_index(input_path: Path, retriever_path: Path) -> bm25s.BM25
# - query_bm25(retriever_path: Path, retriever: bm25s.BM25, query: str, k: int, corpus: Optional[List[str]]) -> List[Dict]
# - run_bm25_query(paths: Dict[str, Path], query: str, top_k: int) -> List[Dict]

# Usage Example
from pathlib import Path
from bm25_utils import run_bm25_query

paths = {
    'pdf_folder': Path('data/text_corpus'),
    'retriever': Path('data/bm25_index')
}

results = run_bm25_query(paths, query='machine learning fundamentals', top_k=5)
for r in results:
    print(f"Rank {r['rank']} (score: {r['score']:.2f}) - {r['grandparent']} - {r['parent']}")