import os
from typing import List, Tuple
from rdflib import Graph, URIRef
import requests
import json

# ----------------------------
# Configuration
# ---------------------------- 
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TTL_FILE = os.path.join(base_dir, "kg_artifacts", "graph_unified.ttl")
OLLAMA_URL = "http://localhost:11434/api/generate" 
MODEL = "llama3.2" 

MAX_PREDICATES = 80 
MAX_CLASSES = 40 
SAMPLE_TRIPLES = 20 

def ask_local_llm(prompt: str) -> str: 
    payload = { "model": MODEL, "prompt": prompt, "stream": False } 
    response = requests.post(OLLAMA_URL, json=payload) 
    if response.status_code != 200: 
        raise RuntimeError(f"Ollama API error {response.status_code}: {response.text}") 
    return response.json().get("response", "") 

def load_graph(ttl_path: str) -> Graph: 
    g = Graph() 
    g.parse(ttl_path, format="turtle")
    g.bind("wd", URIRef("http://www.wikidata.org/entity/"))
    g.bind("wdt", URIRef("http://www.wikidata.org/prop/direct/"))
    g.bind("ex", URIRef("http://example.org/endangered/"))
    print(f"Loaded {len(g)} triples from {ttl_path} (Inferences Materialized)") 
    return g 

def get_prefix_block(g: Graph) -> str: 
    ns_map = {p: str(ns) for p, ns in g.namespace_manager.namespaces()} 
    ns_map.setdefault("ex", "http://example.org/endangered/")
    ns_map.setdefault("wd", "http://www.wikidata.org/entity/")
    ns_map.setdefault("wdt", "http://www.wikidata.org/prop/direct/")
    lines = [f"PREFIX {p}: <{ns}>" for p, ns in ns_map.items() if p] 
    return "\n".join(sorted(lines)) 

def list_distinct_predicates(g: Graph) -> List[str]: 
    q = f"SELECT ?p (COUNT(?s) AS ?count) WHERE {{ ?s ?p ?o . }} GROUP BY ?p ORDER BY DESC(?count) LIMIT {MAX_PREDICATES}" 
    return [row.p.n3(g.namespace_manager) for row in g.query(q)] 

def list_distinct_classes(g: Graph) -> List[str]: 
    q = f"SELECT ?cls (COUNT(?s) AS ?count) WHERE {{ ?s a ?cls . }} GROUP BY ?cls ORDER BY DESC(?count) LIMIT {MAX_CLASSES}" 
    return [row.cls.n3(g.namespace_manager) for row in g.query(q)] 

def sample_triples(g: Graph) -> List[Tuple[str, str, str]]: 
    q = f"SELECT ?s ?p ?o WHERE {{ ?s ?p ?o . }} LIMIT {SAMPLE_TRIPLES}" 
    return [(r.s.n3(g.namespace_manager), r.p.n3(g.namespace_manager), r.o.n3(g.namespace_manager)) for r in g.query(q)] 

def build_schema_summary(g: Graph) -> str: 
    prefixes = get_prefix_block(g) 
    preds = "\n".join(f"- {p}" for p in list_distinct_predicates(g)) 
    clss = "\n".join(f"- {c}" for c in list_distinct_classes(g)) 
    samples = "\n".join(f"- {s} {p} {o}" for s, p, o in sample_triples(g)) 

    return f"{prefixes}\n\n# Predicates\n{preds}\n\n# Classes\n{clss}\n\n# Sample triples\n{samples}".strip() 

SPARQL_INSTRUCTIONS = """
You are a strict SPARQL code generator. DO NOT answer manually.
Translate the QUESTION into a valid SPARQL 1.1 SELECT query for the RDF graph.
Follow strictly: 
- Return ONLY the SPARQL query in a single fenced code block labeled ```sparql
- Do NOT use invalid SQL syntax like 'RETURNing'. Use standard SPARQL.

EXAMPLES:
Question: "What is the rdf:type of the subject that has the rdfs:label 'pandas'?"
```sparql
SELECT ?type WHERE { ?s rdfs:label ?lbl . FILTER(lcase(str(?lbl)) = "pandas") . ?s rdf:type ?type . } LIMIT 10
```

Question: "List subjects that are of type ex:Organization."
```sparql
SELECT ?s WHERE { ?s rdf:type ex:Organization . } LIMIT 10
```

Question: "Find all subjects that are considered as Habitat."
```sparql
SELECT ?s WHERE { ?s rdf:type ex:Habitat . } LIMIT 20
```

Question: "What are the labels of subjects of type ex:Person?"
```sparql
SELECT ?label WHERE { ?s rdf:type ex:Person . ?s rdfs:label ?label . } LIMIT 10
```

Question: "Find entities mentioned in the climate-change article."
```sparql
SELECT ?entity WHERE { ?s rdfs:label ?lbl . FILTER(contains(lcase(str(?lbl)), "climate-change")) . ?s ex:mentionedIn ?entity . }
```

Question: "What is the conservation status of Blue-winged Macaw?"
```sparql
SELECT ?status WHERE { ?s rdfs:label ?lbl . FILTER(lcase(str(?lbl)) = "blue-winged macaw") . ?s wdt:P141 ?status . } LIMIT 10
```
"""

