# RAG (Retrieval-Augmented Generation)

Based on this documentation: https://www.stephane-robert.info/docs/developper/programmation/python/rag-introduction/

<!-- TOC -->
* [RAG (Retrieval-Augmented Generation)](#rag-retrieval-augmented-generation)
  * [Collect and clean the content](#collect-and-clean-the-content)
  * [Clean the text](#clean-the-text)
<!-- TOC -->

## Collect and clean the content

**Trafilatura** is an open-source Python package and command-line tool designed to crawl web pages, extract main text content, and strip away boilerplate noise like ads, navigation bars, and footers.

Install:
```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install trafilatura==2.0.0 lxml-html-clean==0.4.5
```

Create script to extract content from web pages: `extract-html-content-for-rag.py`

Execute it
```shell
python extract-html-content-for-rag.py
```

Corpus is created in `corpus/doc_000.json`

## Clean the text

Clean invisible characters, repeated spaces, residual HTML, and inconsistent Unicode encoding.

Create script to clean the text: `python clean-text-for-rag.py`

**We use a custom script in this project, but for true project, use a professional tool like spaCy or NLTK**
