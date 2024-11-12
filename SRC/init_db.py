import sqlite3

def create_table(conn):
    cur = conn.cursor()
    try: 

        sql = ("CREATE TABLE users ("
               "user_id INTEGER PRIMARY KEY,"
               "username TEXT NOT NULL UNIQUE,"
               "password_hash VARCHAR(120) NOT NULL,"
               "email TEXT NOT NULL,"
               "bio TEXT DEFAULT 'Bio'," 
               "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);" )
        cur.execute(sql) 

        sql = ("CREATE TABLE tweets ("
               "tweet_id INTEGER PRIMARY KEY,"
               "user_id INTEGER NOT NULL,"
               "content TEXT NOT NULL,"
               "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
               "FOREIGN KEY (user_id) REFERENCES users(user_id)"
               ");" )
        cur.execute(sql) 

        sql = ("CREATE TABLE follows ("
               "followee_id INTEGER NOT NULL,"
               "follower_id INTEGER NOT NULL,"
               "PRIMARY KEY (follower_id, followee_id),"
               "FOREIGN KEY (follower_id) REFERENCES users(user_id),"
               "FOREIGN KEY (followee_id) REFERENCES users(user_id)"
               ");" )
        cur.execute(sql) 

        sql = ("CREATE TABLE likes (" 
               "tweet_id INTEGER NOT NULL,"
               "user_id INTEGER NOT NULL,"
               "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
               "PRIMARY KEY (tweet_id, user_id),"
               "FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id),"
               "FOREIGN KEY (user_id) REFERENCES users(user_id)"
               ");" )
        
        cur.execute(sql)  
        conn.commit()

        sql = ("CREATE TABLE profile_picture ("
                "user_id INTEGER PRIMARY KEY,"
                "profile_picture TEXT DEFAULT 'default.jpg',"
                "FOREIGN KEY (user_id) REFERENCES users(user_id)"
                ");" )
        
        cur.execute(sql)
        conn.commit()

        sql = ("CREATE TABLE comments ("
                "comment_id INTEGER PRIMARY KEY,"
                "user_id INTEGER NOT NULL,"
                "tweet_id INTEGER NOT NULL,"
                "content TEXT NOT NULL,"
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                "FOREIGN KEY (user_id) REFERENCES users(user_id),"
                "FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id)"
                ");" )
        
        cur.execute(sql)
        conn.commit()


    except sqlite3.Error as e:
        print(print(f"Error creating table: {e}."))
    else:
        print("Table created successfully.")
    finally:
        cur.close()  

#legg til ny bruker
def add_user(conn, username, password_hash, email):
    cur = conn.cursor()
    try:
        sql = ("INSERT INTO users (username, password_hash, email, bio) "
        "VALUES (?, ?, ?, 'Bio');")
        cur.execute(sql, (username, password_hash, email))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding user: {e}.")
        return -1
    else:
        print("User {} added with id {} created successfully.".format(username, cur.lastrowid))
        return cur.lastrowid
    finally:
        cur.close()

#legg til nytt inlegg
def add_tweet(conn, user_id, content):
    cur = conn.cursor()
    try:
        sql = ("INSERT INTO tweets (user_id, content) "
        "VALUES (?, ?);")
        cur.execute(sql, (user_id, content))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding tweet: {e}.")
        return -1
    else:
        print("Tweet added successfully.")
        return cur.lastrowid
    finally:
        cur.close()
#get inital tweets 
def get_initial_tweets(conn):
    cur = conn.cursor()
    try:
        sql = "SELECT tweet_id, user_id, content, strftime('%Y-%m-%d %H:%M:%S', created_at) AS created_at FROM tweets ORDER BY created_at DESC LIMIT 5;"
        cur.execute(sql)
        tweets = cur.fetchall()
        return tweets
    except sqlite3.Error as e:
        print(f"Error getting initial tweets: {e}.")
        return []
    finally:
        cur.close()

