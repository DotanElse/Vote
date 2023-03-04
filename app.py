import json
import logging

from flask import Flask, render_template, request, make_response, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request, create_access_token
from datetime import datetime, timedelta

import utils
import query

logging.basicConfig(level=logging.INFO, format='%(lineno)d:%(funcName)s:%(message)s')

app = Flask(__name__, static_folder='static')

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
    logging.info("start")

    token = request.cookies.get('access_token_cookie')
    verify_jwt_in_request()
    user = get_jwt_identity()
    groups_id = utils.str_to_list(user['groups'])
    groups = []
    for id in groups_id:
        group = query.get_group(id)
        group_name = group[utils.GROUP_FIELD['name']]
        groups.append(group_name)
    return render_template('create_poll.html', groups=utils.list_to_str(groups), email=user['email'])

@jwt_required
@app.route('/create_group')
def create_group():
    logging.info("start")

    token = request.cookies.get('access_token_cookie')
    verify_jwt_in_request()
    user = get_jwt_identity()

    return render_template('create_group.html', id=user['id'])

def create_jwt_access_token(user):
    logging.info("start")

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
    return accessToken


@app.route('/process_user_login', methods=['POST'])
def process_login_form():
    logging.info("start")

    email = request.form['email']
    password = request.form['password']

    if not query.authorize_user(email, password):
        return render_template("error.html")
    
    user, template = query.setup_main_page(email)

    accessToken = create_jwt_access_token(user)
    resp = make_response(template)
    resp.set_cookie('access_token_cookie', value=accessToken, expires=datetime.utcnow() + timedelta(hours=3))
    return resp
    

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # handle form submission
        picture = request.files.get("picture")
        if picture:
            picture.save("path/to/your/assets/directory/picture.jpg")
        # other form fields handling
    else:
        # render the form template
        return render_template("signup.html")

@app.route('/process_user_register', methods=['POST'])
def process_register_form():
    logging.info("start")

    name = request.form['name']
    email = request.form['email']
    password = utils.encrypt(request.form['password'])
    birthday = request.form['birthday']
    picture = request.files.get("picture")

    if query.submit_user(email, password, name, birthday, picture):
        return render_template('index.html')
    
    return render_template('error.html') # eventually change to popup at main site (additional param to main_page)

@app.route('/process_poll_creation', methods=['POST'])
def process_poll_creation():
    logging.info("start")
    
    creator = request.form.get('creator').strip()
    title = request.form.get('title').strip()
    group_name = request.form.get('group_').strip() # this is the group name that the user chose
    logging.info(f"group name is {group_name}")
    group_id = query.get_group_id(group_name)
    logging.info(f"group id is {group_id}")
    description = request.form.get('description').strip()
    optionNames = utils.list_to_str(request.form.getlist('option'))
    duration = request.form.get('duration').strip()

    if query.submit_poll(creator, title, group_id, description, optionNames, duration):
        return main_page()
    
    return render_template('error.html')

@app.route('/process_group_creation', methods=['POST'])
def process_group_creation():
    logging.info("start")
    
    creator = request.form.get('creator').strip()
    groupName = request.form.get('name').strip()
    description = request.form.get('description').strip()
    public = request.form.get('public').strip()

    if query.submit_group(creator, groupName, description, public):
        return main_page()
    
    return render_template('error.html')

@jwt_required
@app.route('/process_poll_vote/<poll_id>', methods=['POST'])
def poll_vote(poll_id):
    logging.info("start")

    try:  
        verify_jwt_in_request()
        user = get_jwt_identity()
    except BaseException as e:
        logging.warning(f"{e} raised")
    
    optionNum = request.form.get('radar-option')
    query.pick_poll_option(user['id'], poll_id, optionNum)
    optionValues = utils.str_to_list(query.get_poll(poll_id)[utils.POLL_FIELD['optionValues']])

    return jsonify({"message": f"id {user['id']} voting on poll {poll_id} for option num {optionNum}", 
    "optionValues": optionValues, "selectedOption": optionNum})

