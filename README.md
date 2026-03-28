# Endangered Species Knowledge Graph RAG Pipeline 🌿🤖

This project implements a complete Semantic Web pipeline to track and query endangered species using Web Crawling, Knowledge Graph Construction, SWRL Reasoning, and LLM-based RAG.

## 🚀 Quick Start (Complete Pipeline)

### 1. Requirements
- **Local LLM**: Install [Ollama](https://ollama.com/) and pull the model: `ollama pull llama3.2`. 
- **Hardware**: Minimum 8GB RAM (16GB recommended for RAG & KGE). 
- **Python**: `pip install -r requirements.txt`

### 2. Execution Steps
Follow this order to rebuild the Knowledge Base:
1. **Crawl & IE**: `python src/crawl/crawler.py` (Extracts entities from environmental news).
2. **Build KG**: `python src/kg/build_kg.py` (Constructs the initial RDF Graph).
3. **Align & Expand**: `python src/kg/align_expand_wikidata.py` (Links to Wikidata and pulls 50k+ triplets).
4. **Reasoning**: `python src/reason/swrl_kg.py` (Applies SWRL logic rules).
5. **Interactive RAG**: `python src/rag/rag_pipeline.py` (Chat with your Graph using Llama 3.2).

---

## 🏗️ Project Architecture

- **`kg_artifacts/`**: Contains the final Triples (`ontology.ttl`, `alignment.ttl`, `expanded_graph_2hop.ttl`) and `kb_statistics.json`.
- **`src/rag/`**: The RAG Engine featuring Statistical Schema Summary and Automated SPARQL Self-Repair.
- **`src/kge/`**: Knowledge Graph Embeddings (TransE vs ComplEx) with mandatory data splits in `data/kge_splits/`.

## 📊 Key Features
- **Statistical Schema Selection**: The RAG automatically identifies the most important ontological predicates for better query generation.
- **Self-Repair Loop**: If the LLM generates an invalid SPARQL query, the Python backend catches the error and forces the LLM to debug itself.
- **Wikidata Ingestion**: Native alignment with Wikidata ensures the graph is enriched with real-world scientific data.

---

## 📝 Project Details (Submission Compliance)
- **Ontology**: Defined in `kg_artifacts/ontology.ttl`.
- **Reasoning**: Inferred triples saved in `kg_artifacts/kg_inferred.owl`.
- **KGE Splits**: `train.txt`, `valid.txt`, `test.txt` present for reproducibility.
- **Report**: Full technical documentation in `final_report_draft.tex`.

---
*Created for the University Final Project on Web Data and Semantic Web (2025-2026).*
