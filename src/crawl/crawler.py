import trafilatura
import json
import httpx
import os
import time

urls = [
    "https://www.wwf.org.uk/learn/wildlife/endangered-animals",
    "https://www.britannica.com/science/habitat-loss",
    "https://news.mongabay.com/2025/07/more-than-10000-species-on-brink-of-extinction-need-urgent-action-study/",
    "https://news.mongabay.com/2023/06/global-study-of-71000-animal-species-finds-48-are-declining/",
    "https://news.mongabay.com/short-article/2024/09/just-0-7-of-land-hosts-one-third-of-unique-endangered-species-study/",
    "https://news.mongabay.com/2020/08/why-are-some-endangered-species-ignored/",
    "https://theconversation.com/thousands-more-species-at-risk-of-extinction-than-currently-recorded-suggests-new-study-188243",
    "https://www.worldwildlife.org/resources/explainers/what-does-endangered-species-mean",
    "https://news.mongabay.com/short-article/2025/10/20-animal-species-on-the-road-to-recovery-iucn-red-list-update/",
    "https://www.nwf.org/Educational-Resources/Wildlife-Guide/Understanding-Conservation/endangered-species-success-stories",
    "https://theconversation.com/climate-change-could-cause-abrupt-biodiversity-losses-this-century-135968"
]


def crawl_and_filter(urls, output_file, min_words=400):
    valid_articles = []
    print(f"Starting crawl for {len(urls)} URLs...")
    
    for url in urls:
        print(f"Fetching: {url}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            }
            # Use httpx with a strict timeout custom User-Agent and disable SSL verification
            with httpx.Client(timeout=10.0, follow_redirects=True, verify=False, headers=headers) as client:
                response = client.get(url)
                response.raise_for_status()
                html = response.text
                
                text = trafilatura.extract(html)
                if text:
                    word_count = len(text.split())
                    if word_count >= min_words:
                        print(f" [+] SUCCESS: {word_count} words extracted.")
                        valid_articles.append({
                            "url": url,
                            "text": text,
                            "word_count": word_count
                        })
                    else:
                        print(f" [-] REJECTED: Only {word_count} words (too short).")
                else:
                    print(f" [-] FAILED: Could not extract useful text from HTML.")
        except httpx.TimeoutException:
             print(f" [-] ERROR: Connection timed out after 10 seconds.")
        except Exception as e:
             print(f" [-] ERROR: {type(e).__name__} - {e}")
             
        # Wait 2 seconds between requests to avoid overwhelming the servers
        time.sleep(2)
             
    print(f"\nFinished! Found {len(valid_articles)} valid articles out of {len(urls)}.")
    
    # Save to jsonl
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for article in valid_articles:
            f.write(json.dumps(article) + '\n')
            
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    # Get project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    output_path = os.path.join(base_dir, "data", "crawler_output.jsonl")
    crawl_and_filter(urls, output_path)
