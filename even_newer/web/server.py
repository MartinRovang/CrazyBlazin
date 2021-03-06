from flask import Flask, render_template, url_for, request, jsonify
import pickle
from datetime import datetime, time
import numpy as np
import io
from PIL import Image
import matplotlib.pyplot as plt
import json
import jsonpickle
import random
from flask import Flask, render_template, url_for, request, Response, send_file
import http.client
from datetime import datetime, time
from matplotlib import image
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
from pathlib import Path
import uuid
import glob
import shutil
import logging
from werkzeug.datastructures import FileStorage
from flask_restful import Resource, Api, reqparse
from werkzeug.utils import secure_filename

from flask_socketio import SocketIO

from things import *


app = Flask(__name__)
api = Api(app)

logging.basicConfig(filename='server.log', level=logging.DEBUG)
socketio = SocketIO(app, cors_allowed_origins="*", logger = logging)

@socketio.on('msg')
def msg(msg):
    socketio.emit('clientMsg', msg, broadcast=True, include_self=False)

@socketio.on('connect')
def test_connect():
    socketio.emit('datainfo', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

# @app.route("/stonks")
# def front():
#     return render_template('stonks.html')

@app.route("/")
def frontpage():
    return render_template('music.html')

#ed0ce8c7-a4fe-11eb-badb-40167e77d41a




# if __name__ == "__main__":
socketio.run(app, debug=True)