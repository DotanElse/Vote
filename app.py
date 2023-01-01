import logging

from flask import Flask, render_template, request

import utils
import query

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(module)s:%(message)s')

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
    if not query.authorize_user(email, password):
        return render_template("failed_login.html")
    return query.show_main_page(email)
    # should be (return show_main_page(email)), using diff for creating db and testing creation of poll

@app.route('/process_user_register', methods=['POST'])
def process_register_form():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    birthday = request.form['birthday']
    # TODO add hashing of password 
    if query.submit_user(email, password, name, birthday):
        return render_template('index.html')
    return render_template('error.html') # eventually change to popup at main site (additional param to main_page)

@app.route('/process_pool_creation', methods=['POST'])
def process_pool_creation():
    creator = request.form.get('creator')
    title = request.form.get('title')
    group = request.form.get('group_')
    description = request.form.get('description')
    optionNames = request.form.get('optionNames')
    if query.submit_pool(creator, title, group, description, optionNames):
        return render_template('index.html')
    return render_template('error.html')

def temp():
    """Testing tool"""
    query.get_pools_by_groups()

if __name__ == '__main__':
    #print(query.submit_pool("creator", "title", "1", "desc", "asdf, bani"))
    #a = temp()
    #b = 1
    #query.show_main_page("dotanelse@gmail.com")
    logging.info("Server startup")
    assert query.init_db() == True
    app.run(debug=True, host='0.0.0.0')
