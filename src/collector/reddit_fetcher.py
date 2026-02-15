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
        for source in Config.REDDIT_SUBREDDITS:
            subreddit_name = source['name']
            suggested_category = source['category']
            
            print(f"Fetching Reddit: r/{subreddit_name} ...")
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                # Fetch hot posts, limit to 10
                for submission in subreddit.hot(limit=10):
                    if submission.stickied:
                        continue
                        
                    article = self._normalize_submission(submission, subreddit_name, suggested_category)
                    if article:
                        all_articles.append(article)
                        
            except Exception as e:
                print(f"Error fetching r/{subreddit_name}: {e}")
                
        print(f"Total Reddit articles fetched: {len(all_articles)}")
        return all_articles

    def _normalize_submission(self, submission, subreddit_name, suggested_category):
        try:
            content = submission.selftext
            published_dt = datetime.datetime.fromtimestamp(submission.created_utc)

            return {
                'title': submission.title,
                'summary': content, 
                'url': submission.url,
                'source': f"r/{subreddit_name}",
                'suggested_category': suggested_category,
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
