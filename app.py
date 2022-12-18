from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

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

def register_user():
    #TODO - get form data
    #TODO - check if valid input
    #submit_user with the details
    pass

def get_user(email):
    conn = sqlite3.connect('users.db')
    with conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        return c.fetchall()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
        