import logging

from flask import Flask, render_template, request, make_response, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request, create_access_token
from datetime import datetime, timedelta

import utils
import query

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(module)s:%(message)s')

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'super-secret-vote'
app.config["JWT_TOKEN_LOCATION"] = ['cookies']
app.config['JWT_COOKIE_NAME'] = 'access_token_cookie'
app.config['CSRF_ENABLED'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

jwt = JWTManager(app)



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
    verify_jwt_in_request()
    user = get_jwt_identity()
    logging.info(f"jwt identity is: '{user}'")
    return render_template('create_poll.html', groups=user['groups'], email=user['email'])

def create_jwt_access_token(user):
    userId = user[utils.USER_FIELD['id']]
    userEmail = user[utils.USER_FIELD['email']]
    userName = user[utils.USER_FIELD['name']]
    userGroups = user[utils.USER_FIELD['groups']]
    userBirthday = user[utils.USER_FIELD['birthday']]

    # Set the user's ID, name, and email as the identity in the JWT
    accessToken = create_access_token(identity={
        'id': userId,
        'email': userEmail,
        'name': userName,
        'groups': userGroups,
        'birthday': userBirthday
    })
    logging.info(f"access token is {accessToken}")
    return accessToken


@app.route('/process_user_login', methods=['POST'])
def process_login_form():
    logging.info("Processing logging form")
    email = request.form['email']
    password = request.form['password']
    if not query.authorize_user(email, password):
        return render_template("failed_login.html")
    user, polls = query.get_user_and_polls(email)
    if (not user):
        logging.info("Couldnt get user")
        return render_template("error.html")
    id = query.get_user(email)[utils.USER_FIELD['id']]
    accessToken = create_jwt_access_token(user)
    print(f"access: '{accessToken} and id {id}'\n")
    voted = query.get_voted(id, polls)
    logging.info(f"polls are {polls}")
    resp = make_response(render_template('main_page.html', id=id, polls=polls, voted=voted))
    resp.set_cookie('access_token_cookie', value=accessToken, expires=datetime.utcnow() + timedelta(hours=3))
    return resp
    
@app.route('/process_user_register', methods=['POST'])
def process_register_form():
    name = request.form['name']
    email = request.form['email']
    password = utils.encrypt(request.form['password'])
    birthday = request.form['birthday']
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

@jwt_required
@app.route('/process_poll_vote/<poll_id>', methods=['POST']) #TODO continue from here 
def poll_vote(poll_id):

    try:
        verify_jwt_in_request()
        user = get_jwt_identity()
    except BaseException as e:
        logging.warning(f"exception is {e}")
    optionNum = request.form.get('radar-option')
    logging.info(f"id {user['id']} voting on poll {poll_id} for option num {optionNum}")
    query.pick_poll_option(user['id'], poll_id, optionNum)
    optionValues = utils.str_to_list(query.get_poll(poll_id)[utils.POLL_FIELD['optionValues']])
    logging.info(f"values for {poll_id} are {optionValues} and optionNum is {optionNum}")
    return jsonify({"message": f"id {user['id']} voting on poll {poll_id} for option num {optionNum}", 
    "optionValues": optionValues, "selectedOption": optionNum})

if __name__ == '__main__':
    #print(query.submit_poll("creator", "title", "1", "desc", "asdf, bani"))
    #a = temp()
    #b = 1
    logging.info("Server startup")
    assert query.init_db() == True
    app.run(debug=True, host='0.0.0.0')
