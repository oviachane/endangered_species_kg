import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD
import urllib.parse
import os

def create_initial_kb(csv_file, output_ttl):
    print("Loading extracted entities...")
    df = pd.read_csv(csv_file)
    
    # Initialize Graph and Namespaces
    g = Graph()
    EX = Namespace("http://example.org/endangered/")
    g.bind("ex", EX)
    
    # Map spaCy entity types to our Custom RDF Classes
    classes = {
        "ORG": EX.Organization,
        "GPE": EX.Location,
        "LOC": EX.Location,
        "PERSON": EX.Person,
        "DATE": EX.Date,
        "EVENT": EX.Event,
        "NORP": EX.Group
    }
    
    for idx, row in df.iterrows():
        # Clean and encode entity name for URI
        raw_name = str(row['Entity']).strip()
        ent_uri_part = urllib.parse.quote(raw_name.replace(" ", "_"))
        ent_type = str(row['Type']).strip()
        url = str(row['Source_URL']).strip()
        
        # Create Node reference
        node = EX[ent_uri_part]
        
        
        # Triplet 1: Define its class (node is a Location)
        rdf_class = classes.get(ent_type, EX.Entity)
        g.add((node, RDF.type, rdf_class))
        
        # Triplet 2: Add a human-readable label
        g.add((node, RDFS.label, Literal(raw_name, datatype=XSD.string)))
        
        # Triplet 3: Where was this mentioned?
        g.add((node, EX.mentionedIn, URIRef(url)))

    print(f"Graph successfully created with {len(g)} triplets.")
    
    # Save to Turtle format
    os.makedirs(os.path.dirname(output_ttl), exist_ok=True)
    g.serialize(destination=output_ttl, format="turtle")
    print(f"Saved initial Knowledge Base to: {output_ttl}")

if __name__ == "__main__":
    # Chemins relatifs
    INPUT_CSV = "data/extracted_knowledge.csv"
    OUTPUT_TTL = "kg_artifacts/initial_graph.ttl"
    
    if os.path.exists(INPUT_CSV):
        create_initial_kb(INPUT_CSV, OUTPUT_TTL)
    else:
        print(f"Error: {INPUT_CSV} not found.")
