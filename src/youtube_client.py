from googleapiclient.discovery import build
from config.config import YOUTUBE_API_KEY

class YouTubeClient:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    def get_playlist_videos(self, playlist_id):
        videos = []
        next_page_token = None
        
        while True:
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response['items']:
                video = {
                    'title': item['snippet']['title'],
                    'video_id': item['snippet']['resourceId']['videoId'],
                    'description': item['snippet']['description']
                }
                videos.append(video)
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
        return videos 