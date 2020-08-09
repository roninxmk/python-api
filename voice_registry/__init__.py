import markdown
import os
import io
import shelve
import werkzeug
from tinytag import TinyTag
import uuid 
import sys
from passlib.apps import custom_app_context as pwd_context
import re

# Import the framework
from flask import Flask, g, json, send_from_directory, render_template, redirect, url_for
from flask_restful import Resource, Api, reqparse, fields, marshal, request 
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth


app = Flask(__name__)
app.config['TESTING'] = False
app.config['LOGIN_DISABLED'] = False

# Create the API
api = Api(app)

# Authentication
theauth = HTTPBasicAuth()
# theauth = HTTPTokenAuth()

UPLOAD_DIRECTORY = './storage'
TEMP_DIRECTORY = './temp'

# if not os.path.exists(UPLOAD_DIRECTORY):
#     os.makedirs(UPLOAD_DIRECTORY)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("sounds.db")
    return db

def get_userdb():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("users.db")
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    # db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/readme')
def readme():
    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:
        content = markdown_file.read()
    return markdown.markdown(content)

# # Route for handling the login page logic
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != 'admin' or request.form['password'] != 'admin':
#             error = 'Invalid Credentials. Please try again.'
#         else:
#             return redirect(url_for('home'))
#     return render_template('login.html', error=error)


class SoundList(Resource):
    def get(self):
        filename = request.args.get('name')
        maxduration = request.args.get('maxduration')
        filesize = request.args.get('size')

        print("filename: {}" .format(filename), file=sys.stderr)
        print("maxduration: {}" .format(maxduration), file=sys.stderr)
        print("filesize: {}" .format(filesize), file=sys.stderr)

        if maxduration is None:
            maxduration = "9999999999"

        shelf = get_db()
        keys = list(shelf.keys())

        print("Keys: {}" .format(keys), file=sys.stderr)

        sounds = []
        for key in keys:
            if filesize is None:
                if filename is not None and filename == shelf[key]['name'] and (shelf[key]['duration'] < float(maxduration)):
                    print("Found filename", file=sys.stderr)
                    if shelf[key] not in sounds:
                        print("Adding item for filename.", file=sys.stderr)
                        sounds.append(shelf[key])
                else:
                    if filename is None and (shelf[key]['duration'] < float(maxduration)):
                        if shelf[key] not in sounds:
                            print("Adding item.", file=sys.stderr)
                            sounds.append(shelf[key])
            else:
                if (shelf[key]['size'] == filesize):
                    if filename is not None and filename == shelf[key]['name'] and (shelf[key]['duration'] < float(maxduration)):
                        if shelf[key] not in sounds:
                            print("Adding item for filename and filesize.", file=sys.stderr)
                            sounds.append(shelf[key])
                    else:
                        if filename is None and (shelf[key]['duration'] < float(maxduration)):
                            if shelf[key] not in sounds:
                                print("Adding item for filesize", file=sys.stderr)
                                sounds.append(shelf[key])


        print("Done!!!", file=sys.stderr)
        if len(sounds) == 0:
            return {'message': 'Sound not found.'}, 200
        else:
            return {'message': 'Success!', 'data': sounds}, 200

class SoundPost(Resource):
    def post(self):

        # Write content to temporary file
        tempfile = os.path.join(TEMP_DIRECTORY, "temp.wav")
        with open(tempfile, "wb") as fp:
            fp.write(request.get_data())

        # Analyze file
        with io.open(tempfile, 'rb') as fh:
            parser = TinyTag.get_parser_class(tempfile, fh)

        # Check if WAV file
        print("Tag Parser Name: {}" .format(parser.__name__), file=sys.stderr)
        if (parser.__name__ == "Wave"):
            tag = TinyTag.get(TEMP_DIRECTORY + '/temp.wav')
            fid = uuid.uuid1()
        else:
            return {'message': 'Sound not registered. Not a WAVE file.', 'filetype': parser.__name__}, 400

        if (tag.filesize < 12):
            return {'message': 'Sound not registered. Empty WAVE file.', 'size': tag.filesize}, 400

        # Save file
        print("Tag Title: {}" .format(tag.title), file=sys.stderr)
        print("Filename: {}" .format(UPLOAD_DIRECTORY + fid.hex + tag.title + ".wav"))
        filename = os.path.join(UPLOAD_DIRECTORY, fid.hex + tag.title + ".wav")
        with open(filename, "wb") as fp:
            fp.write(request.get_data())

        # Store in database
        shelf = get_db()
        shelf[fid.hex] = {'id': fid.hex, 'name': tag.title + ".wav", 'duration': tag.duration, 'size': tag.filesize}

        return {'message': 'Sound registered', 'id': fid.hex, 'name': tag.title + ".wav", 'size': tag.filesize, 'duration': tag.duration}, 201