#get more tweets
def get_more_tweets_db(conn, tweet_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM tweets WHERE tweet_id < ? ORDER BY created_at DESC LIMIT 10;")
        cur.execute(sql, (tweet_id,))
        tweets = cur.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting more tweets: {e}.")
    else:
        return tweets
    finally:
        cur.close()

#get initial tweets for user
def get_initial_tweets_for_user(conn, user_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM tweets WHERE user_id = ? ORDER BY created_at DESC LIMIT 5;")
        cur.execute(sql, (user_id,))
        tweets = cur.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting initial tweets for user: {e}.")
    else:
        return tweets
    finally:
        cur.close()

#get more tweets for user
def get_more_tweets_for_user_db(conn, user_id, tweet_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM tweets WHERE user_id = ? AND tweet_id < ? ORDER BY created_at DESC LIMIT 10;")
        cur.execute(sql, (user_id, tweet_id))
        tweets = cur.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting more tweets for user: {e}.")
    else:
        return tweets
    finally:
        cur.close()

#get initial tweets for followed users
def get_initial_tweets_for_followed_users(conn, user_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM tweets WHERE user_id IN (SELECT followee_id FROM follows WHERE follower_id = ?) ORDER BY created_at DESC LIMIT 10;")
        cur.execute(sql, (user_id,))
        tweets = cur.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting initial tweets for followed users: {e}.")
    else:
        return tweets
    finally:
        cur.close()

#get more tweets for followed users
def get_more_tweets_for_followed_users_db(conn, user_id, tweet_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM tweets WHERE user_id IN (SELECT followee_id FROM follows WHERE follower_id = ?) AND tweet_id < ? ORDER BY created_at DESC LIMIT 10;")
        cur.execute(sql, (user_id, tweet_id))
        tweets = cur.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting more tweets for followed users: {e}.")
    else:
        return tweets
    finally:
        cur.close()

#hent inlegg basert på id
def get_tweet(conn, tweet_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM tweets WHERE tweet_id = ?;")
        cur.execute(sql, (tweet_id,))
        for row in cur:
            (id, user_id, content, created_at) = row
            return {"tweet_id": id, "user_id": user_id, "content": content, "created_at": created_at}
        else:
            #tweet does not exist
            return {
                "tweet_id": None
            }
    except sqlite3.Error as e:
        print(f"Error getting tweet: {e}.")
        return -1
    else:
        return None
    finally:
        cur.close()

#slett inlegg
def delete_tweet(conn, tweet_id):
    cur = conn.cursor()
    try:
        sql = ("DELETE FROM tweets WHERE tweet_id = ?;")
        cur.execute(sql, (tweet_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error deleting tweet: {e}.")
        return -1
    else:
        print("Tweet deleted successfully.")
        return cur.lastrowid
    finally:
        cur.close()

#rediger inlegg
def edit_tweet(conn, tweet_id, content):
    cur = conn.cursor()
    try:
        sql = ("UPDATE tweets SET content = ? WHERE tweet_id = ?;")
        cur.execute(sql, (content, tweet_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error editing tweet: {e}.")
        return -1
    else:
        print("Tweet edited successfully.")
        return cur.lastrowid
    finally:
        cur.close()

#hent bruker basert på id
def get_user_by_id(conn, user_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM users WHERE user_id = ?;")
        cur.execute(sql, (user_id,))
        for row in cur:
            (id, name, hash, email, bio, created_at) = row
            return {"id": id, "username": name, "password_hash": hash, "email": email, "bio": bio, "created_at": created_at}
        else:
            #user does not exist
            return {
                "username": "Not found",
                "id": None                
            }
        
    except sqlite3.Error as e:
        print(f"Error getting user by id: {e}.")
        return -1
    else:
        return cur.lastrowid
    finally:
        cur.close()

#hent bruker basert på brukernavn
def get_user_by_name(conn, username):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM users WHERE username = ?;")
        cur.execute(sql, (username,))
        for row in cur:
            (id, name, hash, email, bio, created_at) = row
            return {"id": id, "username": name, "password_hash": hash, "email": email, "bio": bio, "created_at": created_at}
        else:
            #user does not exist
            return {
                "username": "Not found",
                "id": None                
            }
        
    except sqlite3.Error as e:
        print(f"Error getting user by name: {e}.")
        return -1
    else:
        return cur.lastrowid
    finally:
        cur.close()

#hent hash for innlogging
def get_hash_for_login(conn, username):
    cur = conn.cursor()
    try:
        sql = ("SELECT password_hash FROM users WHERE username = ?;")
        cur.execute(sql, (username,))
        for row in cur:
            (hash,) = row
            print("hash: " + hash)
            return hash
        else:
            print("User not found.")
            return None
    except sqlite3.Error as e:
        print(f"Error getting hash for login: {e}.")
    else:
        return hash
    finally:
        cur.close()

#hent tweets basert på bruker
def get_tweets_by_user(conn, user_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM tweets WHERE user_id = ?;")
        cur.execute(sql, (user_id,))
        tweets = cur.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting tweets by user: {e}.")
    else:
        return tweets
    finally:
        cur.close()

#hent følgere basert på bruker
def get_followers_by_user(conn, user_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM follows WHERE followee_id = ?;")
        cur.execute(sql, (user_id,))
        followers = cur.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting followers by user: {e}.")
    else:
        return followers
    finally:
        cur.close()

#hent tweets
def get_tweets(conn):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM tweets;")
        cur.execute(sql)
        tweets = cur.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting tweets: {e}.")
    else:
        return tweets
    finally:
        cur.close()

#hent brukere
def get_users(conn):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM users;")
        cur.execute(sql)
        users = cur.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting users: {e}.")
    else:
        return users
    finally:
        cur.close()

#legg til følger
def add_follow(conn, follower_id, followee_id):
    cur = conn.cursor()
    try:
        sql = ("INSERT INTO follows (follower_id, followee_id) "
        "VALUES (?, ?);")
        cur.execute(sql, (follower_id, followee_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding follow: {e}.")
        return
    else:
        print("Follow added successfully.")
        return cur.lastrowid
    finally:
        cur.close()


#fjern følger
def remove_follow(conn, follower_id, followee_id):
    cur = conn.cursor()
    try:
        sql = ("DELETE FROM follows WHERE follower_id = ? AND followee_id = ?;")
        cur.execute(sql, (follower_id, followee_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error removing follow: {e}.")
        return -1
    else:
        print("Follow removed successfully.")
        return cur.lastrowid
    finally:
        cur.close()

def get_followers_db(conn, user_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT COUNT(*) FROM follows WHERE followee_id = ?;")
        cur.execute(sql, (user_id,))
        followers = cur.fetchone()[0]
        return followers
    except sqlite3.Error as e:
        print(f"Error getting followers: {e}.")
    finally:
        cur.close()

def get_following_db(conn, user_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT COUNT(*) FROM follows WHERE follower_id = ?;")
        cur.execute(sql, (user_id,))
        following = cur.fetchone()[0]
        return following
    except sqlite3.Error as e:
        print(f"Error getting following: {e}.")
    finally:
        cur.close()


def is_following_db(conn, follower_id, followee_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM follows WHERE follower_id = ? AND followee_id = ?;")
        cur.execute(sql, (follower_id, followee_id))
        following = cur.fetchall()
        return len(following) > 0
    except sqlite3.Error as e:
        print(f"Error checking if following: {e}.")
        return False
    finally:
        cur.close()

#hent tweets basert på likes
def get_tweets_by_likes(conn, user_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM tweets WHERE tweet_id IN (SELECT tweet_id FROM likes WHERE user_id = ?);")
        cur.execute(sql, (user_id,))
        likes = cur.fetchall()
        return likes
    except sqlite3.Error as e:
        print(f"Error getting tweets by likes: {e}.")
    finally:
        cur.close()

#hent likes basert på tweet
def get_likes_by_tweet(conn, tweet_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT COUNT(*) FROM likes WHERE tweet_id = ?;")
        cur.execute(sql, (tweet_id,))
        like_count = cur.fetchone()[0]
        return like_count
    except sqlite3.Error as e:
        print(f"Error getting likes by tweet: {e}.")
        return -1
    finally:
        cur.close()

def is_liked_by_user(conn, tweet_id, user_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM likes WHERE tweet_id = ? AND user_id = ?;")
        cur.execute(sql, (tweet_id, user_id))
        likes = cur.fetchall()
        return len(likes) > 0
    except sqlite3.Error as e:
        print(f"Error checking if tweet is liked: {e}.")
        return False
    finally:
        cur.close()


#legg til like
#legg til like
def add_remove_like_db(conn, tweet_id, user_id):
    cur = conn.cursor()
    try:
        # Check if the like already exists
        cur.execute("SELECT * FROM likes WHERE tweet_id = ? AND user_id = ?", (tweet_id, user_id))
        existing_like = cur.fetchone()
        print(existing_like)
        if existing_like != None:
            #sletter
            sql = ("DELETE FROM likes WHERE tweet_id = ? AND user_id = ?;")
            cur.execute(sql, (tweet_id, user_id))
            conn.commit()
            print("Like removed successfully.")
            return 1
        else:
            # legger til
            sql = ("INSERT INTO likes (tweet_id, user_id) VALUES (?, ?);")
            cur.execute(sql, (tweet_id, user_id))
            conn.commit()
            print("Like added successfully.")
            return -1
    except sqlite3.Error as e:
        print(f"Error adding like: {e}.")
        return -1
    finally:
        cur.close()

'''
#fjern like
def remove_like(conn, tweet_id, user_id):
    cur = conn.cursor()
    try:
        sql = ("DELETE FROM likes WHERE tweet_id = ? AND user_id = ?;")
        cur.execute(sql, (tweet_id, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error removing like: {e}.")
        return -1
    else:
        print("Like removed successfully.")
        return cur.lastrowid
    finally:
        cur.close()
'''
def oppdater_profilbilde(conn, user_id, profile_picture):
    cur = conn.cursor()
    try:
        sql = ("UPDATE profile_picture SET profile_picture = ? WHERE user_id = ?;")
        cur.execute(sql, (profile_picture, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating profile picture: {e}.")
        return -1
    else:
        print("Profile picture updated successfully.")
        return cur.lastrowid
    finally:
        cur.close()

def get_tweet_by_id(conn, tweet_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM tweets WHERE tweet_id = ?;")
        cur.execute(sql, (tweet_id,))
        for row in cur:
            (id, user_id, content, created_at) = row
            return {"tweet_id": id, "user_id": user_id, "content": content, "created_at": created_at}
    except sqlite3.Error as e:
        print(f"Error getting tweet by id: {e}.")
    finally:
        cur.close()

def add_comment_db(conn, user_id, tweet_id, content):
    cur = conn.cursor()
    try:
        sql = ("INSERT INTO comments (user_id, tweet_id, content) VALUES (?, ?, ?);")
        cur.execute(sql, (user_id, tweet_id, content))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding comment: {e}.")
        return -1
    else:
        print("Comment added successfully.")
        return cur.lastrowid
    finally:
        cur.close()

def get_comments_for_tweet(conn, tweet_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT * FROM comments WHERE tweet_id = ?;")
        cur.execute(sql, (tweet_id,))
        comments = cur.fetchall()
        return comments
    except sqlite3.Error as e:
        print(f"Error getting comments for tweet: {e}.")
    finally:
        cur.close()

def search_tweets(conn, search_query):
    print("search query: " + search_query)
    cur = conn.cursor()
    try:
        sql = "SELECT * FROM tweets WHERE LOWER(content) LIKE LOWER(?);"
        cur.execute(sql, (f"%{search_query}%",))
        tweets = cur.fetchall()
        return tweets
    except sqlite3.Error as e:
        print(f"Error searching tweets: {e}.")
    finally:
        cur.close()

def get_profile_picture(conn, user_id):
    cur = conn.cursor()
    try:
        sql = ("SELECT profile_picture FROM profile_picture WHERE user_id = ?;")
        cur.execute(sql, (user_id,))
        row = cur.fetchone()
        if row:
            (profile_picture,) = row
        else:
            # If no profile picture is found, insert a default profile picture
            default_profile_picture = 'Random-profile-pic.jpg'  # Replace with your default profile picture file name
            insert_default_profile_picture(conn, user_id, default_profile_picture)
            profile_picture = default_profile_picture
        return profile_picture
    except sqlite3.Error as e:
        print(f"Error getting profile picture: {e}.")
    finally:
        cur.close()

def insert_default_profile_picture(conn, user_id, profile_picture):
    cur = conn.cursor()
    try:
        sql = ("INSERT INTO profile_picture (user_id, profile_picture) VALUES (?, ?);")
        cur.execute(sql, (user_id, profile_picture))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting default profile picture: {e}.")
    finally:
        cur.close()

#oppdater bio
def oppdater_bio(conn, user_id, bio):
    cur = conn.cursor()
    try:
        sql = ("UPDATE users SET bio = ? WHERE user_id = ?;")
        cur.execute(sql, (bio, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating bio: {e}.")
        return -1
    else:
        print("Bio updated successfully.")
        return cur.lastrowid
    finally:
        cur.close()

if __name__ == "__main__":
    try:    
        conn = sqlite3.connect('database.db')
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}.")
    else:
        create_table(conn)
        conn.close()