# collect_data.py

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import pandas as pd

# Set your API key (replace 'YOUR_API_KEY' with your actual API key)
API_KEY = 'YOUR_API_KEY'

# Set the YouTube API service
youtube = build('youtube', 'v3', developerKey=API_KEY)


def get_video_data(video_id):
    """
    Get data for a specific video.
    """
    try:
        response = youtube.videos().list(
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


def get_video_analytics(video_id, start_date, end_date):
    """
    Get historical view data for a specific video using YouTube Analytics API.
    """
    # TODO: Make API request to YouTube Analytics API
    # TODO: Extract and return relevant data


def main():
    video_id = 'VIDEO_ID'
    start_date = '2023-01-01'
    end_date = '2023-01-31'

    video_data = get_video_data(video_id)
    video_analytics = get_video_analytics(video_id, start_date, end_date)

    # Print or save the collected data
    print("Video Data:", json.dumps(video_data, indent=2))
    print("Video Analytics:", json.dumps(video_analytics, indent=2))


if __name__ == "__main__":
    main()