@jwt_required
@app.route('/process_group_invite/<group_id>', methods=['POST'])
def admin_group_invite(group_id):
    logging.info("start")
    data = json.loads(request.data)
    selected_ids = data["ids"]
    logging.info(f"sel ids are {selected_ids} with group {group_id}")
    try:
        verify_jwt_in_request()
        user = get_jwt_identity()
    except BaseException as e:
        logging.warning(f"{e} raised")
    
    query.invite_users(user['id'], group_id, selected_ids)
    return jsonify({"message": f"id {user['id']} invited {selected_ids} to {group_id}"})


@jwt_required
@app.route('/process_group_removal/<group_id>', methods=['POST'])
def admin_group_removal(group_id):
    logging.info("JOJOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
    data = json.loads(request.data)
    selected_ids = data["ids"]
    logging.info(f"sel ids are {selected_ids} with group {group_id}")
    try:
        verify_jwt_in_request()
        user = get_jwt_identity()
    except BaseException as e:
        logging.warning(f"{e} raised")
    
    query.remove_users(user['id'], group_id, selected_ids)
    return jsonify({"message": f"id {user['id']} removed {selected_ids} from {group_id}"})

@app.route('/vote/<poll_id>')
def view_poll(poll_id):
    logging.info("start")
    try:
        verify_jwt_in_request()
    except BaseException as e:
        logging.warning(f"{e} raised")
        return query.poll_view(poll_id, None)

    return query.poll_view(poll_id, get_jwt_identity()['id'])

@app.route('/user/<user_id>')
def view_user(user_id):
    logging.info("start")
    try:
        verify_jwt_in_request()
    except BaseException as e:
        logging.warning(f"{e} raised")
        return query.user_view(user_id, None)

    return query.user_view(user_id, get_jwt_identity()['id'])

@app.route('/group/<group_id>')
def view_group(group_id):
    logging.info("start")
    try:
        verify_jwt_in_request()
    except BaseException as e:
        logging.warning(f"{e} raised")
        return query.group_view(group_id, None)

    return query.group_view(group_id, get_jwt_identity()['id'])

@app.route('/handle-invite-notification', methods=['POST'])
def handle_invite_notification():
    data = request.get_json()  # Get data from JavaScript request
    query.handle_invite_notification(data['id'], data['group'], data['choice'])
    return '', 204  # Return empty response with 204 status code

@app.route('/handle-request-notification', methods=['POST'])
def handle_request_notification():
    data = request.get_json()  # Get data from JavaScript request
    logging.info(f"initiator is {data['initiator']}")
    query.handle_request_notification(data['initiator'], data['group'], data['choice'])
    return '', 204  # Return empty response with 204 status code

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    logging.info(f"{data['text']} was searched")
    return '', 204  # Return empty response with 204 status code

@app.route('/logout')
@jwt_required()
def logout():
    resp = make_response(render_template('index.html'))
    resp.set_cookie('access_token_cookie', value="", expires=-1)
    return resp

@app.route('/main')
@jwt_required()
def main_page():
    user = get_jwt_identity()
    email = user['email']

    user, template = query.setup_main_page(email)

    accessToken = create_jwt_access_token(user)
    resp = make_response(template)
    resp.set_cookie('access_token_cookie', value=accessToken, expires=datetime.utcnow() + timedelta(hours=3))
    return resp


@app.route('/leave-group', methods=['POST'])
def leave_group():
    data = request.get_json() # Get data from JavaScript request
    query.remove_users(None, data['group'], [data['id']])
    query.remove_group_from_user(data['id'], data['group'])
    return '', 204

@app.route('/join-group', methods = ['POST'])
def request_join_group():
    data = request.get_json() # Get data from JavaScript request
    result = query.handle_group_request(data['group'], data['id'])
    response_data = {'message': result}
    if result == "Accepted":
        return jsonify(response_data), 200
    return jsonify(response_data), 200

@app.route('/check-requested', methods = ['POST'])
def check_requested_status():
    data = request.get_json() # Get data from JavaScript request
    result = query.check_requested_status(data['group'], data['id'])
    response_data = {'message': result}
    if result == True:
        return jsonify(response_data), 200
    return jsonify(response_data), 200

if __name__ == '__main__':
    logging.info("Server startup")
    assert query.init_db() == True
    app.run(debug=True, host='0.0.0.0')
