from flask import Flask
from flask import request
from flask import jsonify
import json

from connect4 import *

app = Flask(__name__)


@app.route('/check_win', methods=['POST'])
def hello_world():
    print(request.json)
    board = request.json['board']
    last_move = request.json['last_move']
    print(f'{last_move=}')
    # print(json.loads(last_move))

    print(last_move['x'])
    was_won = Connect4Game.check_for_winners(board, last_move['x'], last_move['y'])

    response = jsonify({'won': was_won})
    print(response)
    return response


@app.route('/predict', methods=['POST'])
def predict():
    print(request.json)

    board = request.json['board']
    depth = request.json['depth']

    game_ai = Connect4AI()
    game_ai.checking_depth = depth
    prediction = game_ai.predict(board)

    return jsonify({'status': 'OK'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
