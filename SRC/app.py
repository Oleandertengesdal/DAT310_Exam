from flask import Flask, request, redirect, url_for, flash, session, g, abort, render_template, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from init_db import *
from json import *
import sqlite3
import os
from datetime import datetime
from functools import wraps



app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = '9a00f4c9059ecc2c704dd2ade1e702b5'

app.config['UPLOAD_FOLDER'] = 'static/uploads/profile_pics'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_db():
    if not hasattr(g, '_database'):
        g._database = sqlite3.connect('database.db')
    return g._database

@app.teardown_appcontext
def teardown_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        print('Closing database connection')
        db.close()

def validate_user(username, password):
    conn = get_db()

    hash = get_hash_for_login(conn, username)
    if hash != None:
        return check_password_hash(hash, password)
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if validate_user(username, password) == True:
            print("User validated")
            try:
                print("User validated")
                conn = get_db()
                user = get_user_by_name(conn, username)
                session["username"] = user["username"]
                return redirect(url_for('index1'))
            except sqlite3.Error as err:
                return handle_exception(err)
        else:
            print("User not validated")
            error_message = "The username or password is incorrect"
            print(error_message)    
            return render_template('login.html', username='null', error_message=error_message )
    return render_template('login.html', username='null')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for('notloggedin'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/add_tweet', methods=['POST'])
def create_tweet():
    data = request.get_json()
    content = data.get('content')
    user_id = data.get('user_id')

    if not content:
        return jsonify({'error': 'Content is required'}), 400
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    try: 
        conn = get_db()
        user = get_user_by_name(conn, session["username"])

        add_tweet(conn, user_id, content)
        return jsonify({'message': 'Tweet created successfully'}), 201
    except sqlite3.Error as err:
        return handle_exception(err)

@app.route('/follow', methods=['POST'])
def follow_user():
    data = request.get_json()
    follower_id = data.get('follower_id')
    followed_id = data.get('followed_id')

    if not session.get("username"):
        return redirect(url_for('notloggedin'))
    
    conn = get_db()
    try:
        add_follow(conn, follower_id, followed_id)
        return jsonify({'message': 'success'}), 200
    except sqlite3.Error as err:
        return handle_exception(err)
    

@app.route('/unfollow', methods=['POST'])
def unfollow_user():
    data = request.get_json()
    follower_id = data.get('follower_id')
    followed_id = data.get('followed_id')

    if not session.get("username"):
        return redirect(url_for('login'))
    
    conn = get_db()
    try:
        remove_follow(conn, follower_id, followed_id)
        return jsonify({'message': 'success'}), 200
    except sqlite3.Error as err:
        return handle_exception(err)
    
@app.route('/get_followers', methods=['POST'])
def get_followers():
    data = request.get_json()
    user_id = data.get('user_id')
    conn = get_db()
    followers = get_followers_db(conn, user_id)
    return jsonify({'followers': followers})

@app.route('/get_following', methods=['POST'])
def get_following():
    data = request.get_json()
    user_id = data.get('user_id')
    conn = get_db()
    following = get_following_db(conn, user_id)
    return jsonify({'following': following})

@app.route('/is_following', methods=['POST']) 
def is_following():
    data = request.get_json()
    follower_id = data.get('follower_id')
    followed_id = data.get('followed_id')
    conn = get_db()
    is_following = is_following_db(conn, follower_id, followed_id)
    return jsonify({'is_following': is_following})

@app.route('/add_remove_like', methods=['POST'])
def add_remove_like():
    data = request.get_json()
    tweet_id = data.get('tweet_id')

    if not session.get("username"):
        return redirect(url_for('login'))
    
    conn = get_db()
    user = get_user_by_name(conn, session["username"])
    result = add_remove_like_db(conn, tweet_id, user["id"])

    if(result == 1):
        return jsonify({'message': 'Like added successfully'}), 201
    else:
        return jsonify({'message': 'Like removed successfully'}), 200

@app.route('/get_likes', methods=['POST'])
def get_likes():
    data = request.get_json()
    tweet_ids = data.get('tweet_ids')
    user = get_user_by_name(get_db(), session["username"])

    conn = get_db()
    likes_data = []

    for tweet_id in tweet_ids:
        likes = get_likes_by_tweet(conn, tweet_id)
        is_liked = is_liked_by_user(conn, tweet_id, user["id"])
        likes_data.append({
            'tweet_id': tweet_id,
            'likes': likes,
            'is_liked': is_liked
        })
    return jsonify({'likes_data': likes_data})

@app.route('/get_tweets_account', methods=['POST'])
def get_tweets_account():
    data = request.get_json()
    user_id = data.get('user_id')
    conn = get_db()
    tweets = get_initial_tweets_for_user(conn, user_id)
    print(tweets)
    tweet_data = []
    for tweet in tweets:
        tweet_id, user_id, content, created_at = tweet
        username = get_user_by_id(conn, user_id)["username"]
        tweet_data.append({
            'tweet_id': tweet_id,
            'user_id': user_id,
            'username': username, 
            'content': content,
            'created_at': created_at
        })
    return jsonify(tweet_data)


@app.route('/initial_tweets')
def initial_tweets():
    conn = get_db()
    tweets = get_initial_tweets(conn)
    tweet_data = []
    for tweet in tweets:
        tweet_id, user_id, content, created_at = tweet
        username = get_user_by_id(conn, user_id)["username"]
        tweet_data.append({
            'tweet_id': tweet_id,
            'user_id': user_id,
            'username': username, 
            'content': content,
            'created_at': created_at
        })
    print(tweet_data)
    return jsonify(tweet_data)

@app.route('/initial_tweets_for_user', methods=['POST'])
def initial_tweets_for_user():
    data = request.get_json()
    user_id = data.get('user_id')
    conn = get_db()
    tweets = initial_tweets_for_user(conn, user_id)
    tweet_data = []
    for tweet in tweets:
        tweet_id, user_id, content, created_at = tweet
        username = get_user_by_id(conn, user_id)["username"]
        tweet_data.append({
            'tweet_id': tweet_id,
            'user_id': user_id,
            'username': username, 
            'content': content,
            'created_at': created_at
        })
    return jsonify(tweet_data)

@app.route('/get_more_tweets', methods=['POST'])
def get_more_tweets():
    data = request.get_json()
    last_tweet_id = data.get('last_tweet_id')
    conn = get_db()
    tweets = get_more_tweets_db(conn, last_tweet_id)
    tweet_data = []
    for tweet in tweets:
        tweet_id, user_id, content, created_at = tweet
        username = get_user_by_id(conn, user_id)["username"]
        tweet_data.append({
            'tweet_id': tweet_id,
            'user_id': user_id,
            'username': username, 
            'content': content,
            'created_at': created_at
        })
    return jsonify(tweet_data)

@app.route('/get_following_tweets', methods=['POST'])
def get_following_tweets():
    data = request.get_json()
    user_id = data.get('user_id')
    conn = get_db()
    tweets = get_initial_tweets_for_followed_users(conn, user_id)
    tweet_data = []
    for tweet in tweets:
        tweet_id, user_id, content, created_at = tweet
        username = get_user_by_id(conn, user_id)["username"]
        tweet_data.append({
            'tweet_id': tweet_id,
            'user_id': user_id,
            'username': username, 
            'content': content,
            'created_at': created_at
        })
    return jsonify(tweet_data)


@app.route('/get_more_tweets_for_user', methods=['POST'])
def get_more_tweets_for_user():
    data = request.get_json()
    last_tweet_id = data.get('last_tweet_id')
    user_id = data.get('user_id')
    conn = get_db()
    tweets = get_more_tweets_for_user_db(conn, last_tweet_id, user_id)
    tweet_data = []
    for tweet in tweets:
        tweet_id, user_id, content, created_at = tweet
        username = get_user_by_id(conn, user_id)["username"]
        tweet_data.append({
            'tweet_id': tweet_id,
            'user_id': user_id,
            'username': username, 
            'content': content,
            'created_at': created_at
        })
    return jsonify(tweet_data)

@app.route('/get_more_tweets_for_followed_users', methods=['POST'])
def get_more_tweets_for_followed_users():
    data = request.get_json()
    last_tweet_id = data.get('last_tweet_id')
    user_id = data.get('user_id')
    conn = get_db()
    tweets = get_more_tweets_for_followed_users_db(conn, last_tweet_id, user_id)
    tweet_data = []
    for tweet in tweets:
        tweet_id, user_id, content, created_at = tweet
        username = get_user_by_id(conn, user_id)["username"]
        tweet_data.append({
            'tweet_id': tweet_id,
            'user_id': user_id,
            'username': username, 
            'content': content,
            'created_at': created_at
        })
    return jsonify(tweet_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None  
    if request.method == 'POST':
        username = request.form.get("rusername", "").strip()
        if username == "":
            error_message = "Username is required"
            return render_template('register.html', error_message=error_message, username='null')
        if len(username) < 3:
            error_message = "Username must be at least 3 characters"
            return render_template('register.html', error_message=error_message, username='null')
        email = request.form.get("email", "").strip()
        if email == "":
            error_message = "Email is required"
            return render_template('register.html', error_message=error_message, username='null')
        if email.count("@") != 1 or email.count(".") == 0:      
            error_message = "Invalid email"
            return render_template('register.html', error_message=error_message, username='null')
        password = request.form.get("password", "").strip()
        if password == "":
            error_message = "Password is required"
            return render_template('register.html', error_message=error_message, username='null')
        if len(password) < 6:
            error_message = "Password must be at least 6 characters"
            return render_template('register.html', error_message=error_message, username='null')
        confirm_password = request.form.get("confirm_password", "").strip()
        if confirm_password != password:
            error_message = "Passwords must match"
            return render_template('register.html', error_message=error_message, username='null')

        print(password + " " + confirm_password + " " + username + " " + email)

        try:   
            conn = get_db()
            user = get_user_by_name(conn, username)
            if user and user['id'] is not None:
                error_message = "Username already exists"
                return render_template('register.html', error_message=error_message, username='null') 
        except sqlite3.Error as err:
            error_message = str(err)
            return render_template('register.html', error_message=error_message, username='null')   

        try:
            hash = generate_password_hash(password)
            conn = get_db()
            id = add_user(conn, username, hash, email)
            session["username"] = username
            return redirect(url_for('index1'))
        except sqlite3.Error as err:
            error_message = str(err)
            return render_template('register.html', error_message=error_message, username='null') 

    # If it's a GET request or none of the conditions are met
    return render_template('register.html', username='null')

@app.route('/profile/<pusername>')
@login_required
def profile(pusername):
    if not session.get("username"):
        return redirect(url_for('notloggedin'))
    try:
        conn = get_db()
        user = get_user_by_name(conn, pusername)
        #tweets = get_tweets_for_user(conn, user["id"])
        email = user["email"]
        bio = user["bio"]
        created_at = user["created_at"]

        if isinstance(created_at, str):
            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
           
        formatted_created_at = created_at.strftime('%Y-%m-%d')
        user_id = user["id"]
        is_own_profile = session.get("username", None) == pusername
        username = session["username"]
        current_user = get_user_by_name(conn, username)
        current_user_id = current_user["id"]

        following_count = get_following_db(conn, user_id)
        followers_count = get_followers_db(conn, user_id)
    
        return render_template('account.html',followers_count=followers_count, following_count=following_count, current_user_id=current_user_id, pusername=pusername, username=username, user_id=user_id, user=user, is_own_profile=is_own_profile,  email=email, bio=bio, created_at=formatted_created_at)
    except sqlite3.Error as err:
        return handle_exception(err)
    
@app.route('/update_bio', methods=['POST'])
def update_bio():
    if request.method == 'POST':
        data = request.get_json()
        user_id = data.get('user_id')
        new_bio = data.get('bio')
        
        try:
            conn = get_db()
            oppdater_bio(conn, user_id, new_bio)
            user = get_user_by_id(conn, user_id)
            oppdatert_bio = user["bio"]
            print(oppdatert_bio)    
            return jsonify({'message': 'Bio updated successfully', 'bio': oppdatert_bio}), 200
        except sqlite3.Error as err:
            #feilmelding hvis det ikke funker
            return handle_exception(err)

@app.route('/initial_comments/<tweet_id>', methods=['GET'])
def initial_comments(tweet_id):
    conn = get_db()
    comments = get_comments_for_tweet(conn, tweet_id)
    print(comments)
    comment_data = []
    for comment in comments:
        comment_id, user_id, tweet_id, content, created_at = comment
        username = get_user_by_id(conn, user_id)["username"]
        comment_data.append({
            'comment_id': comment_id,
            'user_id': user_id,
            'tweet_id': tweet_id,
            'username': username,
            'content': content,
            'timestamp': created_at
        })
    return jsonify(comment_data)

@app.route('/comments/<tweet_id>')
@login_required
def comments(tweet_id):
    try:
        conn = get_db() 
        tweet = get_tweet_by_id(conn, tweet_id)
        tweet_content = tweet["content"]
        tweet_user_id = tweet["user_id"]
        created_at = tweet["created_at"]
        tweet_username = get_user_by_id(conn, tweet_user_id)["username"]
        username = session["username"]
        user_id = get_user_by_name(conn, username)["id"]
        return render_template('comments.html', user_id=user_id, username=username, tweet_id=tweet_id, tweet_content=tweet_content, created_at=created_at, tweet_user_id=tweet_user_id, tweet_username=tweet_username)
    except sqlite3.Error as err:
        return handle_exception(err)
    
@app.route('/add_comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    tweet_id = data.get('tweet_id')
    user_id = data.get('user_id')
    content = data.get('content')

    if not content:
        print("Content is required")
        return jsonify({'error': 'Content is required'}), 400
    if not user_id:
        print("User ID is required")
        return jsonify({'error': 'User ID is required'}), 400
    try: 
        conn = get_db()
        add_comment_db(conn, user_id, tweet_id, content)
        return jsonify({'message': 'Comment created successfully'}), 201
    except sqlite3.Error as err:
        return handle_exception(err)

@app.route('/get_comments', methods=['POST'])
def get_comments():
    data = request.get_json()
    tweet_id = data.get('tweet_id')
    conn = get_db()
    comments = get_comments_for_tweet(conn, tweet_id)
    return jsonify({'comments': comments})

@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for('notloggedin'))

@app.route('/notloggedin')
def notloggedin():
    return render_template('notlogged.html', username='null')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.json.get('search', '')
    conn = get_db()
    print(search_term)  
    tweets = search_tweets(conn, search_term)
    print(tweets)
    tweet_data = []
    for tweet in tweets:
        tweet_id, user_id, content, created_at = tweet
        username = get_user_by_id(conn, user_id)["username"]
        tweet_data.append({
            'tweet_id': tweet_id,
            'user_id': user_id,
            'username': username, 
            'content': content,
        })
        print(tweet_data)
    return jsonify(tweet_data)

@app.route('/')
@login_required
def index1():
    if not session.get("username"):
        return redirect(url_for('notloggedin'))
    user_id = get_user_by_name(get_db(), session["username"])["id"]
    return render_template('index1.html',  username=session.get("username", None), user_id=user_id)        

@app.route('/get_profile_pic/<user_id>', methods=['GET'])
def get_profile_pic(user_id):
    conn = get_db()
    profile_pic = get_profile_picture(conn, user_id)
    return jsonify({'profile_pic': profile_pic})

@app.route('/get_profile_pic_layout/<username>', methods=['GET'])
def get_profile_pic_layout(username):
    conn = get_db()
    user = get_user_by_name(conn, username) 
    user_id = user["id"]
    profile_pic = get_profile_picture(conn, user_id)
    return jsonify({'profile_pic': profile_pic})

@app.route('/get_profile_pic_comments/<username>', methods=['GET'])
def get_profile_pic_comments(username):
    conn = get_db()
    user = get_user_by_name(conn, username) 
    user_id = user["id"]
    profile_pictu = get_profile_picture(conn, user_id)
    return jsonify({'profile_pictu': profile_pictu})

@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print(f"Filename: {filename}")  # Debugging
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print(f"File path: {file_path}")  # Debugging
        
        user_id = request.form.get('user_id')
        print(f"User ID: {user_id}")  # Debugging
        if user_id:
            conn = get_db()
            oppdater_profilbilde(conn, user_id, filename)
            print("Profile picture updated")  # Debugging
            return jsonify({"message": "File successfully uploaded"})
    
    return jsonify({"message": "File upload failed"})

@app.errorhandler(404)
def not_found_error(error):
    username = session["username"]
    user = get_user_by_name(get_db(), username)
    user_id = user["id"]
    return render_template('notfound.html', username=username, user_id=user_id), 404

@app.errorhandler(Exception)
def handle_exception(error):
    # Log the error
    app.logger.error(f"An error occurred: {error}")

    username = session.get("username", None)
    
    user = get_user_by_name(get_db(), username)
    user_id = user["id"]

    # Get the error code and message
    error_code = getattr(error, 'code', 500)
    error_message = getattr(error, 'description', 'Internal Server Error')

    return render_template('error.html', username=username, user_id=user_id, error_code=error_code, error_message=error_message), error_code