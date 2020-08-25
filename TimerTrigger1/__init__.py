import datetime
import logging
import time
import azure.functions as func
import json
import tweepy
import sys

class UserDetails():
    def __init__(self, description, loc, text, coords, name, user_created, followers,
            id_str, created, retweets, bg_color):
            self.description = description
            self.loc = loc
            self.text = text 
            self.coords = coords
            self.name = name
            self.user_created = user_created
            self.followers = followers
            self.id_str = id_str
            self.created = created
            self.retweets = retweets
            self.bg_color = bg_color

class MyStreamListener(tweepy.StreamListener):

    def __init__(self, outputBlob, time_limit = 60):
        self.start_time = time.time()
        self.time_limit = time_limit
        self.tweet_list = list()
        self.outputBlob = outputBlob
        super(MyStreamListener, self).__init__()


    def on_status(self, status):        
        if (time.time() - self.start_time) >= self.time_limit:
            logging.info("Time Limit Exceeded Shutting Down the Streaming")
            no_of_tweets = len(self.tweet_list)            
            logging.info("Collected {0} Tweets ".format(no_of_tweets)) 
            jsonStr = json.dumps(self.tweet_list, default= str)
            self.outputBlob.set(jsonStr)           
            return False
        else:
            description = status.user.description
            loc = status.user.location
            text = status.text
            coords = status.coordinates
            name = status.user.screen_name
            user_created = status.user.created_at
            followers = status.user.followers_count
            id_str = status.id_str
            created = status.created_at
            retweets = status.retweet_count
            bg_color = status.user.profile_background_color
            userinstance = UserDetails(description, loc, text, coords, name, user_created, followers, id_str, created, retweets, bg_color)
            self.tweet_list.append(userinstance.__dict__)
            

    def on_error(self, status_code):
        print("Encountered streaming error (", status_code, ")")
        sys.exit()


def main(mytimer: func.TimerRequest,  outputBlob: func.Out[str]) -> None: #
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    
    consumer_key = ''
    consumer_secret = ''
    access_key = ''
    access_secret = ''


    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # initialize stream
    streamListener = MyStreamListener(outputBlob, time_limit=10)
    stream = tweepy.Stream(auth=api.auth, listener=streamListener, tweet_mode='extended')

    tags = ["#covid19"]
    stream.filter(track=tags)

