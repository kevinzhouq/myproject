import praw
import datetime
from src.config import Config

class RedditFetcher:
    def __init__(self):
        self.reddit = None
        if Config.REDDIT_CLIENT_ID and Config.REDDIT_CLIENT_SECRET:
            try:
                self.reddit = praw.Reddit(
                    client_id=Config.REDDIT_CLIENT_ID,
                    client_secret=Config.REDDIT_CLIENT_SECRET,
                    user_agent=Config.REDDIT_USER_AGENT
                )
            except Exception as e:
                print(f"Error initializing Reddit client: {e}")
        else:
            print("Warning: Reddit credentials not found in environment variables. Reddit fetcher disabled.")

    def fetch_all(self):
        """
        Fetch top posts from configured subreddits.
        Returns a list of article dictionaries.
        """
        if not self.reddit:
            return []

        all_articles = []
        for subreddit_name in Config.REDDIT_SUBREDDITS:
            print(f"Fetching Reddit: r/{subreddit_name} ...")
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                # Fetch hot posts, limit to 10
                for submission in subreddit.hot(limit=10):
                    if submission.stickied:
                        continue
                        
                    article = self._normalize_submission(submission, subreddit_name)
                    if article:
                        all_articles.append(article)
                        
            except Exception as e:
                print(f"Error fetching r/{subreddit_name}: {e}")
                
        print(f"Total Reddit articles fetched: {len(all_articles)}")
        return all_articles

    def _normalize_submission(self, submission, subreddit_name):
        try:
            # Skip if it's just a self post with no text (unless title is very informative?)
            # But let's keep it simple.
            
            content = submission.selftext
            # If it's a link post, content is the URL usually, but we want the text content if any
            # For link posts, we might want to follow the link, but that's complex. 
            # For now, if it's a link, we use the title and link.
            
            published_dt = datetime.datetime.fromtimestamp(submission.created_utc)

            return {
                'title': submission.title,
                'summary': content, 
                'url': submission.url,
                'source': f"r/{subreddit_name}",
                'published_at': published_dt,
                'type': 'reddit',
                'score': submission.score,
                'num_comments': submission.num_comments,
                'raw': {'id': submission.id, 'score': submission.score}
            }
        except Exception as e:
            print(f"Error normalizing submission: {e}")
            return None

if __name__ == "__main__":
    # Test run (requires env vars)
    fetcher = RedditFetcher()
    results = fetcher.fetch_all()
    
    print("\n--- Sample Reddit Article ---")
    if results:
        r = results[0]
        print(f"Title: {r['title']}")
        print(f"Source: {r['source']}")
        print(f"Date: {r['published_at']}")
        print(f"URL: {r['url']}")
        print(f"Score: {r['score']}")
