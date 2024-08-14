from googleapiclient.discovery import build
from pytube import YouTube
import os
import assemblyai as aai
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


nltk.download('punkt')
nltk.download('stopwords')

api_key = 'api_key'
youtube = build(
    'youtube',
    'v3',
    developerKey=api_key
)
aai.settings.api_key = "api_key"
transcriber = aai.Transcriber()

def download(url, path):
    youtube = YouTube(url)
    streams = youtube.streams.filter(progressive=True)
    my_video = streams.get_by_resolution("720p")
    my_video.download(output_path=path)

def clean_filename(filename):
    illegal_chars = re.compile(r'[\\/:*?"<>|]')
    cleaned_filename = re.sub(illegal_chars, '', filename)
    cleaned_filename = cleaned_filename.strip()
    return cleaned_filename

def extract_workouts(transcript):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(transcript.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return filtered_words

muscle = input("Enter a muscle group you want to find workouts for: ")
search_query = 'best ' + muscle + ' workouts'
request = youtube.search().list(
    part='id,snippet',
    q=search_query,
    videoEmbeddable='true',
    type='video',
    maxResults=10
)

response = request.execute()
transcripts = []

for item in response['items']:
    video_id = item['id']['videoId']
    video_title = item['snippet']['title']
    cleaned_title = clean_filename(video_title)
    video_link = f'https://www.youtube.com/watch?v={video_id}'
    directory = os.getcwd()
    download(video_link, directory)
    transcript = transcriber.transcribe(cleaned_title + ".mp4")
    transcripts.append(transcript.text)

workout_counter = Counter()

for transcript in transcripts:
    workouts = extract_workouts(transcript)
    workout_counter.update(workouts)

most_common_workouts = workout_counter.most_common(10)

print("Most common workouts mentioned in the transcripts:")
for workout, count in most_common_workouts:
    print(f"{workout}: {count}")
