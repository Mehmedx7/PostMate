import tweepy
import os
from config import Config

def post_to_twitter(content, image_path=None):
    auth = tweepy.OAuthHandler(Config.TWITTER_API_KEY, Config.TWITTER_API_SECRET)
    auth.set_access_token(Config.TWITTER_ACCESS_TOKEN, Config.TWITTER_ACCESS_SECRET)
    api = tweepy.API(auth)
    client = tweepy.Client(
        consumer_key=Config.TWITTER_API_KEY,
        consumer_secret=Config.TWITTER_API_SECRET,
        access_token=Config.TWITTER_ACCESS_TOKEN,
        access_token_secret=Config.TWITTER_ACCESS_SECRET
    )

    try:
        media_ids = []
        if image_path and os.path.exists(image_path):
            media = api.media_upload(filename=image_path)
            media_ids.append(media.media_id)

        if media_ids:
            response = client.create_tweet(text=content, media_ids=media_ids)
        else:
            response = client.create_tweet(text=content)

        print(f"Tweet posted successfully! Tweet ID: {response.data['id']}")
        return response
    except Exception as e:
        print(f"Error posting tweet: {e}")
        raise