class SoundInfo(Resource):
    def get(self):
        filename = request.args['name']

        print("filename: {}" .format(filename), file=sys.stderr)

        shelf = get_db()
        keys = list(shelf.keys())

        sounds = []
        for key in keys:
            if filename == shelf[key]['name']:
                sounds.append(shelf[key])

        if len(sounds) == 0:
            return {'message': 'Sound not found', 'data': {}}, 404
        else:
            return {'message': 'Sound found', 'data': sounds}, 200
        print("Done!!!", file=sys.stderr)

class SoundDownload(Resource):
    def get(self):
        filename = request.args['name']

        print("filename: {}" .format(filename), file=sys.stderr)

        shelf = get_db()
        keys = list(shelf.keys())

        for key in keys:
            if filename == shelf[key]['name']:
                archname = shelf[key]['id'] + shelf[key]['name']
                print("archname: {}" .format(archname), file=sys.stderr)
                # UPLOAD_PATH does not work in 'send_from_directory'. Path needs to be absolute
                # return send_from_directory("/usr/src/app/storage", archname, as_attachment=True)
                return send_from_directory("/usr/src/app/storage", archname)
        return {'message': 'Sound not found', 'data': {}}, 404


### Authenticated section

def check_password(password, hashpwd):
    print("Checking password...", file=sys.stderr)
    print(password, file=sys.stderr)
    print(hashpwd, file=sys.stderr)
    return pwd_context.verify(password, hashpwd)

@theauth.verify_password
def verify_password(username, password):
    print("username: {}" .format(username), file=sys.stderr)
    print("password: {}" .format(password), file=sys.stderr)

    if (username is None or username == "") or (password is None or password == ""):
        print("Invalid username or password", file=sys.stderr)
        return False

    # Check database
    print("Get DB", file=sys.stderr)
    shelf = get_userdb()
    print("Get keys", file=sys.stderr)
    keys = list(shelf.keys())
    for key in keys:
        print("key: {}" .format(key), file=sys.stderr)
        isok = check_password(password, shelf[key]['password'])
        print("isok: {}" .format(isok), file=sys.stderr)
        if (username == shelf[key]['user']) and (isok):
            return username
    return False

