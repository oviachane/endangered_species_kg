import os
from owlready2 import *
from rdflib import Graph, URIRef, RDF, Namespace

# Get project root
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load original TTL into rdflib
g = Graph()
ttl_path = os.path.join(base_dir, "kg_artifacts", "expanded_graph_2hop.ttl")
g.parse(ttl_path, format="turtle")

# Load OWL via Owlready2
onto_path = os.path.join(base_dir, "kg_artifacts", "kg_inferred.owl")
onto = get_ontology(f"file://{onto_path}").load()

print("Running reasoner...")
with onto:
    sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)

# Namespaces
EX = Namespace("http://example.org/endangered/")
EX_INF = Namespace("http://example.org/endangered_inference.owl#")

# Map Inferred class Habitat to our RDF graph
print("Materializing inferences...")
habitat_count = 0
for i in onto.individuals():
    # Check if the individual is inferred as a Habitat
    if onto.Habitat in i.is_a:
        # Convert to rdflib triple
        subj = URIRef(EX + i.name)
        g.add((subj, RDF.type, URIRef(EX + "Habitat")))
        habitat_count += 1

print(f"Materialized {habitat_count} Habitat triples.")

# Save the unified graph
output_path = os.path.join(base_dir, "kg_artifacts", "graph_unified.ttl")
g.serialize(destination=output_path, format="turtle")
print(f"Unified graph saved to {output_path}")
