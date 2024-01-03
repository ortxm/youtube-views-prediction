import pandas as pd
import re
from datetime import timedelta

# Define the path to the CSV file
csv_path = "datasets/video_data.csv"

# Load the dataset
df = pd.read_csv(csv_path)

# Drop unnecessary columns
df = df.drop(columns=['title', 'upload_date', 'video_id'])


# Convert durationMs to seconds
def convert_duration(duration_str):
    if pd.isnull(duration_str):
        return None

    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration_str)
    if match:
        hours, minutes, seconds = map(lambda x: int(x[:-1]) if x else 0, match.groups())
        return hours * 3600 + minutes * 60 + seconds

    return None


df['duration_seconds'] = df['durationMs'].apply(convert_duration)
df = df.drop(columns=['durationMs'])

# Save the cleaned dataset
cleaned_csv_path = "datasets/cleaned_video_data.csv"
df.to_csv(cleaned_csv_path, index=False)

print("Cleaning complete. Cleaned dataset saved to:", cleaned_csv_path)
