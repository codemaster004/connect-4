import pyglet
from pyglet import shapes
from pyglet.window import mouse

from itertools import groupby
from random import randint
from functools import lru_cache
from datetime import datetime
from threading import Thread
import json
import sys
from multiprocessing import Process

from pprint import pprint


class Connect4Game:
    def __init__(self, window_obj, batch_obj, log=False, use_ai=True):
        self.log = log
        self.use_ai = use_ai

        self.game_won = False
        self.current_row = None
        self.picked_column = None
        self.current_player = 1
        self.players = [1, 2]
        self.player_colors = {
            2: (255, 198, 109),
            1: (136, 136, 198)
        }

        self.game_width = 7
        self.game_height = 7
        self.game_state = {i: [0 for j in range(self.game_width)] for i in range(self.game_height)}

        self.window = window_obj
        self.initiate_window_events()

        self.batch = batch_obj

        self.labels = []
        self.rectangles = []
        self.circles = []
        self.circle_spacing = 10
        self.circle_diameter = self.window.width / 7 - self.circle_spacing
        self.circle_radius = self.circle_diameter / 2

    def initiate_window_events(self):
        @self.window.event
        def on_draw():
            window.clear()
            batch.draw()

        @self.window.event
        def on_mouse_press(x, y, button, modifier):
            if button is mouse.LEFT:
                self.handle_user_move(x)

    def move(self):
        self.game_state, self.current_row = Connect4Game.update_game_state(self.game_state,
                                                                           self.picked_column,
                                                                           self.current_player)

        if self.current_row is not None:
            player_color = self.player_colors[self.current_player]
            self.draw_circle(self.picked_column, self.game_height - self.current_row - 1, player_color)
            self.current_player = self.players[self.current_player % len(self.players)]
        else:
            print('End of column')
            return

        if self.log:
            pprint(self.game_state)

        self.game_won = self.check_for_winners(self.game_state, self.picked_column, self.current_row)

    def handle_user_move(self, x):
        if self.game_won:
            self.restart()
            return

        for i in range(self.window.width):
            x_min = self.circle_diameter * i + self.circle_spacing * i + self.circle_spacing * 0.5
            x_max = self.circle_diameter * i + self.circle_spacing * i + self.circle_spacing * 0.5 + self.circle_diameter
            if x_min <= x <= x_max:
                self.picked_column = i

        if self.picked_column is None:
            return

        self.move()

        if self.game_won:
            self.winner_screen()
        elif self.use_ai:
            game_ai = Connect4AI()
            game_state = {row: self.game_state[row].copy() for row in self.game_state}
            pprint(game_state)
            self.picked_column = game_ai.predict(game_state)
            self.move()

            if self.game_won:
                self.winner_screen()

    @staticmethod
    def update_game_state(game_state, column, player):
        for i in range(len(game_state) - 1, -1, -1):
            if game_state[i][column] == 0:
                game_state[i][column] = player
                return game_state, i

        return game_state, None

    @classmethod
    def check_for_winners(cls, game_state, new_x, new_y):
        # Slant growing
        b = new_y + new_x
        axis = [game_state[i][b - i] for i in range(b, -1, -1) if 0 <= i < 7 and b - i < 7]
        # print(f'{axis=}')
        if cls.check_direction(axis) is not None:
            return True

        # Slant lowering
        b = new_y - new_x
        # print(f'{axis=}')
        axis = [game_state[i][i - b] for i in range(b, len(game_state)) if 0 <= i < 7 and 0 <= i - b <= 6]
        if cls.check_direction(axis) is not None:
            return True

        # Horizontal
        row = game_state[new_y]
        # print(f'{row=}')
        if cls.check_direction(row) is not None:
            return True

        # Vertical
        column = [game_state[row][new_x] for row in game_state]
        # print(f'{column=}')
        if cls.check_direction(column) is not None:
            return True

        return False

    @classmethod
    def check_direction(cls, path):
        for player, value_groups in groupby(path):
            list_values = list(value_groups)
            if len(list_values) >= 4 and list_values[0] != 0:
                return player

    def winner_screen(self):
        rectangle = shapes.Rectangle(
            x=0,
            y=0,
            height=self.window.height,
            width=self.window.width,
            color=(0, 0, 0),
            batch=self.batch
        )
        rectangle.opacity = 150
        self.rectangles.append(rectangle)
        # self.labels.append(pyglet.text.Label(
        #     'Game Won by Player: ',
        #     font_size=36,
        #     color=(255, 255, 255, 255),
        #     x=100,
        #     anchor_x='center',
        #     y=100,
        #     batch=self.batch))

    def draw_circle(self, col, row, color=(50, 51, 53)):
        x = self.circle_radius + self.circle_diameter * col + self.circle_spacing * col + self.circle_spacing * 0.5
        y = self.circle_radius + self.circle_diameter * row + self.circle_spacing * row + self.circle_spacing * 0.5
        self.circles.append(shapes.Circle(x, y, self.circle_radius, color=color, batch=self.batch))

    def create_board(self):
        self.rectangles.append(shapes.Rectangle(
            x=0,
            y=0,
            height=self.window.height,
            width=self.window.width,
            color=(35, 36, 37),
            batch=self.batch
        ))

        for j in range(self.game_height):
            for i in range(self.game_width):
                self.draw_circle(i, j)

    def start_window(self):
        self.window.set_caption('Connect 4')
        pyglet.app.run()

    def restart(self):
        self.game_state = {i: [0 for j in range(self.game_width)] for i in range(self.game_height)}
        self.game_won = False
        self.current_row = None
        self.picked_column = None
        self.current_player = 1

        self.rectangles = []
        self.circles = []

        self.create_board()


