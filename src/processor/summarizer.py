from src.processor.llm_client import LLMClient
import json
import re

class Summarizer:
    def __init__(self):
        self.llm = LLMClient()

    def process_article(self, article):
        """
        Process an article to generate summary, title, score, etc.
        Returns the modified article dict.
        """
        print(f"Processing: {article['title'][:30]}... ({article['source']})")
        
        # Prepare content (truncate to avoid exceeding context window)
        # 1 token ~= 4 chars, 4096 tokens ~= 16000 chars. 
        # Safe limit: 3000 chars of content
        content_snippet = article['summary'][:3000]
        
        prompt = f"""
        You are an editor for "AI Sports Daily". Analyze the following article and provide a JSON response in Simplified Chinese.
        
        Article:
        Title: {article['title']}
        Content: {content_snippet}
        
        Task:
        1. Translate title to Chinese (title_zh).
        2. Write a detailed summary in Chinese (3-5 sentences) (summary_zh).
        3. Write a one-sentence comment/insight (one_sentence_comment).
        4. Rate importance (1-10) based on relevance to AI or Sports Science (score).
        5. Assign tags (max 3) (tags).
        6. Categorize into: "AI", "Science", "Gear", "Training", "Industry", "Other" (category).
        
        Response Format (JSON ONLY):
        {{
            "title_zh": "...",
            "summary_zh": "...",
            "one_sentence_comment": "...",
            "score": 8,
            "tags": ["Tag1", "Tag2"],
            "category": "AI"
        }}
        """
        
        response_text = self.llm.generate(prompt)
        
        if not response_text:
            print("  LLM generation failed or returned empty.")
            return self._fallback_enrichment(article)

        # Parse JSON from response
        try:
            # Clean potential markdown code blocks
            clean_text = self._extract_json(response_text)
            if not clean_text:
                raise ValueError("No JSON found in response")
                
            data = json.loads(clean_text)
            
            article['title_zh'] = data.get('title_zh', article['title'])
            article['summary_zh'] = data.get('summary_zh', article['summary'][:200])
            article['summary_short'] = article['summary_zh'][:100] + "..."
            article['comment'] = data.get('one_sentence_comment', '')
            article['score'] = int(data.get('score', 5))
            article['tags'] = data.get('tags', [])
            article['category'] = data.get('category', 'Other')
            article['importance'] = article['score'] # Align with existing logic
            
            return article
            
        except Exception as e:
            print(f"  Error parsing LLM response: {e}")
            print(f"  Raw response: {response_text[:100]}...")
            return self._fallback_enrichment(article)

    def _extract_json(self, text):
        """Extract JSON part from text using regex or simple search"""
        # Try to find ```json ... ```
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        
        # Try to find first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
            
        return text

    def _fallback_enrichment(self, article):
        """Fallback when LLM fails"""
        article['title_zh'] = article['title']
        article['summary_zh'] = article['summary'][:200]
        article['summary_short'] = article['summary'][:100]
        article['score'] = 5
        article['importance'] = 5
        article['tags'] = ['Raw']
        return article
