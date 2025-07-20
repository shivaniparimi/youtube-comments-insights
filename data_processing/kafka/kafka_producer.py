from googleapiclient.discovery import build
import re
from bs4 import BeautifulSoup
from confluent_kafka import Producer
import json
from dotenv import load_dotenv
import os

# Function to extract video ID from YouTube URL
def get_video_id(url):
    video_id = re.findall(r"(?<=v=)[^&#]+", url)
    if not video_id:
        video_id = re.findall(r"(?<=be/)[^&#]+", url)
    return video_id[0] if video_id else None

# Function to completely remove HTML content and other irrelevant text
def clean_comment(comment):
    # Use BeautifulSoup to remove HTML tags and content
    soup = BeautifulSoup(comment, "html.parser")
    
    # Remove all tags
    text = soup.get_text()
    
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    
    # Remove timestamps formatted as HH:MM:SS or MM:SS
    text = re.sub(r'\b\d{1,2}:\d{2}(:\d{2})?\b', '', text)
    
    # Remove numbers that could be timestamps (e.g., standalone numbers)
    text = re.sub(r'\b\d{3,4}\b', '', text)  # Removes numbers of 3 or 4 digits
    
    # Remove emojis
    text = re.sub(r'[\U0001F600-\U0001F64F]', '', text)  # emoticons
    text = re.sub(r'[\U0001F300-\U0001F5FF]', '', text)  # symbols & pictographs
    text = re.sub(r'[\U0001F680-\U0001F6FF]', '', text)  # transport & map symbols
    text = re.sub(r'[\U0001F700-\U0001F77F]', '', text)  # alchemical symbols
    text = re.sub(r'[\U0001F780-\U0001F7FF]', '', text)  # Geometric Shapes Extended
    text = re.sub(r'[\U0001F800-\U0001F8FF]', '', text)  # Supplemental Arrows-C
    text = re.sub(r'[\U0001F900-\U0001F9FF]', '', text)  # Supplemental Symbols and Pictographs
    text = re.sub(r'[\U0001FA00-\U0001FA6F]', '', text)  # Chess Symbols
    text = re.sub(r'[\U0001FA70-\U0001FAFF]', '', text)  # Symbols and Pictographs Extended-A
    text = re.sub(r'[\U00002702-\U000027B0]', '', text)  # Dingbats
    text = re.sub(r'[\U000024C2-\U0001F251]', '', text)  # Enclosed characters
    
    # Remove non-alphanumeric characters (except whitespace) including quotes and apostrophes
    text = re.sub(r'[^0-9a-zA-Z\s]+', '', text)
    
    # Remove leading and trailing whitespace
    text = text.strip()
    
    # If the result is empty, return an empty string
    return text if text else ''

# Function to get geolocation of the comment author
def get_country(author_channel_id):
    try:
        request = youtube.channels().list(
            part="snippet,brandingSettings",
            id=author_channel_id
        )
        response = request.execute()
        if response["items"]:
            country = response["items"][0]["brandingSettings"]["channel"].get("country", "Unknown")
            return country
    except Exception as e:
        print(f"Error fetching country: {e}")
    return 'Unknown'

# Function to get comments
def get_comments(video_url):
    video_id = get_video_id(video_url)
    if not video_id:
        print("Invalid YouTube URL.")
        return

    comments = []
    next_page_token = None

    while True:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            pageToken=next_page_token,
            maxResults=100
        ).execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            clean = clean_comment(comment['textDisplay'])
            if not clean:
                continue
            author = comment['authorDisplayName']
            author_channel_id = comment['authorChannelId']['value']
            country = get_country(author_channel_id)
            comment_data = {
                'author': author,
                'text': clean,
                'publishedAt': comment['publishedAt'],
                'updatedAt': comment.get('updatedAt', comment['publishedAt']),
                'likeCount': comment['likeCount'],
                'country': country
            }
            comments.append(comment_data)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return comments

# Function to send data to Kafka
def send_to_kafka(comments, kafka_topic, kafka_config):
    producer = Producer(kafka_config)

    def delivery_report(err, msg):
        if err is not None:
            print(f"Delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

    for comment in comments:
        comment_json = json.dumps(comment).encode('utf-8')
        producer.produce(kafka_topic, key=None, value=comment_json, callback=delivery_report)
    
    producer.flush()


# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')

video_url = 'https://www.youtube.com/watch?v=gFPrZlRhf8I'

youtube = build('youtube', 'v3', developerKey=api_key)

# Replace with your Kafka configuration
kafka_config = {
    'bootstrap.servers': bootstrap_servers,  # Kafka broker address
}

# Replace with your Kafka topic name
kafka_topic = 'youtube-comments'

comments = get_comments(video_url)
if comments:
    # print(comments)
    send_to_kafka(comments, kafka_topic, kafka_config)