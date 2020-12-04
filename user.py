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

def authUser(cur, username, password):
    #authenticating user information
    if username == '' or password == '':
        return False
    cur.execute("SELECT * FROM UserAccounts WHERE username='{}'".format(str(username)))
    user = cur.fetchone()
    if user == None:
        return False
    elif user[0] == str(username) and user[1] == str(password):
        return True

# HELPER FUNCTIONS />---------------------------------------------------

@app.route('/', methods=['GET'])
def users():
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = []
    cur.execute("SELECT * FROM UserAccounts")
    usersSQL = cur.fetchall()
    if usersSQL == []:
        conn.close()
        return make_response(jsonify(usersSQL), 200)
    for user in usersSQL:
        account.append({'username': user[0], 'password': user[1], 'email': user[2]}) 
    conn.close()   
    return make_response(jsonify(account), 200)

@app.route('/users', methods=['GET', 'POST'])
def get_users():
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = []
    cur.execute("SELECT * FROM UserAccounts")
    usersSQL = cur.fetchall()
    if usersSQL == []:
        # Returns an empty array if no users have been created
        conn.close()
        return make_response(jsonify(usersSQL), 201)
    for user in usersSQL:
        account.append({'username': user[0], 'password': user[1], 'email': user[2]}) 
    conn.close()   
    return make_response(jsonify(account), 200)

@app.route('/userfollows/<username>', methods=['GET', 'POST'])
def get_followers(username):
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = []
    cur.execute("SELECT * FROM UserFollows WHERE followed='{}'".format(str(username)))
    followers = cur.fetchall()
    if followers == []:
        conn.close()
        return make_response("NOT FOUND", 404)
    for follows in followers:
        account.append({ username + ' is following':follows[1]})

    conn.close()
    return make_response(jsonify(account), 200)

@app.route('/create', methods=['POST'])
def create_user():
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = request.get_json(force=True)
    exists = userExist(cur, str(account['username']), str(account['email']))

    if exists:
        conn.close()
        return make_response("USERNAME ALREADY EXISTS", 409)
    else:
        cur.execute("INSERT INTO UserAccounts(username, password, email) VALUES (?,?,?)", (str(account['username']), str(account['password']), str(account['email'])))
        conn.commit()
        cur.execute("SELECT * FROM UserAccounts WHERE username='{}'".format(str(account['username'])))
        conn.close()
        return make_response("SUCCESS: USER CREATED", 201, {"location" : '/users'})
    conn.close()

@app.route('/auth', methods=['GET'])
def auth_user():
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = request.get_json(force=True)
    auth = authUser(cur, str(account['username']), str(account['password']))

    if auth:
        conn.close()
        return make_response("SUCCESS: USER AUTHENTICATED", 200)
    else:
        conn.close()
        return make_response("ERROR: Unsuccessful Authorization", 401)

    
@app.route('/addfollower', methods=['POST'])
def add_follower():
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = request.get_json(force=True)
    exists = followExist(cur, str(account['follower']), str(account['followed']))

    if not exists:
        conn.close()
        return make_response("USERNAME OR FOLLOWER NAME DOES NOT EXIST", 404)
    else:
        cur.execute("INSERT INTO UserFollows(followed, follower) VALUES (?,?)", (str(account['followed']), str(account['follower'])))
        conn.commit()
        cur.execute("SELECT * FROM UserFollows WHERE followed='{}'".format(str(account['followed'])))
        conn.close()
        return make_response("SUCCESS: USER FOLLOWED", 201, {"location" : '/userfollows/' + str(account['follower'])})
    conn.close()

@app.route('/removefollower', methods=['DELETE'])
def remove_follower():
    conn = connectDB(databaseName)
    cur = conn.cursor()
    account = request.get_json(force=True)
    cur.execute("SELECT * FROM UserFollows WHERE followed=? AND follower=?", (str(account['username']), str(account['followed'])))
    row = cur.fetchone()
    if row == None:
        conn.close()
        return make_response("ERROR: YOU ARE NOT FOLLOWING THIS USER", 404)
    if str(account['username']) == '':
        conn.close()
        return make_response("ERROR: USERNAME DOES NOT EXIST", 404)
    if str(account['followed']) == '':
        conn.close()
        return make_response("ERROR: USER FOLLOWING DOES NOT EXIST", 404)
    if str(account['username']) == str(account['followed']):
        conn.close()
        return make_response("ERROR: YOU CANNOT UNFOLLOW YOURSELF", 404)
    else:
        cur.execute("DELETE FROM UserFollows WHERE followed=? AND follower=?", (str(account['username']), str(account['followed'])))
        conn.commit()
        return make_response("SUCCESS: USER UNFOLLOWED", 201, {"location" : '/userfollows/' + str(account['username'])})
    conn.close()


if __name__ == '__main__':
    app.run(debug=True)
app.run()