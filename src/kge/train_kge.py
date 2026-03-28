import os
import torch
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
import pandas as pd
import rdflib

def train_and_evaluate(ttl_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    print("--- Phase 4: Knowledge Graph Embeddings (KGE) ---\n")
    print(f"1. Loading RDF Graph from {ttl_path}...")
    
    g = rdflib.Graph()
    g.parse(ttl_path, format="turtle")
    
    # We extract triplets from our graph to feed them into PyKEEN
    triples = []
    for s, p, o in g:
        subj = str(s).split('/')[-1]
        pred = str(p).split('/')[-1].split('#')[-1]
        obj = str(o.value) if hasattr(o, "value") else str(o).split('/')[-1]
        triples.append([subj, pred, obj])
        
    df = pd.DataFrame(triples, columns=["head", "relation", "tail"])
    # Clean possible empty strings or None values
    df = df.dropna()
    df = df[(df.T != '').any()]
    
    print(f" -> Extracted {len(df)} clean triplets for AI Training.\n")
    
    print("2. Formatting and Splitting Dataset (Train/Valid/Test)...")
    tf = TriplesFactory.from_labeled_triples(df[["head", "relation", "tail"]].values)
    training, testing, validation = tf.split([0.8, 0.1, 0.1], random_state=42)
    
    print("\n3. Training Model 1: TransE (Translating Embeddings)...")
    result_transe = pipeline(
        training=training,
        testing=testing,
        validation=validation,
        model='TransE',
        training_kwargs=dict(num_epochs=10),
        evaluator_kwargs=dict(batch_size=16),
        random_seed=42,
    )
    
    print("\n4. Training Model 2: ComplEx (Complex Embeddings)...")
    result_complex = pipeline(
        training=training,
        testing=testing,
        validation=validation,
        model='ComplEx',
        training_kwargs=dict(num_epochs=10),
        evaluator_kwargs=dict(batch_size=4),
        random_seed=42,
    )
    
    print("\n============= Evaluation Results =============")
    
    def print_metrics(name, res):
        metrics = res.metric_results.to_df()
        
        # PyKEEN 1.11+ removed the 'Type' column for evaluation metrics
        if 'Type' in metrics.columns:
            df_slice = metrics[(metrics['Side'] == 'both') & (metrics['Type'] == 'realistic')]
        else:
            df_slice = metrics[metrics['Side'] == 'both']
            
        def get_val(metric_name):
            try:
                return df_slice[df_slice['Metric'] == metric_name]['Value'].values[0]
            except IndexError:
                return 0.0
        
        mrr = get_val('inverse_harmonic_mean_rank')
        mr = get_val('arithmetic_mean_rank')
        hits1 = get_val('hits_at_1')
        hits3 = get_val('hits_at_3')
        hits10 = get_val('hits_at_10')
        
        print(f"--- Model: {name} ---")
        print(f"MRR (Mean Reciprocal Rank) : {mrr:.4f}")
        print(f"MR (Mean Rank)  : {mr:.4f}")
        print(f"Hits@1  : {hits1:.4f}")
        print(f"Hits@3  : {hits3:.4f}")
        print(f"Hits@10 : {hits10:.4f}\n")
        
    print_metrics("TransE", result_transe)
    print_metrics("ComplEx", result_complex)
    
    print("Saving Models and Data Splits to disk...")
    result_transe.save_to_directory(os.path.join(out_dir, "transe"))
    result_complex.save_to_directory(os.path.join(out_dir, "complex"))
    
    # Export splits for grading compliance
    split_dir = os.path.join(os.path.dirname(out_dir), "kge_splits")
    os.makedirs(split_dir, exist_ok=True)
    training.to_path_binary(os.path.join(split_dir, "train.txt"))
    testing.to_path_binary(os.path.join(split_dir, "test.txt"))
    validation.to_path_binary(os.path.join(split_dir, "valid.txt"))
    
    print(f"\n✅ All Phase 4 Models successfully trained and saved to {out_dir}")
    print(f"✅ Data splits exported to {split_dir}")

if __name__ == "__main__":
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    # Training on the MASSIVE 53k graph. Evaluation is highly restricted to prevent OOM Kills.
    TTL_FILE = "/home/ovia/web_data_project/endangered_species_kg/kg_artifacts/expanded_graph_2hop.ttl"
    OUT_DIR = "/home/ovia/web_data_project/endangered_species_kg/kg_artifacts/kge_results"
    
    if os.path.exists(TTL_FILE):
        train_and_evaluate(TTL_FILE, OUT_DIR)
    else:
        print(f"Error: Could not find {TTL_FILE}")
