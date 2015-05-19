import ScrapeUtils.database as db
from ScrapeUtils.GetSubredditSubscribers import *
import time
import praw
import csv
from sqlalchemy import distinct
# import sqlite3
# import GetSubredditSubscribersComments
from flask import Flask, jsonify, render_template, request, abort

app = Flask(__name__)
CLIENT_ID = 'XPQ6fQXlWgk5dg'
CLIENT_SECRET = 'tnrBSPQekZXO0_8ucRGNIVmeFwE'
REDIRECT_URI  = 'http://127.0.0.1:4444/authorize_callback'
BASE_DIR = '/Users/ifjorissen/github_repos/flaskreddit/LDA/'

# @app.before_request
# def before_request():
#     if request.path != '/':
#         if request.headers['content-type'].find('application/json'):
#             return 'Unsupported Media Type', 415

r = praw.Reddit('OAuth testing by u/brackishish for scrape-reddit app')
r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

db.init_db()

# def get_db():
#     return sqlite3.connect('<database>')
 
def makeQuery(val):
    topPosts = []
    print("make query called with: " +  str(val))
    gen = r.get_subreddit(val).get_top_from_all(limit=5)
    for post in gen:
        topPosts.append(post)
        print(post)
    return topPosts

def getSRSubscribedComments(val):
    nposts = 2
    s = SubredditScraper()
    start = time.time()

    s.scrapeSubredditUsers(target_subreddit=str(val), nposts=nposts)
    print("Subreddit scraping: %s" %str(val))
    end = time.time()

    session = Session()
    for username in s.authors:
        try:
            print(str(username))
            found_user = session.query(User).filter(User.username == str(username)).all()
            print("usr: %s found: %s" % (str(username), str(found_user)))
            if found_user:
                pass
            else:
                print("adding user")
                session.add(User(username))
        except Exception as err:
            # TODO: determine exact SQLAlchemy error thrown here
            print("could not save user %s: %s" % (username, err))
        finally:
            session.commit()
            session.close()

    session = Session()

    allusers = session.query(User).all()
    print("Everyone")
    print(allusers)

    # scraped = session.query(distinct(Comment.author))
    scraped = session.query(distinct(Comment.author_username)).all()
    print("Scraped: ")
    print(scraped)

    unscraped = [user.username for user in allusers if user not in scraped]
    print("Unscraped: ")
    print(unscraped)
    # print("Everyone")
    # print(allusers)
    # print("Scraped: ")
    # print(scraped)
    # print("Uncraped: ")
    # print(unscraped)

    # r=praw.Reddit(user_agent="u/tooproudtopose reddit-scraper")

    for username in unscraped:
        basename = '%s.csv' % username
        full_path =  BASE_DIR + str(basename)
        start = time.time()
        comments = r.get_redditor(username).get_comments(limit=25)
        lc = 0
        print("writing to %s" %full_path)

        with open(full_path, "wb") as f:
            writer = csv.writer(f, lineterminator = "\n")

            for comment in comments:
                writer.writerow((comment.body, comment.author, datetime.datetime.fromtimestamp(comment.created_utc)))
                lc += 1
                db_comment = Comment(comment)
                try:
                    session.add(db_comment)
                except e:
                    print("could not write comment to db: %s" % e)

        session.commit()
        end = time.time()

        print( "        %s: %d comments downloaded in %d seconds." % (username, lc, int(end-start)))
    return allusers




@app.route('/')
def index():
    links = []
    link_no_refresh = r.get_authorize_url('Unique Key')
    link_refresh = r.get_authorize_url('Different Unique Key', refreshable=True)
    links.append(link_no_refresh)
    links.append(link_refresh)
    return render_template('index.html')

@app.route('/authorize_callback')
def authorized():
    state = request.args.get('state', '')
    code = request.args.get('code', '')
    info = r.get_access_information(code)
    user = r.get_me()
    variables_text = "State=%s, code=%s, info=%s." % (state, code,
                                                      str(info))
    text = 'You are %s and have %u link karma.' % (user.name,
                                                   user.link_karma)
    back_link = "<a href='/'>Back home</a>"
    return redirect('/')

 
@app.route('/scrapesubredditsubscribers/', methods=['GET'])
def scrapesubredditsubscribers():
    ret_data = {"value": request.args.get('SRres')}
    print("scrape sr subscribers called")
    print(ret_data)
    # posts = makeQuery(ret_data.get('value'))
    authors = getSRSubscribedComments(ret_data.get('value'))
    data = []
    for author in authors:
        # sess = post.get("")
        data.append([str(author.username), str(author.comments)]) 
    return jsonify({"value": str(data)})

@app.route('/subredditstream/', methods=['GET'])
def subredditstream():
    ret_data = {"value": request.args.get('SRstream')}
    print("stream called")
    print(ret_data)
    posts = makeQuery(ret_data.get('value'))
    data = []
    for post in posts:
        data.append(str(post)) 
    return jsonify({"value": str(data)})
 
if __name__ == '__main__':
    app.run(port=4444, debug=True)


