# collect_data.py

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Set your API key (replace 'YOUR_API_KEY' with your actual API key)
API_KEY = 'AIzaSyDOiOOGjskuedf2x-q-f9SLZm24w0_wbwo'

# Set the YouTube API service
youtube = build('youtube', 'v3', developerKey=API_KEY)

flow = (InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json', scopes=['https://www.googleapis.com/auth/yt-analytics.readonly']))
credentials = Credentials.from_authorized_user_file('token.json')
youtube_analytics = build('youtubeAnalytics', 'v2', credentials=credentials)


def get_video_data(video_id, youtube_service):
    """
    Get data for a specific video.
    """
    try:
        response = youtube_service.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()

        # Extract relevant data
        statistics_data = response['items'][0]['statistics']
        content_details_data = response['items'][0]['contentDetails']

        # Extract numeric features
        views = int(statistics_data.get('viewCount', 0))
        likes = int(statistics_data.get('likeCount', 0))
        dislikes = int(statistics_data.get('dislikeCount', 0))
        comments = int(statistics_data.get('commentCount', 0))

        # Convert video duration to seconds
        duration = pd.to_timedelta(
            content_details_data.get('duration')).total_seconds() if 'duration' in content_details_data else 0

        return {
            'views': views,
            'likes': likes,
            'dislikes': dislikes,
            'comments': comments,
            'duration': duration
        }

    except HttpError as e:
        print(f'Error: {e}')


def get_video_analytics(video_id, start_date, end_date, youtube_analytics_service):
    """
    Get historical view data for a specific video using YouTube Analytics API.
    """
    try:
        # Make API request to YouTube Analytics API
        analytics_response = youtube_analytics_service.reports().query(
            ids=f'channel==@NotAlbino',
            startDate=start_date,
            endDate=end_date,
            metrics='views',
            dimensions='video',
            filters=f'video=={video_id}',
            includeHistoricalChannelData=True
        ).execute()

        # Extract and return relevant data
        analytics_data = analytics_response.get('rows', [])
        return analytics_data

    except HttpError as e:
        print(f'Error: {e}')
        return None


def authenticate_youtube():
    """
    Authenticate YouTube API using OAuth2.
    """
    try:
        local_flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json', scopes=['https://www.googleapis.com/auth/youtube.readonly'])
        local_credentials = local_flow.run_local_server(port=0)
        return local_credentials
    except Exception as e:
        print(f'Authentication Error: {e}')
        return None


def main():
    video_id = 'cyeaGI2UyDs'
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    # Authenticate YouTube API
    cred = authenticate_youtube()
    if not cred:
        return

    # Set the YouTube API service
    youtube_service = build('youtube', 'v3', credentials=credentials)

    # Set the YouTube Analytics API service
    youtube_analytics_service = build('youtubeAnalytics', 'v2', credentials=credentials)

    # Continue with the rest of the script...
    video_data = get_video_data(video_id, youtube_service)
    video_analytics = get_video_analytics(video_id, start_date, end_date, youtube_analytics_service)

    # Print or save the collected data
    print("Video Data:", json.dumps(video_data, indent=2))
    print("Video Analytics:", json.dumps(video_analytics, indent=2))


if __name__ == "__main__":
    main()
