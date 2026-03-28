import os
import torch
import torch.nn.functional as F
import pandas as pd
import numpy as np

# ----------------------------
# Configuration
# ----------------------------
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(base_dir, "kg_artifacts", "kge_results", "transe", "trained_model.pkl")
TRIPLES_DIR = os.path.join(base_dir, "kg_artifacts", "kge_results", "transe", "training_triples")

def load_transe_model():
    """Load the trained PyKEEN model."""
    print(f"Loading model from {MODEL_PATH}...")
    # Fix for PyTorch 2.6+ which defaults weights_only=True
    model = torch.load(MODEL_PATH, map_location=torch.device('cpu'), weights_only=False)
    return model

def get_nearest_neighbors(model, entity_name, tf, k=5):
    """Find the k nearest neighbors of an entity in the vector space."""
    # 1. Get embedding for the target entity
    entity_id = tf.entity_to_id.get(entity_name)
    if entity_id is None:
        print(f"Entity '{entity_name}' not found in the training triples.")
        return []

    # Access embeddings directly from the model
    # Note: In PyKEEN Model, entity_embeddings is often an Embedding instance
    all_embeddings = model.entity_representations[0](indices=None)
    target_embedding = all_embeddings[entity_id].unsqueeze(0)

    # 2. Calculate cosine similarity against all other entities
    similarities = F.cosine_similarity(target_embedding, all_embeddings)
    
    # 3. Get Top-K indices
    # We use k+1 because the entity itself will be at rank 0 (similarity = 1.0)
    scores, indices = torch.topk(similarities, k + 1)
    
    results = []
    id_to_entity = {v: k for k, v in tf.entity_to_id.items()}
    
    for i in range(1, len(indices)): # Skip the first one (itself)
        idx = indices[i].item()
        score = scores[i].item()
        results.append((id_to_entity[idx], score))
        
    return results

def run_tsne_visualization(model, tf, output_path):
    """Generate a t-SNE plot if sklearn and matplotlib are available."""
    try:
        from sklearn.manifold import TSNE
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n[!] Skipping t-SNE: sklearn or matplotlib not installed.")
        return

    print("\nGenerating t-SNE visualization (this may take a minute for 39k entities)...")
    
    # Sub-sample to keep it fast
    N_SAMPLE = 1000
    all_embeddings = model.entity_representations[0](indices=None).detach().numpy()
    
    if len(all_embeddings) > N_SAMPLE:
        indices = np.random.choice(len(all_embeddings), N_SAMPLE, replace=False)
        sampled_embeddings = all_embeddings[indices]
    else:
        sampled_embeddings = all_embeddings

    tsne = TSNE(n_components=2, perplexity=30, n_iter=300, random_state=42)
    embeddings_2d = tsne.fit_transform(sampled_embeddings)

    plt.figure(figsize=(12, 8))
    plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], alpha=0.5, s=10, c='teal')
    plt.title("t-SNE Projection of Endangered Species Knowledge Graph Embeddings (TransE)")
    plt.xlabel("Dimension 1")
    plt.ylabel("Dimension 2")
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.savefig(output_path)
    print(f"t-SNE plot saved to {output_path}")

if __name__ == "__main__":
    # 1. Load Data & Model
    # Since we saved the trained model pkl, we need to load the mapping too
    # We can reconstruct a dummy triples factory to get the label-to-id mapping
    # Note: In a production script, we'd load the .tsv files from the export
    
    # Let's use the entity_to_id mapping if it exists
    id_map_path = os.path.join(TRIPLES_DIR, "entity_to_id.tsv.gz")
    if not os.path.exists(id_map_path):
        # Fallback to loading the graph if no mapping export
        from rdflib import Graph
        print("Mapping file not found, reconstructing from graph...")
        # (This is just a mockup fallback)
    
    # For this script, we assume the user has the mapping or we can load a factory
    # PyKEEN's torch.load(model) includes the mapping in model.triples_factory if it was saved
    model = load_transe_model()
    
    # Try to extract the mapping from the model itself
    if hasattr(model, 'triples_factory') and model.triples_factory:
        tf = model.triples_factory
    else:
        # Reconstruct from the existing tsv mapping exported by train_kge.py
        entity_map = pd.read_csv(id_map_path, sep="\t", compression='gzip')
        class TFProxy: pass
        tf = TFProxy()
        # Ensure we use the right columns: 'id' and 'label'
        tf.entity_to_id = dict(zip(entity_map['label'], entity_map['id']))

    # 2. Demonstration: Nearest Neighbors
    targets = [
        "Q242",     # Giant Panda
        "Q184",     # Wolf
        "Q148",     # China
        "Q211005",  # Least Concern
        "Q11394"    # Endangered
    ]

    print("\n" + "="*40)
    print("  KGE SEMANTIC NEAREST NEIGHBORS (TransE)")
    print("="*40)

    id_to_label = {v: k for k, v in tf.entity_to_id.items()}

    for t in targets:
        name = t
        # Try to find a human readable label in the map
        for label, eid in tf.entity_to_id.items():
            if eid == t:
                name = label
                break
        
        print(f"\nTarget Entity: {t}")
        neighbors = get_nearest_neighbors(model, t, tf, k=5)
        if neighbors:
            for n_name, score in neighbors:
                print(f"  -> {n_name} (Sim: {score:.4f})")
    
    # 3. Visualization
    output_viz = os.path.join(base_dir, "kg_artifacts", "embeddings_tsne.png")
    run_tsne_visualization(model, tf, output_viz)
    
    print("\nAnalysis Complete. Use these neighbors to prove the 'Semantic Learning' of the Knowledge Graph!")
