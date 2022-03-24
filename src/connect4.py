import pyglet
from pyglet import shapes
from pyglet.window import mouse

from itertools import groupby
from random import randint
from datetime import datetime
from threading import Thread

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
        self.game_state, current_row = Connect4Game.update_game_state(self.game_state,
                                                                      self.picked_column,
                                                                      self.current_player)

        print(self.picked_column, current_row)
        if current_row is not None:
            player_color = self.player_colors[self.current_player]
            self.draw_circle(self.picked_column, self.game_height - current_row - 1, player_color)
            self.current_player = self.players[self.current_player % len(self.players)]
        else:
            print('End of column')
            return

        if self.log:
            pprint(self.game_state)

        self.game_won = self.check_for_winners(self.game_state, self.picked_column, current_row)

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
        # elif self.use_ai:
        #     game_ai = Connect4AI()
        #     self.picked_column = game_ai.predict(self.game_state)
        #     self.move()

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
        self.player_number = 2
        self.current_player = 2
        self.game_state = []
        self.game_tree = {i: [] for i in range(8)}
        self.checking_layer = 0
        self.found_winning = False

    def predict(self, board):
        self.game_state = {row: board[row].copy() for row in board}
        state = {
            'state': board,
            'actions': [],
            'winnings': {'won': False,
                         'lost': False}
        }
        self.game_tree[self.checking_layer].append(state)
        self.check_layer()
        # self.check_layer()
        # print(datetime.now())
        # self.check_layer()
        # print(datetime.now())
        # self.check_layer()
        # print(datetime.now())
        # self.check_layer()
        # print(datetime.now())
        # self.check_layer()
        # print(datetime.now())
        # self.check_layer()
        # print(datetime.now())

        return randint(0, 6)

    def check_layer(self):
        boards = self.game_tree[self.checking_layer]
        self.checking_layer += 1
        for board in boards:
            self.generate_possible_moves(board)
        self.current_player = int(not bool(self.current_player - 1)) + 1

    def generate_possible_moves(self, board):
        actions = [0, 1, 2, 3, 4, 5, 6]
        for action in actions:
            game_state = {row: board['state'][row].copy() for row in board['state']}
            past_actions = board['actions'].copy()
            for i in range(len(game_state) - 1, -1, -1):
                if game_state[i][action] == 0:
                    game_state[i][action] = self.current_player

                    was_won = Connect4Game.check_for_winners(game_state, action, i)
                    past_actions.append((action, self.current_player))
                    state = {
                        'state': game_state,
                        'actions': past_actions,
                        'winnings': {'won': was_won if self.current_player == self.player_number else False,
                                     'lost': was_won if self.current_player != self.player_number else False}
                    }
                    self.game_tree[self.checking_layer].append(state)
                    break


if __name__ == '__main__':
    game_ai = Connect4AI()
    game_ai.predict({0: [0, 0, 0, 0, 0, 0, 0],
                     1: [0, 0, 0, 0, 0, 0, 0],
                     2: [0, 0, 0, 0, 0, 0, 0],
                     3: [0, 0, 0, 0, 0, 0, 0],
                     4: [0, 0, 0, 2, 0, 0, 0],
                     5: [0, 0, 0, 1, 1, 1, 0],
                     6: [0, 2, 1, 1, 2, 0, 0]})
    # pprint(game_ai.game_tree)
    exit()

    width, height = 700, 700
    window = pyglet.window.Window(width, height)
    batch = pyglet.graphics.Batch()

    game = Connect4Game(window, batch, log=False, use_ai=True)
    game.create_board()
    game.start_window()