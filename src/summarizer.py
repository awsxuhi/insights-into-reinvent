import openai
from config.config import OPENAI_API_KEY

class VideoSummarizer:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        
    def generate_summary(self, video):
        prompt = f"""
        Please summarize the key points from this AWS re:Invent video:
        Title: {video['title']}
        Description: {video['description']}
        Focus on industry-related insights and announcements.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that summarizes AWS re:Invent videos."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content 