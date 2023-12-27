# collect_data.py

import os
import json
import csv
from datetime import datetime, timedelta
from googleapiclient.discovery import build

# Set your YouTube API key
API_KEY = 'AIzaSyDOiOOGjskuedf2x-q-f9SLZm24w0_wbwo'

# Define the channels to collect data from
channels = [
    {'name': 'Channel1', 'id': 'ChannelID1'},
    {'name': 'Channel2', 'id': 'ChannelID2'},
]

# Specify the number of videos to retrieve from each channel
videos_per_channel = 30

# Specify the directory where you want to save the CSV file
dataset_directory = 'datasets'

# Specify the file name
csv_filename = 'video_data.csv'

# Construct the full file path
csv_filepath = os.path.abspath(os.path.join(dataset_directory, csv_filename))


def is_same_day(timestamp1, timestamp2):
    """
    Check if two timestamps are from the same day.
    """
    date1 = datetime.utcfromtimestamp(timestamp1).date()
    date2 = datetime.utcfromtimestamp(timestamp2).date()
    return date1 == date2


def get_video_data(api_key, channel_id, max_results):
    """
    Get data for the latest videos from a specific channel.
    """
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Make API request to get the latest videos from the channel
    response = youtube.search().list(
        part='id',
        channelId=channel_id,
        type='video',
        order='date',
        maxResults=max_results
    ).execute()

    video_data = []

    for item in response.get('items', []):
        video_id = item['id']['videoId']
        video_info = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()

        # Extract relevant data
        snippet = video_info['items'][0]['snippet']
        statistics = video_info['items'][0]['statistics']
        content_details = video_info['items'][0]['contentDetails']

        video_data.append({
            'duration': content_details['duration'],
            'upload_date': snippet['publishedAt'],
            'views': statistics.get('viewCount', 0),
            'likes': statistics.get('likeCount', 0),
            'dislikes': statistics.get('dislikeCount', 0),
            'comments': statistics.get('commentCount', 0)
        })

    return video_data


def write_to_csv(file_path, data):
    """
    Write video data to a CSV file.
    """
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['duration', 'upload_date', 'views', 'likes', 'dislikes', 'comments']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def get_top_channels(api_key, max_results):
    """
    Get a list of top channels based on view count.
    """
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Make API request to get channels based on search query
    response = youtube.search().list(
        part='snippet',
        type='channel',
        maxResults=max_results,
        order='viewCount',  # Sorting by view count
        q='popular channels'  # You can adjust the search query as needed
    ).execute()

    top_channels = [{'name': item['snippet']['title'], 'id': item['id']['channelId']} for item in response.get('items', [])]

    return top_channels


def main():
    # Check if data was already collected today
    today = datetime.utcnow().date()
    if os.path.exists(csv_filepath) and is_same_day(today, datetime.utcfromtimestamp(os.path.getctime(csv_filepath)).date()):
        print("Data already collected today. Exiting.")
        return

    top_channels = get_top_channels(API_KEY, 10)  # Adjust the number as needed

    channels = top_channels
    # Collect video data from each channel
    all_video_data = []
    for channel in channels:
        channel_name = channel['name']
        channel_id = channel['id']
        print(f"Collecting data for {channel_name}...")
        video_data = get_video_data(API_KEY, channel_id, videos_per_channel)
        all_video_data.extend(video_data)

    # Write data to CSV file
    write_to_csv(csv_filepath, all_video_data)
    print("Data collection completed.")


if __name__ == "__main__":
    main()
