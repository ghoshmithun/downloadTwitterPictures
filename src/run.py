import tweepy
import os
from tweepy import OAuthHandler
import json
import wget
import argparse
import configparser

#TODO: Limit by number of tweets?
def parse_arguments():
  parser = argparse.ArgumentParser(description='Download pictures from a Twitter feed.')
  parser.add_argument('--username', type=str, default='NatGeoPhotos', help='The twitter screen name from the account we want to retrieve all the pictures')
  parser.add_argument('--num', type=int, default=100, help='Maximum number of tweets to be returned.')
  parser.add_argument('--retweets', default=False, action='store_true', help='Include retweets')
  parser.add_argument('--replies', default=False, action='store_true', help='Include replies')
  parser.add_argument('--output', default='../pictures/', type=str, help='folder where the pictures will be stored')

  args = parser.parse_args()
  return args

def parse_config(config_file):
  config = configparser.ConfigParser()
  config.read(config_file)
  return config 
  
@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw))
    return status

def init_tweepy():
  # Status() is the data model for a tweet
  tweepy.models.Status.first_parse = tweepy.models.Status.parse
  tweepy.models.Status.parse = parse
  # User() is the data model for a user profil
  tweepy.models.User.first_parse = tweepy.models.User.parse
  tweepy.models.User.parse = parse

def authorise_twitter_api(config):
  auth = OAuthHandler(config['DEFAULT']['consumer_key'], config['DEFAULT']['consumer_secret'])
  auth.set_access_token(config['DEFAULT']['access_token'], config['DEFAULT']['access_secret'])
  return auth

def download_images_by_user(api, username, retweets, replies, num_tweets, output_folder):
  tweets = api.user_timeline(screen_name=username, count=100, include_rts=retweets, exclude_replies=replies)
  if not os.path.exists(output_folder):
      os.makedirs(output_folder)

  downloaded = 0
  while (len(tweets) != 0 and downloaded < num_tweets):    
    last_id = tweets[-1].id
    
    for status in tweets:
      media = status.entities.get('media', []) 
      if(len(media) > 0 and downloaded < num_tweets):
        wget.download(media[0]['media_url'], out=output_folder)
        downloaded += 1        

    tweets = api.user_timeline(screen_name=username, count=100, include_rts=retweets, exclude_replies=replies, max_id=last_id-1)

def download_images_by_tag(api, tag, retweets, replies, num_tweets, output_folder):
  tweets = api.search('#'+tag, count=100, include_rts=retweets, exclude_replies=replies)
  if not os.path.exists(output_folder):
      os.makedirs(output_folder)

  downloaded = 0
  while (len(tweets) != 0 and downloaded < num_tweets):
    print("{} tweets processed".format(len(tweets)))
    last_id = tweets[-1].id
    
    for status in tweets:
      media = status.entities.get('media', []) 
      if(len(media) > 0 and downloaded < num_tweets):
        wget.download(media[0]['media_url'], out=output_folder)
        downloaded += 1        

    tweets = api.search('#'+tag, count=100, include_rts=retweets, exclude_replies=replies, max_id=last_id-1)

def main():    
  arguments = parse_arguments() 
  username = arguments.username
  retweets = arguments.retweets
  replies = arguments.replies
  num_tweets = arguments.num
  output_folder = arguments.output

  config = parse_config('../config.cfg')
  auth = authorise_twitter_api(config)
  api = tweepy.API(auth)

  download_images_by_tag(api, username, retweets, replies, num_tweets, output_folder)

if __name__=='__main__':
    main()
