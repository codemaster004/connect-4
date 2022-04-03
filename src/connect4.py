import pyglet
from pyglet import shapes
from pyglet.window import mouse

from itertools import groupby
from time import perf_counter
from threading import Thread
from multiprocessing import Process, Manager
from pprint import pprint


class Connect4Game:
    def __init__(self, window_obj, batch_obj, width, height, log=False, use_ai=True):
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

        self.game_width = width
        self.game_height = height
        self.game_state = [[0 for j in range(self.game_height)] for i in range(self.game_width)]

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
            self.draw_circle(self.picked_column, self.current_row, player_color)
            self.current_player = self.players[self.current_player % len(self.players)]
        else:
            # print('End of column')
            return

        pprint(self.game_state)
        print(self.picked_column, self.current_row)
        print(f'{self.picked_column=}')
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
            game_state = [col.copy() for col in self.game_state]
            # start = perf_counter()
            self.picked_column = game_ai.predict(game_state)
            # end = perf_counter()
            # print('Execution time:', end - start, 's')

            if self.picked_column is None:
                self.move()

                if self.game_won:
                    self.winner_screen()

    @staticmethod
    def update_game_state(game_state, column, player):
        for i in range(len(game_state[0])):
            if game_state[column][i] == 0:
                game_state[column][i] = player
                return game_state, i

        return game_state, None

    @classmethod
    def check_for_winners(cls, game_state, new_x, new_y):
        value = game_state[new_x][new_y]
        if value == 0:
            return False

        # /
        if cls.max_main(game_state, new_x, new_y, value) - cls.min_main(game_state, new_x, new_y, value) + 1 >= 4:
            return True

        # \
        if cls.max_anti(game_state, new_x, new_y, value) - cls.min_anti(game_state, new_x, new_y, value) + 1 >= 4:
            return True

        # -
        if cls.max_row(game_state, new_x, new_y, value) - cls.min_row(game_state, new_x, new_y, value) + 1 >= 4:
            return True

        # |
        if cls.max_col(game_state, new_x, new_y, value) - cls.min_col(game_state, new_x, new_y, value) + 1 >= 4:
            return True

        return False

    @classmethod
    def max_col(cls, game_state, col, row, val):
        top_row = len(game_state[0]) - 1

        if row == top_row:
            return row

        for i in range(row + 1, top_row + 1):
            if game_state[col][i] != val:
                return i - 1

        return top_row

    @classmethod
    def min_col(cls, game_state, col, row, val):
        if row == 0:
            return row

        for i in range(row - 1, -1, -1):
            if game_state[col][i] != val:
                return i + 1

        return 0

    @classmethod
    def max_row(cls, game_state, col, row, val):
        end_col = len(game_state) - 1

        if col == end_col:
            return col

        for i in range(col + 1, end_col + 1):
            if game_state[i][row] != val:
                return i - 1

        return end_col

    @classmethod
    def min_row(cls, game_state, col, row, val):
        if col == 0:
            return col

        for i in range(col, -1, -1):
            if game_state[i][row] != val:
                return i + 1

        return 0

    @classmethod
    def max_main(cls, game_state, col, row, val):
        top_row = len(game_state[0]) - 1
        end_col = len(game_state) - 1

        if col == end_col or row == top_row:
            return col

        for i in range(1, min([end_col - col, top_row - row]) + 1):
            if game_state[col + i][row + i] != val:
                return col + i - 1

        return col + min([end_col - col, top_row - row])

    @classmethod
    def min_main(cls, game_state, col, row, val):
        if col == 0 or row == 0:
            return col

        for i in range(1, min([col, row]) + 1):
            if game_state[col - i][row - i] != val:
                return col - i + 1

        return col - min([col, row])

    @classmethod
    def max_anti(cls, game_state, col, row, val):
        top_row = len(game_state[0]) - 1
        end_col = len(game_state) - 1

        if col == end_col or row == top_row:
            return col

        for i in range(1, min([end_col - col, row]) + 1):
            if game_state[col + i][row - i] != val:
                return col + i - 1

        return col + min([end_col - col, row])

    @classmethod
    def min_anti(cls, game_state, col, row, val):
        top_row = len(game_state[0]) - 1

        if col == 0 or row == 0:
            return col

        for i in range(1, min([col, top_row - row]) + 1):
            if game_state[col - i][row + i] != val:
                return col - i + 1

        return col - min([col, top_row - row])

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
        self.game_state = [[0 for j in range(self.game_height)] for i in range(self.game_width)]
        self.game_won = False
        self.current_row = None
        self.picked_column = None
        self.current_player = 1

        self.rectangles = []
        self.circles = []

        self.create_board()


