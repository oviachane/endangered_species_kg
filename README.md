# 🌿 Endangered Species Knowledge Graph & RAG Pipeline 🤖

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

### 🛡️ Key Innovations
- **Self-Repair SPARQL Loop**: Intercepts LLM hallucinations and forces 100% syntactical accuracy.
- **2-Hop BFS Expansion**: Strategically scales the domain knowledge from 300 to 53,000 facts.
- **Privacy-First RAG**: No data ever leaves your machine; fully local Llama-3.2 inference.

---

---


### RAG Agent SPARQL Self-Repair
![RAG Screenshot](rag.png)
*Figure: The system successfully translating "Find subjects that are Habitat" into a SPARQL query and correcting itself after a syntax error.*



---



*Project developed for the **Semantic Web & Web Data** Final Project (2025-2026).*
*Timothée JOLIOT & Ovia CHANEMOUGANANDAM*
