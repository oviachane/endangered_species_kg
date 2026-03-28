import json
import spacy
import pandas as pd
import os

# Define the target entity types we care about for our Knowledge Graph
TARGET_ENTITIES = {"ORG", "GPE", "LOC", "PERSON", "DATE"}

def extract_entities(input_file, output_file):
    print("Loading spaCy model (en_core_web_sm)...")
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Model not found. Please run: python -m spacy download en_core_web_sm")
        return

    extracted_data = []

    print(f"Reading crawled data from {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        articles = [json.loads(line) for line in f]

    for article in articles:
        url = article["url"]
        text = article["text"]
        print(f"\nProcessing {url}...")
        
        # We only process the first 3000 chars to avoid memory issues with the transformer
        doc = nlp(text[:3000]) 
        
        found_entities = 0
        for ent in doc.ents:
            if ent.label_ in TARGET_ENTITIES:
                # remove newlines and extra spaces
                clean_name = " ".join(ent.text.split())
                if len(clean_name) > 1: # ignore single letter garbage
                    extracted_data.append({
                        "Entity": clean_name,
                        "Type": ent.label_,
                        "Source_URL": url
                    })
                    found_entities += 1
                    
        print(f" -> Found {found_entities} relevant entities in this text snippet.")

    # Save to CSV
    df = pd.DataFrame(extracted_data)
    # Deduplicate entities per URL
    df = df.drop_duplicates()
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"\nSuccess! Total unique Entity-URL pairs saved: {len(df)}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    # Chemins relatifs
    INPUT_FILE = "data/crawler_output.jsonl"
    OUTPUT_FILE = "data/extracted_knowledge.csv"
    
    if os.path.exists(INPUT_FILE):
        extract_entities(INPUT_FILE, OUTPUT_FILE)
    else:
        print(f"Error: {INPUT_FILE} not found. Run the crawler first!")
