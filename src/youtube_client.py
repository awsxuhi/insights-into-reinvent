from googleapiclient.discovery import build
from config.config import YOUTUBE_API_KEY
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import time

logger = logging.getLogger(__name__)

class YouTubeClient:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    def _clean_description(self, description):
        """Clean up video description by removing redundant content"""
        try:
            # Define possible cutoff phrases
            cutoff_phrases = [
                "Learn more:",
                "Learn more about AWS events:",
                "Subscribe to AWS:"
            ]
            
            # Find the earliest occurrence of any cutoff phrase
            earliest_index = len(description)
            for phrase in cutoff_phrases:
                index = description.find(phrase)
                if index != -1 and index < earliest_index:
                    earliest_index = index
            
            # If any cutoff phrase was found, trim the description
            if earliest_index < len(description):
                cleaned_description = description[:earliest_index].strip()
                return cleaned_description
            
            return description.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning description: {str(e)}")
            return description
    
    def get_video_transcript(self, video_id):
        """
        Get transcript for a specific video
        Args:
            video_id: YouTube video ID
        Returns:
            str: Formatted transcript text or None if not available
        """
        try:
            # Get transcript in English
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=['en']
            )
            
            # Format transcript to plain text
            formatter = TextFormatter()
            formatted_transcript = formatter.format_transcript(transcript_list)
            
            return formatted_transcript
            
        except Exception as e:
            logger.error(f"Error getting transcript for video {video_id}: {str(e)}")
            return None
    
    def get_playlist_videos(self, playlist_id):
        """
        Get basic information for all videos in a playlist
        Args:
            playlist_id: YouTube playlist ID
        Returns:
            list: List of dictionaries containing video information
        """
        videos = []
        next_page_token = None
        
        try:
            while True:
                request = self.youtube.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response['items']:
                    original_description = item['snippet']['description']
                    cleaned_description = self._clean_description(original_description)
                    
                    video = {
                        'title': item['snippet']['title'],
                        'video_id': item['snippet']['resourceId']['videoId'],
                        'description': cleaned_description
                    }
                    videos.append(video)
                    logger.info(f"Processed video: {video['title']}")
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            logger.info(f"Successfully retrieved and cleaned {len(videos)} video descriptions")
            return videos
            
        except Exception as e:
            logger.error(f"Error fetching playlist videos: {str(e)}")
            raise
    
    def add_transcripts_to_videos(self, videos, delay_seconds=1):
        """
        Add transcripts to a list of videos
        Args:
            videos: List of video dictionaries
            delay_seconds: Delay between API calls to avoid rate limits
        Returns:
            list: List of videos with added transcripts
        """
        videos_with_transcripts = []
        total_videos = len(videos)
        
        for i, video in enumerate(videos, 1):
            try:
                logger.info(f"Getting transcript for video {i}/{total_videos}: {video['title']}")
                transcript = self.get_video_transcript(video['video_id'])
                
                video_with_transcript = video.copy()
                video_with_transcript['transcript'] = transcript
                video_with_transcript['has_transcript'] = transcript is not None
                
                videos_with_transcripts.append(video_with_transcript)
                
                # Add statistics to log
                success_rate = sum(1 for v in videos_with_transcripts if v['has_transcript']) / len(videos_with_transcripts)
                logger.info(f"Progress: {i}/{total_videos} ({(i/total_videos)*100:.1f}%) - "
                          f"Success rate: {success_rate*100:.1f}%")
                
                # Add delay to avoid API rate limits
                if i < total_videos and delay_seconds > 0:
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                logger.error(f"Error processing video {video.get('title', '')}: {str(e)}")
                continue
        
        # Final statistics
        successful_transcripts = sum(1 for v in videos_with_transcripts if v['has_transcript'])
        logger.info(f"\nTranscript retrieval completed:")
        logger.info(f"Total videos processed: {len(videos_with_transcripts)}")
        logger.info(f"Successful transcripts: {successful_transcripts}")
        logger.info(f"Success rate: {(successful_transcripts/len(videos_with_transcripts))*100:.1f}%")
        
        return videos_with_transcripts