class User(Resource):
    def post(self):
        auth = request.json.get('auth')
        user = request.json.get('username')
        pwd = request.json.get('password')
        usertype = request.json.get('type') # permission levels: 0 (normal) or 1 (admin)
        uid = uuid.uuid1()
        hashpwd = self.hash_password(pwd)
        print("uid: {}" .format(uid.hex), file=sys.stderr)
        print("auth: {}" .format(auth), file=sys.stderr)
        print("user: {}" .format(user), file=sys.stderr)
        print("pwd: {}" .format(pwd), file=sys.stderr)
        print("type: {}" .format(usertype), file=sys.stderr)
        print("hashpwd: {}" .format(hashpwd), file=sys.stderr)

        if auth is None:
            auth = "dummy"
        # Store in database
        shelf = get_userdb()
        keys = list(shelf.keys())

        if len(keys) == 0: # There are no users registered
            shelf['superuser'] = {'id': 'superuser', 'user': 'admin', 'type': '1','password': hashpwd}
            return {'message': 'Admin account created!', 'id': 'superuser', 'username': 'admin', 'password': hashpwd, 'type': '1'}, 201

        # Check if superuser
        if self.verify_password(auth, shelf['superuser']['password']):
            print("Auth passed.", file=sys.stderr)
            # If user is admin, then admin wants to update its account
            if user == 'admin':
                print("User is admin.", file=sys.stderr)
                shelf['superuser'] = {'id': 'superuser', 'user': 'admin', 'type': '1','password': hashpwd}
                return {'message': 'Admin account updated!', 'id': 'superuser', 'username': 'admin', 'password': hashpwd, 'type': '1'}, 201
            else: # If not, admin is creating an account.
                # Admin can create type 0 or type 1
                # Admin cannot update accounts
                # Check if user exists
                print("User is not admin.", file=sys.stderr)
                for key in keys:
                    if user in shelf[key]['user']:
                        return {'message': 'User already exists.', 'data': {'id': shelf[key]['id'], 'username': user}}, 204
                # If passed, then the user is new. Create new user
                amsg = 'User registered.'
                if usertype is None:
                    usertype = '0'
                else: 
                    amsg = 'Administrator registered.'
                shelf[uid.hex] = {'id': uid.hex, 'user': user, 'password': hashpwd, 'type': usertype}
                return {'message': amsg, 'id': uid.hex, 'username': user, 'password': hashpwd, 'type': usertype}, 201
        else:
            # Check if user exists
            for key in keys:
                if user == shelf[key]['user']:
                    # If user exists and if auth is None, it is a new user trying to signup. 
                    # Send an error
                    if (auth is None) or not (self.verify_password(auth, shelf[key]['password'])):
                        return {'message': 'Authorization failed.', 'data': {}}, 401
                    else:
                        # User exists and auth is verified, it is an update.
                        # Update user
                        olduid = shelf[key]['id']
                        shelf[olduid] = {'id': olduid, 'user': user, 'password': hashpwd, 'type': shelf[key]['type']}
                        return {'message': 'User updated!', 'id': olduid, 'username': user, 'password': hashpwd, 'type': shelf[key]['type']}, 201

        # Otherwise, it is only a normal user signing up
        shelf[uid.hex] = {'id': uid.hex, 'user': user, 'password': hashpwd, 'type': '0'}
        return {'message': 'User registered', 'id': uid.hex, 'username': user, 'password': hashpwd, 'type': '0'}, 201


    def get(self):
        user = request.json.get('username')
        pwd = request.json.get('password')

        searchname = request.args.get('user')

        print("user: {}" .format(user), file=sys.stderr)
        print("pwd: {}" .format(pwd), file=sys.stderr)

        # Check database
        shelf = get_userdb()
        keys = list(shelf.keys())
        users = []
        for key in keys:
            # If user is authenticated, it can see information
            if user == shelf[key]['user'] and self.verify_password(pwd, shelf[key]['password']):
                # If user does not have enough privileges, it can only see its own info
                # no matter which parameters it passed
                if shelf[key]['type'] == '0':
                    users.append(shelf[key])
                    return {'message': 'USer info', 'data': {users}}, 200
                elif shelf[key]['type'] == '1':
                    # If the user has enough privileges, it can browse users
                    for anotherkey in keys:
                        if searchname is None:
                            users.append(shelf[anotherkey])
                        if searchname == shelf[anotherkey]['user']:
                            users.append(shelf[anotherkey])
                            return {'message': 'User info', 'data': {users}}, 200
                    return {'message': 'Users info', 'data': {users}}, 200
                        
        # Could not find viable user
        return {'message': 'Authorization failed', 'data': {}}, 401

        # shelf[uid.hex] = {'id': uid.hex, 'user': user, 'password': hashpwd}
        # return {'message': 'User registered', 'id': uid.hex, 'username': user, 'password': hashpwd}, 201

    def hash_password(self, password):
        return pwd_context.encrypt(password)

    def verify_password(self, password, hashpwd):
        return pwd_context.verify(password, hashpwd)

class AuthTest(Resource):
    # decorators = [theauth.login_required]
    @theauth.login_required
    def get(self):
        return {"meaning_of_life": 42}

