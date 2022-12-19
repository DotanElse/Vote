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

def submit_user(email, password, name, date):
    conn = sqlite3.connect('users.db')
    with conn:
        c = conn.cursor()
        # create the db if does not exist, maybe move to different function
        c.execute("""
        CREATE TABLE IF NOT EXISTS users 
        (
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            name TEXT NOT NULL,
            birthday TEXT NOT NULL
        )
        """)
        # add the user
        c.execute("INSERT INTO users VALUES (:email, :hashed_password, :name, :birthday)",
        {'email': email, 'hashed_password': password, 'name': name, 'birthday': date})

def get_user(email, password):
    conn = sqlite3.connect('users.db')
    with conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND hashed_password=?", (email, password))
        return c.fetchall()

@app.route('/process_user_login', methods=['POST'])
def process_login_form():
    email = request.form['email']
    password = request.form['password']
    # TODO add check of hashing password
    if get_user(email, password):
        return render_template("main_page.html")
    return render_template("failed_login.html")

@app.route('/process_user_register', methods=['POST'])
def process_register_form():
  name = request.form['name']
  email = request.form['email']
  password = request.form['password']
  birthday = request.form['birthday']
  # TODO add hashing of password 
  submit_user(email, password, name, birthday)
  return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    print("a")
        