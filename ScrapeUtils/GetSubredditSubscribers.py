import praw
import database as db
from datamodel import *

_ua = "u/tooproudtopose reddit-scraper"
target_subreddit = 'Reedcollege'

class SubredditScraper(object):
    def __init__(self,ua=_ua):
        self.conn = praw.Reddit(user_agent=ua)
        self.authors={}

    def scrapeSubredditUsers(self, target_subreddit = target_subreddit, nposts=5):
        
        r = self.conn
        sub = r.get_subreddit(target_subreddit)
        post_generator = sub.get_new(limit=None)

        n=0
        for post in post_generator:
            n+=1
            comments = praw.helpers.flatten_tree(post.comments)
            print("Scraped %d posts" % n)
            lc = len(comments)
            nc = 0
            for comment in comments:
                nc +=1
                #print("%d of %d comments scraped") % (nc, lc)
                try:
                    author = comment.author
                    self.authors[author.name] = author
                except:
                    break
            if n >= nposts:
                break
