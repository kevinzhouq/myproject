import sys
import os
import datetime
from src.collector.rss_fetcher import RSSFetcher
from src.collector.reddit_fetcher import RedditFetcher
from src.processor.summarizer import Summarizer
from src.generator.html_builder import HtmlBuilder
from src.config import Config

def main():
    print("--- AI Sports Daily Generator Started ---")
    
    # 1. Fetch Data
    print("\n[Step 1] Fetching data...")
    rss_fetcher = RSSFetcher()
    reddit_fetcher = RedditFetcher()
    
    articles = []
    articles.extend(rss_fetcher.fetch_all())
    articles.extend(reddit_fetcher.fetch_all())
    
    print(f"Total raw articles: {len(articles)}")
    
    if not articles:
        print("No articles found! Exiting.")
        return

    # 2. Process Data (Deduplication & Filtering)
    print("\n[Step 2] Filtering and Deduplicating...")
    unique_articles = []
    seen_urls = set()
    
    kw_pattern = [k.lower() for k in Config.KEYWORDS]
    
    for a in articles:
        if a['url'] in seen_urls:
            continue
            
        # Keyword filtering (simple check in title or summary)
        text_to_check = (a['title'] + " " + a.get('summary', '')).lower()
        if not any(k in text_to_check for k in kw_pattern):
            # Skip irrelevant articles? 
            # For now, let's keep them but mark low score, OR strict filtering?
            # Let's do strict filtering for now to save LLM tokens
            # print(f"Skipping irrelevant: {a['title']}")
            continue
            
        seen_urls.add(a['url'])
        unique_articles.append(a)
        
    print(f"Articles after filtering: {len(unique_articles)}")
    
    # Limit processing to save time/tokens (e.g. top 10 most relevant)
    # For now, just take first 15
    articles_to_process = unique_articles[:15]

    # 3. LLM Processing
    print("\n[Step 3] AI Processing (Summarization & Scoring)...")
    summarizer = Summarizer()
    processed_articles = []
    
    for i, article in enumerate(articles_to_process):
        print(f"Processing {i+1}/{len(articles_to_process)}...")
        try:
            processed = summarizer.process_article(article)
            processed_articles.append(processed)
        except Exception as e:
            print(f"Error processing {article['title']}: {e}")
            processed_articles.append(article) # Keep original if failed

    # 4. Generate HTML
    print("\n[Step 4] Generating HTML...")
    builder = HtmlBuilder()
    builder.copy_static_assets()
    
    today = datetime.date.today()
    builder.build_daily_page(today, processed_articles)
    
    # Update Index (Mock implementation needs real persistence, 
    # for now we just regenerate index with today's entry. 
    # In real app, we'd scan output dir for history.)
    
    # Scan output dir for existing dates
    history = []
    output_dir = builder.OUTPUT_DIR # Access output dir from builder instance logic? 
    # Use hardcoded path logic matching builder
    base_output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    
    if os.path.exists(base_output_dir):
        for item in os.listdir(base_output_dir):
            if os.path.isdir(os.path.join(base_output_dir, item)):
                try:
                    # Valid date folder?
                    d = datetime.datetime.strptime(item, '%Y-%m-%d').date()
                    # Count articles? Simplification: assume 10
                    history.append((d, 10)) 
                except ValueError:
                    continue
    
    # Add today if not in history (it should be since we just generated it)
    if not any(h[0] == today for h in history):
        history.append((today, len(processed_articles)))
        
    builder.build_index_page(history)
    
    print("--- Done! ---")

if __name__ == "__main__":
    main()
