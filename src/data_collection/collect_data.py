import os
import json
import csv
from datetime import datetime, timedelta
from googleapiclient.discovery import build

# Constants and Configuration
API_KEY = 'AIzaSyDOiOOGjskuedf2x-q-f9SLZm24w0_wbwo'  # Replace with your actual API key
# Manually specified channel IDs for data collection
CHANNELS = [
    {'name': 'T-Series', 'id': 'UCq-Fj5jknLsUf-MWSy4_brA'},
    {'name': 'Zee Music Company', 'id': 'UCFFbwnve3yF62-tVXkTyHqg'},
    {'name': 'BLACKPINK', 'id': 'UCOmHUn--16B90oW2L6FRR3A'},
    {'name': 'BANGTANTV', 'id': 'UCLkAepWjdylmXSltofFvsYQ'},
    {'name': 'HYBE LABELS', 'id': 'UC3IZKseVpdzPSBaWxBxundA'},
    {'name': 'Justin Bieber', 'id': 'UCIwFjwMjI0y7PDBVEO9-bkQ'},
    {'name': 'Tips Official', 'id': 'UCJrDMFOdv1I2k8n9oK_V21w'},
    {'name': 'Marshmello', 'id': 'UCEdvpU2pFRCVqU6yIPyTpMQ'},
    {'name': 'Taylor Swift', 'id': 'UCqECaJ8Gagnn7YCbPEzWH6g'},
    {'name': 'EminemMusic', 'id': 'UCfM3zsQsOnfWNUppiycmBuw'},
]

VIDEOS_PER_CHANNEL = 30
DATASET_DIRECTORY = 'datasets'
CSV_FILENAME = 'video_data.csv'
FORCE_DATA_COLLECTION = True

# Construct the full file path
CSV_FILEPATH = os.path.abspath(os.path.join(DATASET_DIRECTORY, CSV_FILENAME))


def is_same_day(timestamp1, timestamp2):
    """
    Check if two timestamps are from the same day.
    """
    date1 = timestamp1.date() if isinstance(timestamp1, datetime) else timestamp1
    date2 = timestamp2.date() if isinstance(timestamp2, datetime) else timestamp2
    return date1 == date2


def duration_to_seconds(duration):
    """
    Convert video duration from the format PT3M39S to seconds.
    """
    duration = duration[2:]  # Remove 'PT' at the beginning
    seconds = 0
    segments = duration.split('M')

    for segment in segments:
        if 'H' in segment:
            hours, minutes = segment.split('H')
            seconds += int(hours) * 3600
        elif 'S' in segment:
            seconds += int(segment.split('S')[0])
        elif 'M' in segment:
            minutes = segment.split('M')[0]
            seconds += int(minutes) * 60

    return seconds


def get_video_data(channel_id, max_results):
    """
    Get data for the latest videos from a specific channel.
    """
    print(f"Attempting to collect data for channel with ID: {channel_id}")
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    try:
        # Step 1: Get Uploads Playlist ID
        uploads_playlist_id = get_uploads_playlist_id(youtube, channel_id)

        if not uploads_playlist_id:
            print(f"No uploads playlist found for channel with ID {channel_id}")
            return []

        # Step 2: Get Videos from Uploads Playlist
        videos = get_videos_from_playlist(youtube, uploads_playlist_id, max_results)

        # Step 3: Process the videos as needed
        processed_data = process_videos(videos)

        return processed_data

    except Exception as e:
        print(f"Error: {str(e)}")
        return []


def get_uploads_playlist_id(youtube, channel_id):
    """
    Get the uploads playlist ID for a specific channel.
    """
    try:
        # API request to get the playlists for the channel
        playlists_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        # Check if the response contains any playlists
        playlists = playlists_response.get('items', [])

        # Find the uploads playlist
        uploads_playlist_id = next(
            (playlist['contentDetails']['relatedPlaylists']['uploads'] for playlist in playlists),
            None
        )

        return uploads_playlist_id

    except Exception as e:
        print(f"Error getting uploads playlist ID: {str(e)}")
        return None


