import feedparser
import datetime
import time
from email.utils import parsedate_to_datetime
from src.config import Config

class RSSFetcher:
    def fetch_all(self):
        """
        Fetch articles from all configured RSS feeds.
        Returns a list of article dictionaries.
        """
        all_articles = []
        for url in Config.RSS_FEEDS:
            print(f"Fetching RSS: {url} ...")
            try:
                feed = feedparser.parse(url)
                
                # Check for bozo error (encoding/XML issues)
                if feed.bozo:
                    print(f"  Warning: Potential issue with feed {url}: {feed.bozo_exception}")

                if not feed.entries:
                    print(f"  No entries found in {url}")
                    continue

                source_name = feed.feed.get('title', 'Unknown RSS')
                
                # Limit to latest 10 entries per feed to avoid overwhelming
                entries_to_process = feed.entries[:10]
                
                for entry in entries_to_process:
                    article = self._normalize_entry(entry, source_name)
                    if article:
                        all_articles.append(article)
                        
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                
        print(f"Total RSS articles fetched: {len(all_articles)}")
        return all_articles

    def _normalize_entry(self, entry, source_name):
        """Convert feedparser entry to standard article dict"""
        try:
            title = entry.get('title', '').strip()
            if not title:
                return None

            link = entry.get('link', '')
            
            # Try to find best content
            content = entry.get('summary', '') or entry.get('description', '')
            if 'content' in entry:
                # Atom feeds often have full content in 'content' list
                for c in entry.content:
                    if c.get('value'):
                        content = c.value
                        break
            
            # Clean content (basic) - specialized cleaning can be in Processor
            # For now just keep it as is, or maybe strip HTML tags if needed later
            
            # Date handling
            published_struct = entry.get('published_parsed') or entry.get('updated_parsed')
            if published_struct:
                published_dt = datetime.datetime.fromtimestamp(time.mktime(published_struct))
            else:
                published_dt = datetime.datetime.now()

            return {
                'title': title,
                'summary': content, # This is often HTML
                'url': link,
                'source': source_name,
                'published_at': published_dt,
                'type': 'rss',
                'raw': entry # Keep raw just in case
            }
        except Exception as e:
            print(f"Error normalizing entry: {e}")
            return None

if __name__ == "__main__":
    # Test run
    fetcher = RSSFetcher()
    results = fetcher.fetch_all()
    
    print("\n--- Sample Article ---")
    if results:
        r = results[0]
        print(f"Title: {r['title']}")
        print(f"Source: {r['source']}")
        print(f"Date: {r['published_at']}")
        print(f"URL: {r['url']}")
        print(f"Summary Len: {len(r['summary'])}")