def extract_sparql(text: str) -> str: 
    m = re.search(r"```(?:sparql)?\s*(.*?)```", text, re.IGNORECASE | re.DOTALL) 
    query = m.group(1).strip() if m else text.strip() 
    # Auto-patch rdflib strict literal matching for small LLMs
    query = re.sub(
        r'rdfs:label\s+([\"\'][^\"]+[\"\'])(?:\@[a-zA-Z]+)?',
        r'rdfs:label ?__lbl . FILTER(lcase(str(?__lbl)) = lcase(\1))',
        query
    )
    return query

def generate_sparql(question: str, schema: str) -> str: 
    return extract_sparql(ask_local_llm(f"{SPARQL_INSTRUCTIONS}\n\nSCHEMA SUMMARY:\n{schema}\n\nQUESTION:\n{question}")) 

def run_sparql(g: Graph, query: str) -> Tuple[List[str], List[Tuple]]: 
    res = g.query(query) 
    return [str(v) for v in res.vars], [tuple(str(cell) for cell in r) for r in res] 

def repair_sparql(schema: str, question: str, bad_q: str, err: str) -> str: 
    prompt = f"You are a strict SPARQL generator. DO NOT answer manually. The previous SPARQL failed.\nSCHEMA SUMMARY:\n{schema}\nQUESTION:\n{question}\nBAD SPARQL:\n{bad_q}\nERROR MESSAGE:\n{err}\nReturn ONLY the corrected SPARQL in a ```sparql block."
    return extract_sparql(ask_local_llm(prompt)) 

def answer_with_rag(g: Graph, schema: str, question: str) -> dict: 
    sparql = generate_sparql(question, schema) 
    try: 
        v, r = run_sparql(g, sparql) 
        return {"query": sparql, "rows": r, "repaired": False, "error": None} 
    except Exception as e: 
        rep = repair_sparql(schema, question, sparql, str(e)) 
        try: 
            v, r = run_sparql(g, rep) 
            return {"query": rep, "rows": r, "repaired": True, "error": None} 
        except Exception as e2: 
            return {"query": rep, "rows": [], "repaired": True, "error": str(e2)} 

def generate_final_answer(question: str, sparql: str, rows: List[Tuple]) -> str:
    if not rows:
        data_str = "No data found in the knowledge graph for this query."
    else:
        # Pass more items for full list synthesis
        data_str = "\n".join(["- " + " | ".join(r) for r in rows[:40]])
        
    prompt = f"""You are a strict data formatter. Convert the provided DATA into a short English response answering the QUESTION.
CRITICAL RULES:
1. DO NOT use your internal knowledge! 
2. You MUST use ALL the unique items provided in the list below. Do not pick just one.
3. Extract ONLY the last word of URIs (e.g. 'http://example.org/endangered/Person' -> 'Person').
4. Always answer with a complete, natural sentence.
5. If you see a Wikidata ID (Q-code), use this MAP: 
   - Q211005: Least Concern
   - Q11394: Endangered
   - Q219127: Critically Endangered
   - Q7191: Near Threatened
   - Q278113: Vulnerable
   - Q123068: Extinct (only if this exact code appears!)

QUESTION: {question}

DATA RETRIEVED:
{data_str}

STRICT FORMATTED ANSWER:"""
    return ask_local_llm(prompt)

if __name__ == "__main__": 
    print("Initializing NL-to-SPARQL RAG Engine...")
    G = load_graph(TTL_FILE) 
    schema = build_schema_summary(G) 
    
    print("\n--- Baseline vs RAG Interactive Demo ---")
    q = input("Question (e.g. 'What is the type of Panda?'): ").strip() 
    
    print("\n[Baseline - Direct LLM (No RAG)]")
    print(ask_local_llm(q)) 
    
    print("\n[RAG - SPARQL Generation & Self-Repair]") 
    res = answer_with_rag(G, schema, q) 
    print(f"\nSPARQL Used:\n{res['query']}\n\nRepaired: {res['repaired']}")
    if res.get("error"): 
        print("Error:", res["error"])
    else: 
        print("\nRaw SPARQL Results:")
        if not res["rows"]:
            print("  (Empty)")
        else:
            for row in res["rows"][:10]: 
                print(" | ".join(row))
        print("\n[Final Natural Language Response]")
        final_ans = generate_final_answer(q, res['query'], res['rows'])
        print(final_ans)
