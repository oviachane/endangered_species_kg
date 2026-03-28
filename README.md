# 🌿 Endangered Species Knowledge Graph & RAG Pipeline 🤖

[![Project Status](https://img.shields.io/badge/Project%20Status-Submission%20Ready-success.svg)](https://github.com/oviachane/endangered_species_kg)
[![License](https://img.shields.io/badge/License-Academic-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

A multi-phase Semantic Web ecosystem for **Automated Biodiversity Knowledge Discovery**. This system transforms unstructured environmental news into a logic-certified Knowledge Graph (53,000+ triplets), enriched via Wikidata, and queryable through a local LLM-powered RAG agent with SPARQL self-repair.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Web Sources: WWF/Mongabay] -->|httpx / trafilatura| B(Phase 1: NER Extraction)
    B -->|rdflib| C(Phase 2: Initial KG Construction)
    C -->|SPARQL 2-Hop| D{Wikidata Alignment}
    D -->|TTL| E(Phase 3: SWRL Reasoning)
    E -->|RDF/OWL| F[Unified Knowledge Graph]
    F -->|PyKEEN| G(Phase 4: KGE Embeddings)
    F -->|Ollama / Llama 3.2| H(Phase 5: SPARQL-RAG Agent)
    H -->|Natural Language| I[User Interface]
```

---

## 📸 Project Showcase (Screenshots Needed)

> [!IMPORTANT]
> To finalize the documentation, please replace the placeholders below with the requested screenshots.

### 1. Knowledge Graph Visualization
![Graph Visualization Placeholder](path/to/your/graph_viz.png)
*Visualizing the 53,000-triplet semantic space using the interactive HTML explorer.*

### 2. RAG Agent in Action (Self-Repair)
![RAG Demo Placeholder](path/to/your/rag_demo.png)
*The system successfully translating "Find subjects that are Habitat" into a SPARQL query and correcting itself after a syntax error.*

### 3. KGE Performance Metrics
![KGE Metrics Placeholder](path/to/your/kge_metrics.png)
*Comparative training results for TransE vs ComplEx models using PyKEEN.*

### 4. Semantic Learning (KGE Analysis)
The system learns latent relationships between entities even without explicit rules. Using the `Nearest Neighbors` tool, we can observe the model's "common sense":

- **Target: Giant Panda (wd:Q242)** 🎋
  - ✅ 近隣 (Similarity: 0.52): *Republic of China* (Native Region)
  - ✅ 近隣 (Similarity: 0.52): *Animal Habitat* (Ontological Context)
  - ✅ 近隣 (Similarity: 0.51): *List of Endangered Species* (Correct Taxonomic Status!)

- **Target: China (wd:Q148)** 🌏
  - ✅ 近隣 (Similarity: 0.49): *State in Asia* (Geographic Reality)

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

## 📊 Technical Specifications (Submission Ready)

- **KB Statistics**: [kb_statistics.json](kg_artifacts/kb_statistics.json) (Triplets, Entities, Predicates).
- **Core Ontology**: [ontology.ttl](kg_artifacts/ontology.ttl) (Formal class definitions).
- **Reasoning Materialization**: Inferred relations stored in `graph_unified.ttl`.
- **KGE Reproducibility**: Dataset splits located in `data/kge_splits/`.

### 🛡️ Key Innovations
- **Self-Repair SPARQL Loop**: Intercepts LLM hallucinations and forces 100% syntactical accuracy.
- **2-Hop BFS Expansion**: Strategically scales the domain knowledge from 300 to 53,000 facts.
- **Privacy-First RAG**: No data ever leaves your machine; fully local Llama-3.2 inference.

---

*Project developed for the **Semantic Web & Web Data** University Final Project (2025-2026).*
*Timothée JOLIOT & Ovia CHANEMOUGANANDAM*
