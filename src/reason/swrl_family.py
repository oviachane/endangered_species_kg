from owlready2 import *
import os

def run_family_reasoning(owl_file, output_path):
    print("--- Phase 3, Part 1: SWRL Reasoning on School's Family Ontology ---\n")
    print(f"Loading ontology from {owl_file}...")
    
    onto = get_ontology(f"file://{owl_file}").load()
    
    with onto:
        # Define OldPerson class since the rule needs to infer it
        class OldPerson(onto.Person): pass
        
    print("\nBefore reasoning:")
    for p in onto.Person.instances():
        is_old = OldPerson in p.is_a
        print(f" -> {p.name} (age {p.age}): is OldPerson? {is_old}")
    
    print("\nApplying SWRL Rule: Person(?p) ^ age(?p, ?a) ^ greaterThan(?a, 60) -> OldPerson(?p)")
    with onto:
        rule = Imp()
        rule.set_as_rule("""Person(?p), age(?p, ?a), greaterThan(?a, 60) -> OldPerson(?p)""")
        
    print("\nRunning Pellet Reasoner (HermiT doesn't support mathematical built-ins like greaterThan)...")
    sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
    
    print("\nAfter reasoning:")
    for p in onto.Person.instances():
        # Check INDIRECT_is_a to see what the reasoner inferred
        is_old = OldPerson in p.INDIRECT_is_a
        print(f" -> {p.name} (age {p.age}): is OldPerson? {is_old}")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    onto.save(file=output_path, format="rdfxml")
    print(f"\n✅ Inferred ontology saved to {output_path}")

if __name__ == "__main__":
    # Get the project root directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    IN_FILE = os.path.join(base_dir, "data", "family.owl")
    OUT_FILE = os.path.join(base_dir, "kg_artifacts", "family_inferred.owl")
    
    if os.path.exists(IN_FILE):
        run_family_reasoning(IN_FILE, OUT_FILE)
    else:
        print(f"Error: {IN_FILE} not found!")
