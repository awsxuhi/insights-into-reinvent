from config.config import INDUSTRY_KEYWORDS

class VideoProcessor:
    def filter_industry_videos(self, videos):
        industry_videos = []
        
        for video in videos:
            if any(keyword.lower() in video['title'].lower() or 
                  keyword.lower() in video['description'].lower() 
                  for keyword in INDUSTRY_KEYWORDS):
                industry_videos.append(video)
                
        return industry_videos 