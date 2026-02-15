import os
import shutil
import datetime
import json
from jinja2 import Environment, FileSystemLoader

# Configuration
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'template')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output')
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static')
MAX_ARTICLES_PER_PAGE = 30

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

class HtmlBuilder:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        self.daily_template = self.env.get_template('daily_template.html')
        self.index_template = self.env.get_template('index_template.html')

    def build_daily_page(self, date_obj, articles):
        """
        Generate a daily report page.
        date_obj: datetime.date object
        articles: list of dictionaries
        """
        date_str = date_obj.strftime('%Y-%m-%d')
        display_date = date_obj.strftime('%Y年%m月%d日')
        
        # Prepare output directory
        daily_output_dir = os.path.join(OUTPUT_DIR, date_str)
        ensure_dir(daily_output_dir)
        
        # Sort by importance
        sorted_articles = sorted(articles, key=lambda x: x.get('importance', 0), reverse=True)
        
        # Split headlines
        headlines = [a for a in sorted_articles if a.get('importance', 0) >= 8]
        
        # Article Limiting Logic
        display_articles = sorted_articles
        hidden_articles = []
        has_more = False
        
        if len(sorted_articles) > MAX_ARTICLES_PER_PAGE:
            display_articles = sorted_articles[:MAX_ARTICLES_PER_PAGE]
            hidden_articles = sorted_articles[MAX_ARTICLES_PER_PAGE:]
            has_more = True
            
            # Save hidden articles to archive.json
            with open(os.path.join(daily_output_dir, 'archive.json'), 'w', encoding='utf-8') as f:
                json.dump(hidden_articles, f, ensure_ascii=False, indent=2)

        # Render HTML
        html_content = self.daily_template.render(
            title=f"AI运动日报 | {display_date}",
            date_str=display_date,
            headlines=headlines,
            all_articles=display_articles,
            headline_count=len(headlines),
            total_count=len(articles),
            canonical_url=f"./{date_str}/index.html", # Relative for now, can be absolute if base URL known
            has_more=has_more,
            hidden_count=len(hidden_articles),
            generated_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Write file
        with open(os.path.join(daily_output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Generated daily page for {date_str} ({len(display_articles)} displayed, {len(hidden_articles)} archived)")

    def build_index_page(self, existing_dates):
        """
        Generate the main index/archive page.
        existing_dates: list of (date_obj, article_count) tuples
        """
        # Calendar data (last 30 days)
        today = datetime.date.today()
        calendar_days = []
        existing_date_strs = {d[0].strftime('%Y-%m-%d') for d in existing_dates}
        
        for i in range(29, -1, -1):
            d = today - datetime.timedelta(days=i)
            d_str = d.strftime('%Y-%m-%d')
            calendar_days.append({
                'day': d.day,
                'link': f"./{d_str}/index.html" if d_str in existing_date_strs else "#",
                'has_report': d_str in existing_date_strs
            })
            
        # Archive list (reverse chronological)
        archives = []
        for date_obj, count in sorted(existing_dates, key=lambda x: x[0], reverse=True):
            d_str = date_obj.strftime('%Y-%m-%d')
            archives.append({
                'date_str': date_obj.strftime('%Y年%m月%d日'),
                'link': f"./{d_str}/index.html",
                'count': count
            })
            
        # Render HTML
        html_content = self.index_template.render(
            calendar_days=calendar_days,
            archives=archives
        )
        
        # Write file
        with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Generated index page")

    def copy_static_assets(self):
        """Copy static CSS/JS to output directory"""
        output_static = os.path.join(OUTPUT_DIR, 'static')
        # if os.path.exists(output_static):
        #     shutil.rmtree(output_static)
        # shutil.copytree(STATIC_DIR, output_static)
        
        # Ensure static dir exists in output
        ensure_dir(output_static)
        
        # Copy files individually to avoid permission errors on Windows if directory is locked
        for item in os.listdir(STATIC_DIR):
            s = os.path.join(STATIC_DIR, item)
            d = os.path.join(output_static, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
        
        # Create .nojekyll file
        with open(os.path.join(OUTPUT_DIR, '.nojekyll'), 'w') as f:
            pass
            
        print("Copied static assets and created .nojekyll")

# Example usage (for testing)
if __name__ == "__main__":
    builder = HtmlBuilder()
    
    # Mock data - Generate > 50 articles to test limiting
    today = datetime.date.today()
    mock_articles = []
    
    # Headlines
    for i in range(5):
        mock_articles.append({
            'title': f'今日头条新闻 {i+1}',
            'summary': '这是一条非常重要的新闻摘要，涵盖了AI与运动科学的最新突破。',
            'summary_short': '重要新闻摘要...',
            'url': 'https://example.com',
            'source': '机器之心',
            'category': 'AI前沿',
            'category_code': 'ai',
            'importance': 9,
            'tags': ['AI', 'Top']
        })
        
    # Standard articles
    for i in range(50):
        mock_articles.append({
            'title': f'普通新闻标题 {i+1}',
            'summary': '这是一条普通的新闻摘要。',
            'summary_short': '普通新闻摘要...',
            'url': 'https://example.com',
            'source': 'Reddit',
            'category': '装备评测' if i % 2 == 0 else '运动科学',
            'category_code': 'gear' if i % 2 == 0 else 'science',
            'importance': 5 + (i % 3), # Random importance 5-7
            'tags': ['News']
        })
    
    builder.copy_static_assets()
    builder.build_daily_page(today, mock_articles)
    builder.build_index_page([(today, len(mock_articles))])
