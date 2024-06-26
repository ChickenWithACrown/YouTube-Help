import requests
import csv
import random
import time
import html
from collections import Counter
import re
from itertools import combinations

API_KEY = "AIzaSyDdMLpvNBxFWWyUTn9QpgF_0b_YCYBXFOk"  # Replace with your API key
BASE_URL = "https://www.googleapis.com/youtube/v3/"

def fetch_channel_videos(channel_id):
    print("Fetching videos for channel...")
    videos = []
    next_page_token = None

    while True:
        url = f"{BASE_URL}search?part=id,snippet&channelId={channel_id}&maxResults=50&type=video&key={API_KEY}"
        if next_page_token:
            url += f"&pageToken={next_page_token}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        videos += [{"id": item["id"]["videoId"], "title": html.unescape(item["snippet"]["title"])} for item in data.get("items", [])]

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

        time.sleep(0.5)  # To avoid hitting API rate limits

    return videos

def fetch_video_details(video_id):
    url = f"{BASE_URL}videos?part=statistics&id={video_id}&key={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    try:
        stats = data["items"][0]["statistics"]
        likes = int(stats.get("likeCount", 0))
        views = int(stats.get("viewCount", 0))
    except (KeyError, IndexError):
        likes = 0
        views = 0
    return likes, views

def categorize_videos(videos):
    print("Categorizing videos...")
    good_videos = []
    neutral_videos = []
    bad_videos = []

    for idx, video in enumerate(videos):
        print(f"Processing video {idx+1}/{len(videos)}: {video['title']} ({video['id']})")
        likes, views = fetch_video_details(video["id"])
        if views >= 100 and likes >= 50:
            good_videos.append(video)
        elif (30 <= views <= 90) or (20 <= likes <= 40):
            neutral_videos.append(video)
        elif views < 30 or likes < 20:
            bad_videos.append(video)
        time.sleep(0.5)  # To avoid hitting API rate limits

    return good_videos, neutral_videos, bad_videos

def extract_keywords(titles):
    keywords = []
    for title in titles:
        # Remove special characters and split by spaces
        words = re.findall(r'\w+', title.lower())
        keywords.extend(words)
    return keywords

def suggest_new_videos(good_videos):
    print("\nGenerating new video ideas based on good videos...")
    suggestions = []
    titles = [video['title'] for video in good_videos]

    # Extract keywords from titles
    keywords = extract_keywords(titles)

    # Find the most common keywords
    common_keywords = Counter(keywords).most_common(10)
    common_keywords = [keyword for keyword, _ in common_keywords]

    # Generate new ideas by creating combinations of common keywords
    for combination in combinations(common_keywords, 2):
        keyword1, keyword2 = combination
        suggestions.append(f"{keyword1.capitalize()} and {keyword2.capitalize()}: What You Need to Know")
        suggestions.append(f"Exploring {keyword1.capitalize()} with {keyword2.capitalize()}")
        suggestions.append(f"The Relationship Between {keyword1.capitalize()} and {keyword2.capitalize()}")
        suggestions.append(f"How {keyword1.capitalize()} Impacts {keyword2.capitalize()}")
        suggestions.append(f"{keyword1.capitalize()} vs. {keyword2.capitalize()}: A Comprehensive Guide")

    # Ensure suggestions are unique and not redundant
    unique_suggestions = list(set(suggestions))

    return unique_suggestions

def save_results(good_videos, neutral_videos, bad_videos):
    with open('youtube_analysis_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Category', 'Video ID', 'Title']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for video in good_videos:
            writer.writerow({'Category': 'Good', 'Video ID': video['id'], 'Title': video['title']})
        for video in neutral_videos:
            writer.writerow({'Category': 'Neutral', 'Video ID': video['id'], 'Title': video['title']})
        for video in bad_videos:
            writer.writerow({'Category': 'Bad', 'Video ID': video['id'], 'Title': video['title']})

def main():
    channel_id = input("Enter your YouTube channel ID: ")

    videos = fetch_channel_videos(channel_id)

    if not videos:
        print("No videos found.")
        return

    good_videos, neutral_videos, bad_videos = categorize_videos(videos)

    total_videos = len(videos)
    print(f"\nGood videos: {len(good_videos) / total_videos * 100:.2f}%")
    print(f"Neutral videos: {len(neutral_videos) / total_videos * 100:.2f}%")
    print(f"Bad videos: {len(bad_videos) / total_videos * 100:.2f}%")

    save_results(good_videos, neutral_videos, bad_videos)

    if good_videos:
        suggestions = suggest_new_videos(good_videos)
        for suggestion in suggestions:
            print(suggestion)

if __name__ == "__main__":
    main()
