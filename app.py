from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/process_user_login', methods=['POST'])
def process_login_form():
    email = request.form['email']
    password = request.form['password']
    # TODO add check of hashing password
    if not get_user(email, password):
        return render_template("failed_login.html")
    # should be (return show_main_page(email)), using diff for creating db and testing creation of poll
    

@app.route('/process_user_register', methods=['POST'])
def process_register_form():
  name = request.form['name']
  email = request.form['email']
  password = request.form['password']
  birthday = request.form['birthday']
  # TODO add hashing of password 
  submit_user(email, password, name, birthday)
  return render_template('index.html')

def submit_user(email, password, name, date):
    users_conn = sqlite3.connect('users.db')
    with users_conn:
        c = users_conn.cursor()
        # create the db if does not exist, maybe move to different function
        c.execute("""
        CREATE TABLE IF NOT EXISTS users 
        (
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            name TEXT NOT NULL,
            birthday TEXT NOT NULL,
            groups TEXT
        )
        """)
        # add the user, all users are in the "0" group, which is THE WORLD
        c.execute("INSERT INTO users VALUES (:email, :hashed_password, :name, :birthday, :groups)",
        {'email': email, 'hashed_password': password, 'name': name, 'birthday': date, 'groups': "0"})

def get_user(email, password):
    users_conn = sqlite3.connect('users.db')
    with users_conn:
        c = users_conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND hashed_password=?", (email, password))
        a = c.fetchall()
        print(a[0][2])
        return c.fetchall()

def get_user_polls(email):
    """"returns all polls"""
    pass

def show_main_page(email):
    users_conn = sqlite3.connect('users.db')
    user_groups = []
    with users_conn:
        c = users_conn.cursor()
        c.execute("SELECT * FROM groups WHERE email=?")
        user_groups = c.fetchall()

    # Build the query string for getting all polls related to specific user
    placeholders = ', '.join(['?'] * len(user_groups))
    query = f"SELECT * FROM polls WHERE group IN ({placeholders});"
    polls_conn = sqlite3.connect('polls.db')
    polls = []
    with polls_conn:
        c = polls_conn.cursor()
        c.execute(query, user_groups)
        polls = c.fetchall()
    #TODO return list of tuples, check code to see how to Enum properly over it
    return render_template("main_page.html", email, polls)
    #TODO - create that database and function to add votes to it

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    print("a")
        