from owlready2 import *
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
import os

def run_kg_reasoning(ttl_file, output_path):
    print("--- Phase 3, Part 2: SWRL Reasoning on Endangered Species KG ---\n")
    print("1. Parsing our initial RDF Graph using rdflib...")
    
    g = Graph()
    g.parse(ttl_file, format="turtle")
    
    # Prefix from our build_kg.py script
    EX_NAMESPACE = "http://example.org/endangered/"
    REF_LOCATION = URIRef(EX_NAMESPACE + "Location")
    
    # Find all locations in our graph
    location_names = []
    for s, p, o in g.triples((None, RDF.type, REF_LOCATION)):
        name = str(s).split('/')[-1]
        location_names.append(name)
        
    print(f" -> Successfully extracted {len(location_names)} Location entities from the KG.")
    
    print("\n2. Transferring to OWLReady2 Artificial Intelligence Engine...")
    onto = get_ontology("http://example.org/endangered_inference.owl")
    
    with onto:
        class Entity(Thing): pass
        class Location(Entity): pass
        class Habitat(Location): pass
        
        # Instantiate the locations dynamically into the OWL logic engine
        for loc_name in location_names:
            Location(loc_name)
            
    print("Before reasoning:")
    print(f" -> API found {len(list(onto.Location.instances()))} Locations.")
    print(f" -> API found {len(list(onto.Habitat.instances()))} Habitats.")
    
    print("\n3. Applying custom SWRL Rule: Location(?x) -> Habitat(?x)")
    with onto:
        rule = Imp()
        rule.set_as_rule("""Location(?x) -> Habitat(?x)""")
        
    print("\nRunning Pellet Reasoner...")
    sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
    
    print("\nAfter reasoning:")
    habitats = list(onto.Habitat.instances())
    print(f" -> The AI effectively deduced {len(habitats)} Habitats from logic alone!")
    
    if len(habitats) > 0:
        print(f" -> Examples of inferred Habitats: {', '.join([h.name.replace('%20', ' ') for h in habitats[:5]])}...")
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    onto.save(file=output_path, format="rdfxml")
    print(f"\n✅ Custom KG Inferrence saved to {output_path}")

if __name__ == "__main__":
    # Get the project root directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    IN_FILE = os.path.join(base_dir, "kg_artifacts", "initial_graph.ttl")
    OUT_FILE = os.path.join(base_dir, "kg_artifacts", "kg_inferred.owl")
    
    if os.path.exists(IN_FILE):
        run_kg_reasoning(IN_FILE, OUT_FILE)
    else:
        print(f"Error: {IN_FILE} not found!")