class Connect4AI:
    def __init__(self):
        self.checking_depth = 11  # 16.0 s
        self.transposition_tables = {}

    def predict(self, board):
        best_move = 0
        best_result = float('-inf')
        for action in [0, 1, 2, 3, 4, 5, 6]:
            game_state = {row: board[row].copy() for row in board}
            current_player = 2

            game_state, row = Connect4Game.update_game_state(game_state, action, current_player)
            if row is None:
                continue
                # return float('-inf')

            result = self.minimax(game_state, {'x': action, 'y': row}, self.checking_depth, float('-inf'), float('inf'),
                                  False)
            # self.start_branch()
            # result = Process(target=self.start_branch, args=(game_state, action), daemon=True).start()
            # current_player = 2
            #
            # game_state, row = Connect4Game.update_game_state(game_state, action, current_player)
            # if row is None:
            #     continue
            #
            # result = self.minimax(game_state, {'x': action, 'y': row}, self.checking_depth, float('-inf'), float('inf'), False)
            if result > best_result:
                best_result = result
                best_move = action
            print(f'{action=}', f'{result}', f'{best_result=}', f'{best_move=}')
        print()
        # print(board)
        # print(result, picked_move)
        return best_move

    def start_branch(self, board, action):
        current_player = 2

        game_state, row = Connect4Game.update_game_state(board, action, current_player)
        if row is None:
            return float('-inf')

        result = self.minimax(game_state, {'x': action, 'y': row}, self.checking_depth, float('-inf'), float('inf'),
                              False)
        return result

    def minimax(self, board, last_move, depth, alpha, beta, player):
        game_won = Connect4Game.check_for_winners(board, last_move['x'], last_move['y'])
        # print(last_move, f'{game_won=}', f'player={int(player) + 1}', f'player={player}')
        # print(player)
        if depth == 0 or game_won:
            # print('depth 0')
            if game_won and player is True:
                return -1 + 0.1 * (self.checking_depth - depth + 1)
            elif game_won and player is False:
                return 1 - 0.1 * (self.checking_depth - depth + 1)
            else:
                return 0

        if player:
            max_state = float('-inf')
            for action in [0, 1, 2, 3, 4, 5, 6]:
                game_state = {row: board[row].copy() for row in board}
                current_player = int(player) + 1

                game_state, row = Connect4Game.update_game_state(game_state, action, current_player)
                if row is None:
                    continue

                if str(game_state) in self.transposition_tables:
                    state = self.transposition_tables[str(game_state)]
                else:
                    state = self.minimax(game_state, {'x': action, 'y': row}, depth - 1, alpha, beta, False)
                    self.transposition_tables[str(game_state)] = state
                max_state = max([max_state, state])

                alpha = max([alpha, state])
                if beta <= alpha:
                    break

            return max_state

        else:
            min_state = float('+inf')
            for action in [0, 1, 2, 3, 4, 5, 6]:
                game_state = {row: board[row].copy() for row in board}
                current_player = int(player) + 1

                game_state, row = Connect4Game.update_game_state(game_state, action, current_player)
                if row is None:
                    continue

                state = self.minimax(game_state, {'x': action, 'y': row}, depth - 1, alpha, beta, True)
                min_state = min([min_state, state])

                beta = min([beta, state])
                if beta <= alpha:
                    break

            return min_state


if __name__ == '__main__':
    game_ai = Connect4AI()
    print(datetime.now())
    game_ai.predict({0: [0, 0, 0, 0, 0, 0, 0],
 1: [0, 0, 0, 0, 0, 0, 0],
 2: [0, 0, 0, 0, 0, 0, 0],
 3: [2, 0, 0, 0, 0, 0, 0],
 4: [1, 0, 0, 2, 0, 0, 0],
 5: [2, 1, 2, 1, 1, 1, 0],
 6: [2, 2, 1, 1, 1, 2, 0]})
    print(datetime.now())

    exit()

    width, height = 700, 700
    window = pyglet.window.Window(width, height)
    batch = pyglet.graphics.Batch()

    game = Connect4Game(window, batch, log=False, use_ai=True)
    game.create_board()
    game.start_window()
