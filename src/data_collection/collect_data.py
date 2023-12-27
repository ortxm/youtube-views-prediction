import os
import json
import pandas as pd
from googleapiclient.discovery import build

# Set your YouTube Data API key (replace 'YOUR_API_KEY' with your actual API key)
API_KEY = 'AIzaSyDOiOOGjskuedf2x-q-f9SLZm24w0_wbwo'

# Set the YouTube API service
youtube = build('youtube', 'v3', developerKey=API_KEY)


def get_video_data(video_id):
    """
    Get data for a specific video using the YouTube Data API.
    """
    try:
        response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()

        # Extract relevant data
        snippet_data = response['items'][0]['snippet']
        statistics_data = response['items'][0]['statistics']

        # Extract desired features
        title = snippet_data.get('title', '')
        description = snippet_data.get('description', '')
        views = int(statistics_data.get('viewCount', 0))
        likes = int(statistics_data.get('likeCount', 0))
        dislikes = int(statistics_data.get('dislikeCount', 0))
        comments = int(statistics_data.get('commentCount', 0))

        return {
            'title': title,
            'description': description,
            'views': views,
            'likes': likes,
            'dislikes': dislikes,
            'comments': comments
        }

    except Exception as e:
        print(f'Error: {e}')
        return None


def save_to_json(data, filename):
    """
    Save data to a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)


def save_to_csv(data, filename):
    """
    Save data to a CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)


def collect_data(_channel_id, _max_results):
    """
    Collect video data for a channel using the YouTube Data API.
    """
    print("Before YouTube Data API Request\n")
    try:
        print("Before YouTube Data API Request but inside of try\n")
        # Make API request to get video IDs from the channel
        search_response = youtube.search().list(
            part='id',
            channelId=_channel_id,
            type='video',
            maxResults=_max_results
        ).execute()

        print("After YouTube Data API Request")

        video_ids = [item['id']['videoId'] for item in search_response['items']]

        # Collect detailed data for each video
        videos_data = []
        for video_id in video_ids:
            video_data = get_video_data(video_id)
            if video_data:
                videos_data.append(video_data)

        return videos_data

    except Exception as e:
        print(f'Error: {e}')
        return None


if __name__ == "__main__":
    # Set channel ID and maximum number of results to collect
    channel_id = '@NotAlbino'
    max_results = 317

    # Collect video data
    collected_data = collect_data(channel_id, max_results)

    if collected_data:
        # Save raw data to JSON
        raw_filename = os.path.join('datasets', 'raw', 'raw_data.json')
        save_to_json(collected_data, raw_filename)
        print(f'Raw data saved to {raw_filename}')

        # Save processed data to CSV
        processed_filename = os.path.join('datasets', 'processed', 'processed_data.csv')
        save_to_csv(collected_data, processed_filename)
        print(f'Processed data saved to {processed_filename}')
    else:
        print('Data collection failed.')
