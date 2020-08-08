import markdown
import os
import io
import shelve
import werkzeug
from tinytag import TinyTag
import uuid 
import sys

# Import the framework
from flask import Flask, g, json, send_from_directory
from flask_restful import Resource, Api, reqparse, fields, marshal, request

# Create an instance of Flask
app = Flask(__name__)

# Create the API
api = Api(app)

UPLOAD_DIRECTORY = './storage'
TEMP_DIRECTORY = './temp'

# if not os.path.exists(UPLOAD_DIRECTORY):
#     os.makedirs(UPLOAD_DIRECTORY)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("voices.db")
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    # db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:
        content = markdown_file.read()
    return markdown.markdown(content)

class SoundList(Resource):
    def get(self):
        # args = request.args
        # print("args: {}" .format(args), file=sys.stderr)

        # query = request.query_string
        # print("query: {}" .format(query), file=sys.stderr)

        # for k, v in args.items():
        #     print("{}: {}" .format(k,v), file=sys.stderr)

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
                if filename is not None and filename in shelf[key]['name'] and (shelf[key]['duration'] < float(maxduration)):
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
                    if filename is not None and filename in shelf[key]['name'] and (shelf[key]['duration'] < float(maxduration)):
                        if shelf[key] not in sounds:
                            print("Adding item for filename and filesize.", file=sys.stderr)
                            sounds.append(shelf[key])
                    else:
                        if filename is None and (shelf[key]['duration'] < float(maxduration)):
                            if shelf[key] not in sounds:
                                print("Adding item for filesize", file=sys.stderr)
                                sounds.append(shelf[key])


        print("Done!!!", file=sys.stderr)
        return {'message': 'Success', 'data': sounds}, 200

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
        if (parser.__name__ == "Wave"):
            tag = TinyTag.get(TEMP_DIRECTORY + '/temp.wav')
            fid = uuid.uuid1()
        else:
            return {'message': 'Sound not registered. Not a WAVE file', 'filetype': parser.__name__}, 400

        # Save file
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
            if filename in shelf[key]['name']:
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
            if filename in shelf[key]['name']:
                archname = shelf[key]['id'] + shelf[key]['name']
                print("archname: {}" .format(archname), file=sys.stderr)
                # return send_from_directory("/usr/src/app/storage", archname, as_attachment=True)
                return send_from_directory("/usr/src/app/storage", archname)
        return {'message': 'Sound not found', 'data': {}}, 404


# class Sound(Resource):
#     def get(self, identifier):
#         shelf = get_db()

#         # If the key does not exist in the data store, return a 404 error.
#         if not (identifier in shelf):
#             return {'message': 'Sound not found', 'data': {}}, 404

#         return {'message': 'Sound found', 'data': shelf[identifier]}, 200

#     def delete(self, identifier):
#         shelf = get_db()

#         # If the key does not exist in the data store, return a 404 error.
#         if not (identifier in shelf):
#             return {'message': 'Sound not found', 'data': {}}, 404

#         del shelf[identifier]
#         return '', 204


api.add_resource(SoundPost, '/post')
api.add_resource(SoundDownload, '/download')
api.add_resource(SoundList, '/list')
api.add_resource(SoundInfo, '/info')
