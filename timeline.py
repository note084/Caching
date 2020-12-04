import json, sqlite3, sys
from flask import Flask, jsonify, request, make_response
from flask.cli import AppGroup
from flask_basicauth import BasicAuth
from datetime import datetime

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
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
        print("SUCCESS: CONNECTED TO {}".format(str(dbName)))
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
def getAllTimelines():
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = []
    cur.execute("SELECT * FROM Tweets ORDER BY tweet_id DESC")
    tweets = cur.fetchall()
    if tweets == []:
        conn.close()
        return make_response("ERROR: NO CONTENT", 204)
    if len(tweets) <= 25:
        for tweet in tweets:
            account.append({'Tweet_ID': tweet[0], 'Username': tweet[1], 'Tweet': tweet[2]})
    else:
        for tweet in tweets[:25]:
            account.append({'Tweet_ID': tweet[0], 'Username': tweet[1], 'Tweet': tweet[2]})
    conn.close()
    return make_response(jsonify(account), 200) 

@app.route('/timeline/home/<username>', methods=['GET'])
def getHomeTimeline(username):
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
                account.append({'Tweet_ID': tweet[0], 'Username': tweet[1], 'Tweet': tweet[2]})
        else:
            for tweet in tweets[:25]:
                account.append({'Tweet_ID': tweet[0], 'Username': tweet[1], 'Tweet': tweet[2]})
    conn.close()
    return make_response(jsonify(account), 200) 
    
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