# 🌿 Endangered Species Knowledge Graph & RAG Pipeline 🤖

[![Project Status](https://img.shields.io/badge/Project%20Status-Submission--Ready-success.svg)](https://github.com/oviachane/endangered_species_kg)
[![Academic Year](https://img.shields.io/badge/Academic%20Year-2024--2025-blue.svg)](https://www.u-paris.fr/)

This repository contains the complete implementation for the **Semantic Web & Knowledge Discovery** final project. It features an end-to-end automated pipeline transforming unstructured conservation news into a verified, reasoned, and queryable Knowledge Graph.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Web: WWF/Mongabay] -->|Crawl & IE| B(Phase 1: Named Entity Recognition)
    B -->|RDFlib| C(Phase 2: Graph Build & Wikidata Expansion)
    C -->|SPARQL 2-Hop| D{Wikidata Alignment}
    D -->|TTL| E(Phase 3: SWRL Reasoning)
    E -->|RDF/OWL| F[Unified Knowledge Graph]
    F -->|PyKEEN| G(Phase 4: KGE Embeddings)
    F -->|Ollama / Llama 3.2| H(Phase 5: SPARQL-RAG Agent)
    H -->|Self-Repair| I[Final Natural Language Answer]
```

---

## 🚀 Installation & Usage

### ⚙️ Prerequisites
1.  **Local AI Engine**: Install [Ollama](https://ollama.com/) and download the model:
    ```bash
    ollama pull llama3.2
    ```
2.  **Environment**:
    ```bash
    pip install -r requirements.txt
    ```

### 🛠️ Execution Pipeline
Follow the sequence below to rebuild the ecosystem:

| Phase | Description | Command |
| :--- | :--- | :--- |
| **1** | Web Crawling & NER | `python src/crawl/crawler.py` |
| **2** | KG Build & Wikidata Expand | `python src/kg/align_expand_wikidata.py` |
| **3** | SWRL Reasoning Logic | `python src/reason/swrl_kg.py` |
| **4** | KGE Model Training | `python src/kge/train_kge.py` |
| **4.5**| **KGE Latent Analysis** | `python src/kge/visualize_embeddings.py` |
| **5** | **Interactive RAG Chat** | `python src/rag/rag_pipeline.py` |

---

## 📊 Technical Specifications 

- **KB Statistics**: [kb_statistics.json](kg_artifacts/kb_statistics.json) (Triplets, Entities, Predicates).
- **Core Ontology**: [ontology.ttl](kg_artifacts/ontology.ttl) (Formal class definitions).
- **Reasoning Materialization**: Inferred relations stored in `graph_unified.ttl`.
- **KGE Reproducibility**: Dataset splits located in `data/kge_splits/`.

---

## 📸 Project Showcase

### RAG Agent SPARQL Self-Repair
![RAG Screenshot](rag.png)
*Figure: The system successfully translating "Find subjects that are Habitat" into a SPARQL query and correcting itself after a syntax error.*

### Embedding Latent Space (t-SNE)
![t-SNE Embeddings](kg_artifacts/embeddings_tsne.png)
*Figure: t-SNE clustering of the 50,000-triplet Knowledge Graph embeddings.*

---

*Project developed for the **Semantic Web & Web Data** Final Project (2025-2026).*
*Timothée JOLIOT & Ovia CHANEMOUGANANDAM*