class Connect4AI:
    def __init__(self):
        self.checking_depth = 8
        self.current_player = 2
        self.transposition_tables = {}
        self.winning_moves = {}

    def predict(self, board):
        with Manager() as manager:
            results = manager.list()
            winning_moves = manager.dict()
            # results = []
            # winning_moves = {}

            processes = []
            for action in [3, 2, 1, 4, 5, 0, 6]:
                processes.append(Thread(target=self.start_branch, args=(board, action, results, winning_moves)))
                # self.start_branch(board, action, results, winning_moves)
            for proces in processes:
                proces.start()
            for proces in processes:
                proces.join()

            results = sorted(list(results), key=lambda x: x[0], reverse=True)
            pprint(dict(winning_moves))
            print(results)

            if len(results) == 0:
                return

            best_move = results[0][1]
            best_win_lost_count = 0
            bets_result = results[0][0]
            for result in results:
                if result[0] == bets_result and result[1] in winning_moves:
                    data = winning_moves[result[1]]
                    if 'wins' not in data or 'worst_lost' not in data or 'lost' not in data or 'best_winning' not in data:
                        continue
                    win_lost_count = (data['wins'] * data['worst_lost']) / (data['lost'] * data['best_winning'])
                    if win_lost_count > best_win_lost_count:
                        best_win_lost_count = win_lost_count
                        best_move = result[1]

            # print(f'{best_move = }')
            return best_move

    def start_branch(self, board, action, results, winning_moves):
        game_state = [col.copy() for col in board]
        self.winning_moves = winning_moves
        current_player = self.current_player

        game_state, row = Connect4Game.update_game_state(game_state, action, current_player)
        if row is None:
            return float('-inf')

        result = self.minimax(game_state, {'x': action, 'y': row}, self.checking_depth, float('-inf'), float('inf'),
                              False, action)
        # print(f'Branch: {action}: ', self.started_boards, self.prunes, self.value_copied, self.calculated_boards)
        winning_moves = self.winning_moves
        results.append((result, action))

    def evaluate_board(self, player, game_won, depth, first_move):
        if game_won and player is True:
            if first_move not in self.winning_moves:
                self.winning_moves[first_move] = {}
            if 'worst_lost' not in self.winning_moves[first_move] \
                    or self.winning_moves[first_move]['worst_lost'] > self.checking_depth - depth:
                win_history = dict(self.winning_moves[first_move])
                win_history['worst_lost'] = self.checking_depth - depth
                win_history['lost'] = win_history.setdefault('lost', 0) + 1
                self.winning_moves[first_move] = win_history

            return -1 + 0.1 * (self.checking_depth - depth)
        elif game_won and player is False:
            if first_move not in self.winning_moves:
                self.winning_moves[first_move] = {}
            if 'best_winning' not in self.winning_moves[first_move] \
                    or self.winning_moves[first_move]['best_winning'] > self.checking_depth - depth:
                win_history = dict(self.winning_moves[first_move])
                win_history['best_winning'] = self.checking_depth - depth
                win_history['wins'] = win_history.setdefault('wins', 0) + 1
                self.winning_moves[first_move] = win_history

            return 1 - 0.1 * (self.checking_depth - depth)
        else:
            return 0

    def minimax(self, board, last_move, depth, alpha, beta, player, first_move):
        game_won = Connect4Game.check_for_winners(board, last_move['x'], last_move['y'])
        if depth == 0 or game_won:
            return self.evaluate_board(player, game_won, depth, first_move)

        if player:
            max_state = float('-inf')
            moves = [0, 1, 2, 3, 4, 5, 6]
            for action in sorted(moves, key=lambda x: pow(last_move['x'] - x, 2)):
                game_state = [col.copy() for col in board]
                current_player = int(player) + 1

                game_state, row = Connect4Game.update_game_state(game_state, action, current_player)
                if row is None:
                    continue

                if str(game_state) in self.transposition_tables:
                    state = self.transposition_tables[str(game_state)]
                else:
                    state = self.minimax(game_state, {'x': action, 'y': row}, depth - 1, alpha, beta, False, first_move)
                    self.transposition_tables[str(game_state)] = state
                max_state = max([max_state, state])

                alpha = max([alpha, state])
                if beta <= alpha:
                    break

            return max_state

        else:
            min_state = float('+inf')
            moves = [0, 1, 2, 3, 4, 5, 6]
            for action in sorted(moves, key=lambda x: pow(last_move['x'] - x, 2)):
                game_state = [col.copy() for col in board]
                current_player = int(player) + 1

                game_state, row = Connect4Game.update_game_state(game_state, action, current_player)
                if row is None:
                    continue

                if str(game_state) in self.transposition_tables:
                    state = self.transposition_tables[str(game_state)]
                else:
                    state = self.minimax(game_state, {'x': action, 'y': row}, depth - 1, alpha, beta, True, first_move)
                    self.transposition_tables[str(game_state)] = state
                min_state = min([min_state, state])

                beta = min([beta, state])
                if beta <= alpha:
                    break

            return min_state


if __name__ == '__main__':
    # game_ai = Connect4AI()
    # game_ai.checking_depth = 10
    # start = perf_counter()
    # game_ai.predict([
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    # ])
    # end = perf_counter()
    # print('Execution time:', end - start, 's')
    #
    # exit()

    width, height = 7, 7
    window = pyglet.window.Window(width * 100, height * 100)
    batch = pyglet.graphics.Batch()

    game = Connect4Game(window, batch, width, height, log=False, use_ai=True)
    game.create_board()
    game.start_window()
