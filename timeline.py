import json, sqlite3, sys
from flask import Flask, jsonify, request, make_response, Response, json, Request, render_template_string
from flask.cli import AppGroup
from flask_basicauth import BasicAuth
from datetime import datetime, date, timedelta
from flask_caching import Cache

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 120
}

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config.from_mapping(config)
cache = Cache(app)
basic_auth = BasicAuth(app)
databaseName = 'database.db'

# < HELPER FUNCTIONS --------------------------------------------------
@app.cli.command('init')
def init():                        
    try:
        conn = sqlite3.connect(databaseName)
        with app.open_resource('create.sql', mode='r') as f:
            conn.cursor().executescript(f.read())
        conn.commit()
        print("Database file created as {}".format(str(databaseName)))
    except:
        print("Failed to create {}".format(str(databaseName)))
        sys.exit()
app.cli.add_command(init)

def connectDB(dbName):  
    # Connects to database and returns the connection, if database is offline, program exits
    try:
        conn = sqlite3.connect(dbName)
        return conn
    except:
        print("ERROR: {} OFFLINE".format(str(dbName)))
        sys.exit()

def userExist(cur, username, email):
    #checking if UserAccount Exists
    if username == '' or email == '':
        return False
    cur.execute("SELECT * FROM UserAccounts WHERE username='{}'".format(str(username)))
    user = cur.fetchone()
    if user == None:
        return False
    elif user[0] == str(username) and user[2] == str(email):
        return True

def followExist(cur, follower, followed):
    #checking user is following
    name = False
    foll = False
    if follower == '' or followed == '' or follower == followed:
        return False
    cur.execute("SELECT * FROM UserAccounts WHERE username='{}'".format(str(follower)))
    user = cur.fetchone()
    if user == None:
        return False
    elif user[0] == str(follower):
        name = True
    cur.execute("SELECT * FROM UserAccounts WHERE username='{}'".format(str(followed)))
    user = cur.fetchone()
    if user == None:
        return False
    elif user[0] == str(followed):
        foll = True
    if name and foll:
        return True


# HELPER FUNCTIONS />---------------------------------------------------

@app.route('/timeline/<username>', methods=['GET'])
def getUserTimeline(username):
    #returns user's tweets
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = []
    cur.execute("SELECT * FROM Tweets WHERE username='{}' ORDER BY tweet_id DESC".format(str(username)))
    tweets = cur.fetchall()
    if tweets == []:
        conn.close()
        return make_response("ERROR: NO CONTENT", 204)
    if len(tweets) <= 25:
        for tweet in tweets:
            account.append({'Tweet_ID': tweet[0], 'Username': tweet[1], 'Tweet': tweet[2], 'Timeline': tweet[3]})
    else:
        for tweet in tweets[:25]:
            account.append({'Tweet_ID': tweet[0], 'Username': tweet[1], 'Tweet': tweet[2], 'Timeline': tweet[3]})
    conn.close()
    return make_response(jsonify(account), 200)

@app.route('/timeline/all', methods=['GET'])
    #if request.headers.get('Last-Modified'):
    #    if (datetime.datetime.utcnow() - datetime.timedelta(minutes = 5)) > request.headers.get('Last-Modified'):
    #        return make_response('Not Modified', 304)
    #else:
    #    response = make_response(str(datetime.datetime.utcnow()))
    #    response.headers['Last-Modified'] ='*'
    #    return response

def getAllTimelines():
    app.logger.debug('getAllTimelines()')
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = []
    if 'If-Modified-Since' in request.headers:
        date_time_str = request.headers['If-Modified-Since']
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        print("Time:", (datetime.now() - date_time_obj).total_seconds(), "seconds")
        if((datetime.now() - date_time_obj).total_seconds() < 300):
            return make_response("Not Modified", 304) 
    cur.execute("SELECT * FROM Tweets ORDER BY tweet_id DESC")
    tweets = cur.fetchall()
    if tweets == []:
        conn.close()
        return make_response("ERROR: NO CONTENT", 204)
    if len(tweets) <= 25:
        for tweet in tweets:
            account.append({'Tweet_ID': tweet[0], 'Username': tweet[1], 'Tweet': tweet[2], 'Timeline': tweet[3]})
    else:
        for tweet in tweets[:25]:
            account.append({'Tweet_ID': tweet[0], 'Username': tweet[1], 'Tweet': tweet[2], 'Timeline': tweet[3]})
    response = jsonify(account)
    response.headers['Last-Modified'] = datetime.now()
    conn.close()
    return make_response(response, 200) 

@app.route('/timeline/home/<username>', methods=['GET'])
def getHomeTimeline(username):
    app.logger.debug("getHomeTimeline('%s')", username)
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = []
#    cur.execute("SELECT * FROM Tweets JOIN UserFollows ON(Tweets.username = UserFollows.followed) WHERE Tweets.username='{}'".format(str(username)))
    cur.execute("SELECT follower FROM UserFollows WHERE followed='{}'".format(str(username)))
    followed = cur.fetchall()
    if followed == []:
        conn.close()
        return make_response(jsonify(followed), 200)
    for i in followed:
        cur.execute("SELECT * FROM Tweets WHERE username='{}'".format(str(i[0])))
        tweets = cur.fetchall()
        if tweets == []:
            conn.close()
            return make_response("ERROR: NO CONTENT", 204)
        if len(tweets) <= 25:
            for tweet in tweets:
                account.append({'Tweet_ID': tweet[0], 'Username': tweet[1], 'Tweet': tweet[2], 'Timeline': tweet[3]})
        else:
            for tweet in tweets[:25]:
                account.append({'Tweet_ID': tweet[0], 'Username': tweet[1], 'Tweet': tweet[2], 'Timeline': tweet[3]})
        cache.set('username', account)
    bar = cache.get('username')
    conn.close()
    return render_template_string(
        "<html><body>Username Cache Follow Timeline: {{bar}}</body></html>", bar=bar
    )
    
@app.route('/timeline/post', methods=['POST'])
def postTweet():
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = request.get_json(force=True)
    cur.execute("SELECT * FROM UserAccounts WHERE username='{}'".format(str(account['username'])))
    user = cur.fetchone()
    if user == None:
        return make_response("ERROR: USER NAME DOES NOT EXIST", 409)
    else:
        cur.execute("INSERT INTO Tweets(username, textEntry) VALUES (?,?)", (str(account['username']), str(account['text'])))
        conn.commit()
        conn.close()
        return make_response("SUCCESS: TWEET POSTED", 201, {"location" : '/timeline/{}'.format(str(account['username']))})
    conn.close()
    

if __name__ == '__main__':
    app.run(debug=True)
app.run()