def get_videos_from_playlist(youtube, playlist_id, max_results):
    """
    Get videos from a specific playlist.
    """
    try:
        # API request to get videos from a playlist
        videos_response = youtube.playlistItems().list(
            part='contentDetails,snippet',
            playlistId=playlist_id,
            maxResults=max_results
        ).execute()

        # Extract video information from the response
        videos = []
        for item in videos_response.get('items', []):
            try:
                video_data = {
                    "title": item["snippet"]["title"],
                    "upload_date": item["contentDetails"]["videoPublishedAt"],
                    "video_id": item["contentDetails"]["videoId"],
                    "viewCount": get_video_stats(youtube, item["contentDetails"]["videoId"], "viewCount"),
                    "likeCount": get_video_stats(youtube, item["contentDetails"]["videoId"], "likeCount"),
                    "commentCount": get_video_stats(youtube, item["contentDetails"]["videoId"], "commentCount"),
                    "durationMs": get_video_stats(youtube, item["contentDetails"]["videoId"], "durationMs")
                }
                videos.append(video_data)
            except KeyError as e:
                print(f"Error extracting video data: {str(e)}")
                continue

        return videos

    except Exception as e:
        print(f"Error getting videos from playlist: {str(e)}")
        return []


def get_video_stats(youtube, video_id, stat_type):
    """
    Get statistics (views, likes, comments, duration) for a specific video using YouTube Data API v3.
    """
    try:
        # API request to get video statistics
        video_stats_response = youtube.videos().list(
            part='statistics,contentDetails',
            id=video_id
        ).execute()

        # Extract the desired statistic
        statistics = video_stats_response['items'][0]['statistics']
        content_details = video_stats_response['items'][0]['contentDetails']

        if stat_type in statistics:
            return int(statistics[stat_type])
        elif stat_type == "durationMs" and 'duration' in content_details:
            return content_details['duration']
        elif stat_type == "durationMs":
            return 0  # If 'duration' is not present in content details, return 0 for durationMs

        print(f"Error: No '{stat_type}' statistic found for video {video_id}")
        return 0

    except Exception as e:
        print(f"Error getting video {stat_type}: {str(e)}")
        return 0


def process_videos(videos):
    """
    Process the video data as nee
    """
    # Add your processing logic here
    return videos


def write_to_csv(file_path, data):
    """
    Write video data to a CSV file.
    """
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'upload_date', 'video_id', 'viewCount', 'likeCount', 'commentCount', 'durationMs']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def get_top_channels(max_results, channel_type='channel'):
    """
    Get a list of top channels based on subscriber count.
    """
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Make API request to get channels based on subscriber count
    response = youtube.search().list(
        part='snippet',
        type=channel_type,
        q='music',
        order='viewCount',
        maxResults=max_results
    ).execute()

    top_channels = []

    for item in response.get('items', []):
        channel_id = item['id'][channel_type + 'Id']
        channel_title = item['snippet']['title']
        top_channels.append({'name': channel_title, 'id': channel_id})

    return top_channels


def main():
    # Check if data was already collected today
    today = datetime.utcnow().date()

    if not FORCE_DATA_COLLECTION and os.path.exists(CSV_FILEPATH) and is_same_day(today,
                                                                                  datetime.utcfromtimestamp(
                                                                                      os.path.getctime(
                                                                                          CSV_FILEPATH)).date()):
        print("Data already collected today. Exiting.")
        exit()

    # Get top channels dynamically
    # top_channels = get_top_channels(10, channel_type='video')  # Adjust the number as needed
    top_channels = CHANNELS

    # Use top_channels for data collection
    all_video_data = []
    for channel in top_channels:
        channel_name = channel['name']
        channel_id = channel['id']
        print(f"Collecting data for {channel_name}...")
        video_data = get_video_data(channel_id, VIDEOS_PER_CHANNEL)
        all_video_data.extend(video_data)

    # Write data to CSV file
    write_to_csv(CSV_FILEPATH, all_video_data)
    print("Data collection completed.")


if __name__ == "__main__":
    main()
