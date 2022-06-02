from distutils.command.config import config
import requests
from flask import session
from fileinput import filename
import mimetypes
import ssl
from requests.adapters import HTTPAdapter, Retry
from urllib import response
from flask import send_from_directory, stream_with_context
from ast import While
import json
from flask import render_template
from datetime import datetime
import logging
import time
import sys
import legalnlp
from io import BytesIO
from zipfile import ZipFile
# from requests.adapters import HTTPAdapter, Retry
import queue
import threading as th
import os
from werkzeug.utils import secure_filename
import builder
from flask import Flask, flash, request, redirect, url_for, render_template, current_app, Response, send_file, g
#now = datetime.now()
import flask_socketio
from flask_socketio import SocketIO, emit, send, join_room, leave_room, close_room, rooms, disconnect
#from app import app as application

from threading import Lock
import threading

current = os.getcwd()
UPLOAD_FOLDER = current
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'rtf', 'png'}


#uploaded = False
#filenamestr = ''
app = Flask(__name__, instance_relative_config=True)


# @app.before_first_request
# def before_first_request():
#     app.before_first_request(assign_user)
app.config["USERS"] = {}
app.config['USERINDEX'] = 0


with app.app_context():

    sess = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(
        max_retries=retry, pool_connections=100, pool_maxsize=100)
    sess.mount('http://', adapter)
    sess.mount('https://', adapter)
    socketio = SocketIO(current_app)

    def assign_user():
        global userindex
        # current_app.app_context().push()
        current_app.config['user'] = "user" + \
            str(app.config['USERINDEX'])
        app.config['USERINDEX'] += 1
        app.config["USERS"][app.config['USERINDEX']] = {
            current_app.config['user']: app.config['USERINDEX']}
        current_app.config['UPLOADED'] = False
        current_app.config['filenamestr'] = ''
        current_app.config['TESTING'] = True
        current_app.config['DEBUG'] = False

        current_app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

        current_app.config['ASSIGNED'] = False
    # current_app.app_context().push()

        current_app.secret_key = "secret key"
        print(current_app.config['user'])
        return current_app.config

    @socketio.on('join')
    def on_join(data):
        print(data)

        username = data['username']
        room = data['room']
        print(username)
        print(room)
        join_room(room)
        send(data, to=room)

    @socketio.on('leave')
    def on_leave(data):
        room = data['room']
        leave_room(room)
        send(data, to=room)

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower(
            ) in ALLOWED_EXTENSIONS

    class MessageAnnouncer:

        def __init__(self):
            self.listeners = []

        def listen(self):
            self.listeners.append(queue.Queue(maxsize=5))
            return self.listeners[-1]

        def announce(self, msg):
            # We go in reverse order because we might have to delete an element, which will shift the
            # indices backward
            for i in reversed(range(len(self.listeners))):
                try:
                    self.listeners[i].put_nowait(msg)
                except queue.Full:
                    del self.listeners[i]

    announcer = MessageAnnouncer()

    def format_sse(data: str, event=None) -> str:
        """Formats a string and an event name in order to follow the event stream convention.
        >>> format_sse(data=json.dumps({'abc': 123}), event='Jackson 5')
        'event: Jackson 5\\ndata: {"abc": 123}\\n\\n'
        """
        msg = f'data: {data}\n\n'
        if event is not None:
            msg = f'event: {event}\n{msg}'
        return msg

    @current_app.route('/ping')
    def ping():
        msg = format_sse(data='pong')
        announcer.announce(msg=msg)
        return {}, 200
    # @current_app.route('/listen', methods=['GET'])
    # def listen():

    #     def stream():
    #         messages = announcer.listen()  # returns a queue.Queue
    #         while True:
    #             msg = messages.get()  # blocks until a new message arrives
    #             print(msg)
    #             yield msg

    #     return Response(stream(), mimetype='text/event-stream')

    def stream_template(template_name, **context):
        current_app.update_template_context(context)
        t = current_app.jinja_env.get_template(template_name)
        rv = t.stream(context)
        rv.enable_buffering(5)
        return rv

    @current_app.route('/reload', methods=['GET'])
    def reload():
        current_app.config['UPLOADED'] = False
        app.config['USERINDEX'] -= 1
        return redirect(url_for('upload'))

    @current_app.route('/result', methods=['GET', 'POST'], endpoint='result')
    def result():

        time.sleep(1)

        return render_template('nlpresults.html',  uploaded=current_app.config['UPLOADED'], iframe='box')
        # return Response(stream_with_context(generate()), mimetype='text/event-stream')

    @ current_app.route('/box', methods=['GET', 'POST'], endpoint='box')
    def box():
        res = gen()
        label_types = [['Provision', 'Provision_url', 'Instrument', 'Instrument_url'],
                       ['CITATION', 'JUDGE', 'PROVISION',  'CASENAME', 'LEGAL_TEST', 'COURT'], ['CONCLUSION', 'AXIOM', 'ISSUE']]
        colors = ["red", "green", "blue", "yellow",
                  "orange", "purple", "pink", "brown", "black"]

        return render_template('box.html', results=res, label_types=label_types, colors=colors)

    @ current_app.route('/gen', methods=['GET', 'POST'], endpoint='gen')
    def gen():
        flow = {}

        r = legalnlp.main(current_app.config['filenamestr'])

        def generate():
            if r:
                for dict in r:
                    for key, value in dict.items():
                        # if key in flow:
                        #     flow[key].append(value)
                        # else:
                        #     flow[key] = value
                        yield {key: value}
        return stream_with_context(generate())

    @ current_app.route('/', methods=['GET', 'POST'],  endpoint='index')
    def index():
        assign_user()
        if(current_app.config['UPLOADED']):
            return render_template('nlpresults.html', uploaded=current_app.config['UPLOADED'], iframe='box')
        else:

            return redirect(url_for('upload'))

    @ current_app.route('/upload', methods=['GET', 'POST'], endpoint='upload')
    def upload():
        global UPLOAD_FOLDER
        print(UPLOAD_FOLDER)

        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):

                current_app.config['filenamestr'] = UPLOAD_FOLDER + \
                    secure_filename(file.filename)
                print(os.path.join(
                    UPLOAD_FOLDER, current_app.config['filenamestr']))
                file.save(os.path.join(
                    UPLOAD_FOLDER, current_app.config['filenamestr']))
                print('upload_image filename: ' +
                      current_app.config['filenamestr'])
                current_app.config['UPLOADED'] = True
                print(current_app.config['UPLOADED'])

            # return Response(results, mimetype='text/event-stream')

        if(current_app.config['UPLOADED']):
            return redirect(url_for('result'))
        return render_template('nlpupload.html')

    @current_app.route('/uploads/<filename>')
    def download_file(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

    @current_app.route('/upload_files/<string:result>')
    def display(result):
        return send_from_directory(UPLOAD_FOLDER, result)


if __name__ == '__main__':
    app.run(host='192.168.0.190', port=5000, threaded=True,
            load_dotenv=True, debug=True)
    # current_app.run(host='
else:
    application = app
