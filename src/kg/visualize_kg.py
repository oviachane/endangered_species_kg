from rdflib import Graph
from pyvis.network import Network
import os

def visualize(ttl_file, output_html):
    print(f"Loading RDF Graph from {ttl_file}...")
    g = Graph()
    g.parse(ttl_file, format="turtle")
    
    # Create an interactive network
    net = Network(height="800px", width="100%", directed=True, notebook=False, bgcolor="#222222", font_color="white")
    
    print("Building nodes and edges...")
    
    # We limit to 300 edges to avoid making the browser lag or look too messy
    count = 0
    for s, p, o in g:
        if count > 300: break
        
        # Shorten the URIs to make them readable on the visual graph
        subj = str(s).split('/')[-1]
        pred = str(p).split('/')[-1].split('#')[-1]
        
        if hasattr(o, "value"): # This handles Literals (strings)
            obj = str(o.value)
        else:
            obj = str(o).split('/')[-1]
            
        # Give different colors to standard strings (Labels) vs structural nodes
        s_color = "#97c2fc"
        o_color = "#e2bbf0" if hasattr(o, "value") else "#f6a894"
        
        net.add_node(subj, label=subj, title=subj, color=s_color)
        net.add_node(obj, label=obj, title=obj, color=o_color)
        net.add_edge(subj, obj, title=pred, label=pred, color="#aaaaaa")
        
        count += 1
        
    # Use physics to spread the graph out nicely
    net.force_atlas_2based()
    
    # Save the file
    os.makedirs(os.path.dirname(output_html), exist_ok=True)
    net.write_html(output_html)
    print(f"\n✅ Interactive visualization successfully saved to: {output_html}")
    print("Double-click this HTML file in your file explorer to open it in your browser!")
    
if __name__ == "__main__":
    # Get project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    TTL_FILE = os.path.join(base_dir, "kg_artifacts", "initial_graph.ttl")
    HTML_FILE = os.path.join(base_dir, "kg_artifacts", "graph_visual.html")
    
    if os.path.exists(TTL_FILE):
        visualize(TTL_FILE, HTML_FILE)
    else:
        print(f"Error: Could not find {TTL_FILE}")
