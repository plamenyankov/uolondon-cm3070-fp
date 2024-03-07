import os
import requests
from dotenv import load_dotenv
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTube_Scrapper:
    BASE_URL = 'https://www.googleapis.com/youtube/v3/'

    def __init__(self):
        # Load environment variables
        load_dotenv()
        # Retrieve the API key from environment variables
        self.api_key = os.getenv("YOUTUBE_API_KEY")
    def get_api_key(self):
        return self.api_key

    def get_video_ids(self, search_url):
        response = requests.get(search_url).json()
        video_ids = [item['id']['videoId'] for item in response['items']]
        return video_ids

    def get_video_statistics(self,video_id, search_url):

        # api request
        data = requests.get(search_url).json()

        # statistics object
        video_statistics = {
            'video_id': video_id,
            'title': data['items'][0]['snippet']['title'],
            'published_date': data['items'][0]['snippet']['publishedAt'],
            'duration': data['items'][0]['contentDetails']['duration'],
            'description': data['items'][0]['snippet']['description'],
            'like_count': data['items'][0]['statistics']['likeCount'],
            'view_count': data['items'][0]['statistics']['viewCount'],
            'comment_count': data['items'][0]['statistics']['commentCount']
        }
        # return statistics object
        return video_statistics

    def get_videos(self, API_KEY, SEARCH_TERM, PUBLISHED_AFTER, PUBLISHED_BEFORE, VIDEO_DURATION, MAX_RESULTS):
        SEARCH_ENDPOINT = (
            f"{self.BASE_URL}search?part=snippet&"
            f"q={SEARCH_TERM}&type=video&publishedAfter={PUBLISHED_AFTER}&publishedBefore={PUBLISHED_BEFORE}&"
            f"videoDuration={VIDEO_DURATION}&maxResults={MAX_RESULTS}&key={API_KEY}"
        )

        video_statistics_list = []
        videos_ids = self.get_video_ids(SEARCH_ENDPOINT)
        for video_id in videos_ids:
            search_url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={API_KEY}&part=snippet,statistics,contentDetails'
            try:
                video_statistics = self.get_video_statistics(video_id, search_url)
            except Exception as e:
                print(f"An error occurred: {e}")
            video_statistics_list.append(video_statistics)
        return pd.DataFrame(video_statistics_list)

    def get_all_comments_per_video_id(self, youtube, part='snippet', videoId=None, textFormat='plainText', maxResults=100):
        comments_data = []
        nextPageToken = None

        while True:
            results = youtube.commentThreads().list(
                part=part,
                videoId=videoId,
                textFormat=textFormat,
                maxResults=maxResults,
                pageToken=nextPageToken
            ).execute()

            for item in results['items']:
                comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comment_likes = item['snippet']['topLevelComment']['snippet']['likeCount']
                reply_count = item['snippet']['totalReplyCount']

                comments_data.append({
                    'video_id': videoId,
                    'comment': comment_text,
                    'comment_likes': comment_likes,
                    'total_reply_count': reply_count
                })

            nextPageToken = results.get("nextPageToken")

            if nextPageToken is None:
                break

        return comments_data

    def get_comments_from_video_ids(self, youtube_videos):
        comments_list = []
        # You should have your API_KEY defined before this point, or replace with the actual key string
        youtube = build('youtube', 'v3', developerKey=self.api_key)

        # Replace with the video ID for which you want to fetch comments
        for i, e in youtube_videos.iterrows():
            video_id = e['video_id']
            try:
                comments = self.get_all_comments_per_video_id(youtube, part='snippet', videoId=video_id,
                                                         textFormat='plainText', maxResults=100)
                for comment in comments:
                    comments_list.append(comment)

            except HttpError as e:
                print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return comments_list

    # Master function
    # Parameter: youtube videos dataframe
    # Loops through video ids and gets comments per each video
    # Create DataFrame of all comments
    # Merge with the DataFrame that was passed as parameter
    def get_video_comments(self, youtube_videos):
        # Get comments per video id
        all_comments = self.get_comments_from_video_ids(youtube_videos)
        # Create DF
        comments_df = pd.DataFrame(all_comments, columns=['video_id', 'comment', 'comment_likes', 'total_reply_count'])
        # Merge all comments with youtube_videos
        merged_df = pd.merge(youtube_videos, comments_df, on='video_id', how='inner')
        return merged_df





