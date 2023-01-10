import logging

from flask import Flask, render_template, request, make_response
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime, timedelta

import utils
import query

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(module)s:%(message)s')

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'super-secret-vote'

jwt = JWTManager(app)
app.config["JWT_TOKEN_LOCATION"] = ['cookies']
app.config['JWT_COOKIE_NAME'] = 'access_token_cookie'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@jwt_required
@app.route('/create_poll')
def create_poll():
    logging.info("Create poll view")
    token = request.cookies.get('access_token_cookie')
    print(f"token is {token}")
    verify_jwt_in_request()
    user = get_jwt_identity()
    return render_template('create_poll.html', groups=user['groups'], email=user['email'])

@app.route('/process_user_login', methods=['POST'])
def process_login_form():
    logging.info("Processing logging form")
    email = request.form['email']
    password = request.form['password']
    # TODO add check of hashing password
    if not query.authorize_user(email, password):
        return render_template("failed_login.html")
    user, polls = query.get_user_and_polls(email)
    access_token = utils.get_access_token(user)
    print(f"access: '{access_token}'")
    resp = make_response(render_template('main_page.html', user=user, polls=polls))
    resp.set_cookie('access_token_cookie', value=access_token, expires=datetime.utcnow() + timedelta(hours=3))
    return resp
    
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

@app.route('/process_poll_creation', methods=['POST'])
def process_poll_creation():
    creator = request.form.get('creator').strip()
    title = request.form.get('title').strip()
    group = request.form.get('group_').strip()
    description = request.form.get('description').strip()
    optionNames = request.form.get('optionNames').strip()
    public = request.form.get('public').strip()
    duration = request.form.get('duration').strip()
    if query.submit_poll(creator, title, group, description, optionNames, duration, public):
        return render_template('index.html')
    return render_template('error.html')

@app.route('/process_poll_vote/<id>', methods=['POST'])
def poll_vote(id):
    print(query.get_poll(id))

def temp():
    """Testing tool"""
    query.get_polls_by_groups()

if __name__ == '__main__':
    #print(query.submit_poll("creator", "title", "1", "desc", "asdf, bani"))
    #a = temp()
    #b = 1
    logging.info("Server startup")
    assert query.init_db() == True
    app.run(debug=True, host='0.0.0.0')
