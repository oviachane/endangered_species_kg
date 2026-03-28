import os
import time
import requests
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import OWL, RDF, RDFS

EX = Namespace("http://example.org/endangered/")
WD = Namespace("http://www.wikidata.org/entity/")

def load_graph(ttl_file):
    g = Graph()
    g.parse(ttl_file, format="turtle")
    g.bind("ex", EX)
    g.bind("wd", WD)
    g.bind("owl", OWL)
    return g

def align_and_expand(g):
    # Wikidata requires a good User-Agent or it will block us (HTTP 403/429)
    headers = {
        "User-Agent": "BotEndangeredSpeciesKG/1.0 (Student Project) python-requests/2.31"
    }
    
    # 1. Find all pure entities in our private graph
    entities_to_align = set()
    for s, p, o in g:
        if str(s).startswith("http://example.org/endangered/"):
            entities_to_align.add(s)
            
    print(f"Total entities to attempt aligning & expanding: {len(entities_to_align)}")
    
    aligned_count = 0
    total_new_triplets = 0
    
    # Temporary graph to store expansion
    expanded_g = Graph()
    
    for entity in list(entities_to_align):
        # We named the URI using the label, let's extract it to search
        label = str(entity).split('/')[-1].replace("_", " ")
        print(f"\nAligning: {label}...")
        
        # Step A: Align with Wikidata Search API
        search_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={label}&language=en&format=json"
        
        try:
            res = requests.get(search_url, headers=headers).json()
            if 'search' in res and len(res['search']) > 0:
                # Take the first best match
                match = res['search'][0]
                wd_id = match['id']
                print(f"  -> Match found! {wd_id} ({match.get('description', 'No description')})")
                
                # Add Alignment Triplet (owl:sameAs)
                wd_uri = WD[wd_id]
                expanded_g.add((entity, OWL.sameAs, wd_uri))
                aligned_count += 1
                
                # Step B: Expand (Execute SPARQL Query on Wikidata to get ~500 properties)
                sparql_query = f"""
                SELECT ?p ?o WHERE {{
                  wd:{wd_id} ?p ?o .
                }}
                LIMIT 500
                """
                
                sparql_url = "https://query.wikidata.org/sparql"
                req = requests.get(sparql_url, params={'query': sparql_query, 'format': 'json'}, headers=headers)
                
                if req.status_code == 200:
                    data = req.json()
                    results = data["results"]["bindings"]
                    for row in results:
                        p_val = row["p"]["value"]
                        o_val = row["o"]["value"]
                        
                        p_uri = URIRef(p_val)
                        if row["o"]["type"] == "uri":
                            o_uri = URIRef(o_val)
                            expanded_g.add((wd_uri, p_uri, o_uri))
                        else:
                            o_lit = Literal(o_val)
                            expanded_g.add((wd_uri, p_uri, o_lit))
                            
                    print(f"  -> Expansion: Added {len(results)} new Wikidata triplets.")
                    total_new_triplets += len(results)
                else:
                    print(f"  -> Failed to expand {wd_id}. Status: {req.status_code}")
                    if req.status_code == 429:
                        print("     [!] Server Rate Limited us! Sleeping 10 seconds...")
                        time.sleep(10)
            else:
                print("  -> No solid match found in Wikidata.")
        except Exception as e:
            print(f"  -> Request error: {e}")
            
        # VERY IMPORTANT: Always sleep between Wikidata requests to avoid bans
        time.sleep(1.5)
        
    # Merge expansion with the original private graph
    g += expanded_g
    
    print(f"\n====================================")
    print(f"Alignment Complete: {aligned_count} entities aligned with Wikidata.")
    print(f"Expansion Complete: Pulled {total_new_triplets} new triplets into our Graph.")
    print(f"New Total Graph Size: {len(g)} triplets (Goal: 50,000+)")
    
    return g

if __name__ == "__main__":
    ttl_path = "/home/ovia/web_data_project/endangered_species_kg/kg_artifacts/initial_graph.ttl"
    out_path = "/home/ovia/web_data_project/endangered_species_kg/kg_artifacts/expanded_graph.ttl"
    
    if os.path.exists(ttl_path):
        g = load_graph(ttl_path)
        g = align_and_expand(g)
        g.serialize(destination=out_path, format="turtle")
        print(f"\n✅ Massive Expanded Graph saved to {out_path}")
    else:
        print(f"Error: Could not find {ttl_path}")