class SoundAuthList(Resource):
    @theauth.login_required
    def get(self):
        filename = request.args.get('name')
        maxduration = request.args.get('maxduration')
        filesize = request.args.get('size')

        print("filename: {}" .format(filename), file=sys.stderr)
        print("maxduration: {}" .format(maxduration), file=sys.stderr)
        print("filesize: {}" .format(filesize), file=sys.stderr)

        if maxduration is None:
            maxduration = "9999999999"

        shelf = get_db()
        keys = list(shelf.keys())

        print("Keys: {}" .format(keys), file=sys.stderr)

        sounds = []
        for key in keys:
            if filesize is None:
                if filename is not None and filename == shelf[key]['name'] and (shelf[key]['duration'] < float(maxduration)):
                    print("Found filename", file=sys.stderr)
                    if shelf[key] not in sounds:
                        print("Adding item for filename.", file=sys.stderr)
                        sounds.append(shelf[key])
                else:
                    if filename is None and (shelf[key]['duration'] < float(maxduration)):
                        if shelf[key] not in sounds:
                            print("Adding item.", file=sys.stderr)
                            sounds.append(shelf[key])
            else:
                if (shelf[key]['size'] == filesize):
                    if filename is not None and filename == shelf[key]['name'] and (shelf[key]['duration'] < float(maxduration)):
                        if shelf[key] not in sounds:
                            print("Adding item for filename and filesize.", file=sys.stderr)
                            sounds.append(shelf[key])
                    else:
                        if filename is None and (shelf[key]['duration'] < float(maxduration)):
                            if shelf[key] not in sounds:
                                print("Adding item for filesize", file=sys.stderr)
                                sounds.append(shelf[key])
        print("Done!!!", file=sys.stderr)
        if len(sounds) == 0:
            return {'message': 'Sound not found.'}, 200
        else:
            return {'message': 'Success!', 'data': sounds}, 200

class SoundAuthInfo(Resource):
    @theauth.login_required
    def get(self):
        filename = request.args['name']

        print("filename: {}" .format(filename), file=sys.stderr)

        self.shelf = get_db()
        keys = list(self.shelf.keys())

        sounds = []
        for key in keys:
            if filename == self.shelf[key]['name']:
                sounds.append(self.shelf[key])

        if len(sounds) == 0:
            return {'message': 'Sound not found', 'data': {}}, 404
        else:
            return {'message': 'Sound found', 'data': sounds}, 200
        print("Done!!!", file=sys.stderr)

class SoundAuthDownload(Resource):
    @theauth.login_required
    def get(self):
        filename = request.args['name']

        print("filename: {}" .format(filename), file=sys.stderr)

        print("Get DB", file=sys.stderr)
        self.shelf = get_db()
        print("Get keys", file=sys.stderr)
        keys = list(self.shelf.keys())

        for key in keys:
            print("key: {}" .format(key), file=sys.stderr)
            if filename == self.shelf[key]['name']:
                print("id: {}" .format(self.shelf[key]['id']), file=sys.stderr)
                print("name: {}" .format(self.shelf[key]['name']), file=sys.stderr)
                archname = self.shelf[key]['id'] + self.shelf[key]['name']
                print("archname: {}" .format(archname), file=sys.stderr)
                # UPLOAD_PATH does not work in 'send_from_directory'. Path needs to be absolute
                # return send_from_directory("/usr/src/app/storage", archname, as_attachment=True)
                return send_from_directory("/usr/src/app/storage", archname)
        return {'message': 'Sound not found', 'data': {}}, 404


api.add_resource(SoundPost, '/post')
api.add_resource(SoundDownload, '/download')
api.add_resource(SoundList, '/list')
api.add_resource(SoundInfo, '/info')

# api.add_resource(Login, '/login')
api.add_resource(User, '/users')
api.add_resource(SoundAuthList, '/authlist')
api.add_resource(SoundAuthInfo, '/authinfo')
api.add_resource(SoundAuthDownload, '/authdownload')
api.add_resource(AuthTest, '/authtest')
