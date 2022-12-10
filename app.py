from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

def submit_user():
    conn = sqlite3.connect('users.db')
    with conn:
        c = conn.cursor()
        c.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
        email text,
        hashed_password text,
        first_name text,
        last_name text,
        birthday text
        )
        """
        )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
        