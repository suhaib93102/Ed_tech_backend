from django.conf import settings
import logging
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

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

    def get_transcript(self, video_id):
        """
        Extract transcript from YouTube video
        """
        try:
            logger.info(f"Fetching transcript for video ID: {video_id}")
            
            # Create API instance
            api = YouTubeTranscriptApi()
            
            # Try to fetch transcript (preferring English)
            try:
                transcript = api.fetch(video_id, languages=['en'])
                logger.info(f"Successfully fetched English transcript for {video_id}")
                return {
                    'success': True,
                    'transcript': [{'text': item.text, 'start': item.start, 'duration': item.duration} 
                                   for item in transcript],
                    'language': 'en'
                }
            except NoTranscriptFound:
                # If English transcript not found, try to get available transcripts
                logger.warning(f"English transcript not found for {video_id}, trying other languages")
                try:
                    transcript_list = api.list(video_id)
                    
                    # Try generated transcripts first
                    if hasattr(transcript_list, 'generated_transcripts') and transcript_list.generated_transcripts:
                        transcript = transcript_list.generated_transcripts[0].fetch()
                        language = transcript_list.generated_transcripts[0].language
                        logger.info(f"Fetched auto-generated {language} transcript for {video_id}")
                        return {
                            'success': True,
                            'transcript': [{'text': item.text, 'start': item.start, 'duration': item.duration} 
                                           for item in transcript],
                            'language': language
                        }
                    elif hasattr(transcript_list, 'manually_created_transcripts') and transcript_list.manually_created_transcripts:
                        transcript = transcript_list.manually_created_transcripts[0].fetch()
                        language = transcript_list.manually_created_transcripts[0].language
                        logger.info(f"Fetched {language} transcript for {video_id}")
                        return {
                            'success': True,
                            'transcript': [{'text': item.text, 'start': item.start, 'duration': item.duration} 
                                           for item in transcript],
                            'language': language
                        }
                except Exception as e:
                    logger.error(f"No transcripts available for {video_id}: {str(e)}")
                    return {
                        'success': False,
                        'error': 'No transcripts available for this video',
                        'details': 'The video does not have captions/subtitles enabled'
                    }
            
        except TranscriptsDisabled:
            logger.warning(f"Transcripts are disabled for video {video_id}")
            return {
                'success': False,
                'error': 'Transcripts disabled',
                'details': 'This video has transcripts disabled'
            }
        except Exception as e:
            logger.error(f"Error fetching transcript: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to fetch transcript',
                'details': str(e)
            }

    def summarize_transcript(self, transcript_list):
        """
        Summarize transcript using Gemini AI
        """
        try:
            from .services.gemini_service import gemini_service
            
            # Combine all transcript text
            full_text = ' '.join([item['text'] for item in transcript_list])
            
            # Check if text is too long (Gemini has token limits)
            if len(full_text) > 50000:
                logger.warning("Transcript is very long, truncating to 50000 characters")
                full_text = full_text[:50000]
            
            logger.info(f"Summarizing {len(full_text)} characters of transcript")
            
            # Use Gemini to summarize
            prompt = f"""Please provide a comprehensive summary of the following YouTube video transcript. 
            
The summary should include:
1. Main topic and key points
2. Important concepts or ideas discussed
3. Key takeaways
4. Any statistics or important numbers mentioned
5. Conclusions or recommendations (if any)

Keep the summary well-structured with sections and bullet points.

Transcript:
{full_text}"""
            
            result = gemini_service.generate_summary(full_text, prompt_type='video')
            
            if result.get('success'):
                return {
                    'success': True,
                    'summary': result.get('summary'),
                    'summary_type': 'gemini_ai'
                }
            else:
                logger.error(f"Gemini summarization failed: {result.get('error')}")
                # Fallback to simple summarization
                return self._simple_summarize(transcript_list)
                
        except ImportError:
            logger.warning("Gemini service not available, using simple summarization")
            return self._simple_summarize(transcript_list)
        except Exception as e:
            logger.error(f"Error summarizing transcript: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to summarize transcript',
                'details': str(e)
            }

    def _simple_summarize(self, transcript_list):
        """
        Simple fallback summarization based on extracting key sentences
        """
        try:
            # Get first 5 and last 5 lines as a simple summary
            if len(transcript_list) <= 10:
                summary_items = transcript_list
            else:
                summary_items = transcript_list[:5] + transcript_list[-5:]
            
            summary = ' '.join([item['text'] for item in summary_items])
            
            return {
                'success': True,
                'summary': summary,
                'summary_type': 'simple_extraction',
                'note': 'This is a simple summary. For better results, enable Gemini service.'
            }
        except Exception as e:
            logger.error(f"Error in simple summarization: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to create summary',
                'details': str(e)
            }
