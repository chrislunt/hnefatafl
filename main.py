# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
from flask import Flask
from flask import render_template
from flask import request
from flask import make_response # for the 404 page, not yet done
from flask import abort

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

from lib import game

@app.route('/')
def hello():
    return render_template('base.html')

@app.route('/starting_board')
def starting_board():
    # return the standard board
    board = game.starting_board()
    return board


@app.route('/move', methods = ['POST'])
def move():
    if not request.json:
        abort(400)
#    app.logger.info(request.json)
    board = game.move(request.json['player'], request.json['board'])

    return board

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python38_app]
