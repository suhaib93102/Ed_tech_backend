from django.conf import settings
import logging
import requests

logger = logging.getLogger(__name__)


class YouTubeService:
    """
    Service class for YouTube API interactions
    """
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.base_url = 'https://www.googleapis.com/youtube/v3'
    
    def get_video_details(self, video_id):
        """
        Fetch video details from YouTube API
        """
        try:
            if not self.api_key:
                logger.warning("YouTube API key not configured")
                return None
            
            url = f"{self.base_url}/videos"
            params = {
                'part': 'snippet,contentDetails,statistics',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('items'):
                return data['items'][0]
            return None
        except Exception as e:
            logger.error(f"Error fetching video details: {str(e)}")
            return None
    
    def get_channel_info(self, channel_id):
        """
        Fetch channel information from YouTube API
        """
        try:
            if not self.api_key:
                logger.warning("YouTube API key not configured")
                return None
            
            url = f"{self.base_url}/channels"
            params = {
                'part': 'snippet,statistics',
                'id': channel_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('items'):
                return data['items'][0]
            return None
        except Exception as e:
            logger.error(f"Error fetching channel info: {str(e)}")
            return None
    
    def extract_video_id(self, url):
        """
        Extract video ID from YouTube URL
        """
        try:
            # Handle various YouTube URL formats
            if 'youtu.be/' in url:
                return url.split('youtu.be/')[1].split('?')[0]
            elif 'youtube.com/watch?v=' in url:
                return url.split('watch?v=')[1].split('&')[0]
            elif 'youtube.com/embed/' in url:
                return url.split('embed/')[1].split('?')[0]
            return None
        except Exception as e:
            logger.error(f"Error extracting video ID: {str(e)}")
            return None
