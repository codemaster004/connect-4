import multiprocessing
from random import choice
from time import perf_counter, sleep
import numpy as np
import requests


def bools():
    game_won = False
    player = True
    print(1 if game_won and player else -1 if game_won and not player else 0)

    game_won = False
    player = False
    print(1 if game_won and player else -1 if game_won and not player else 0)

    game_won = True
    player = True
    print(1 if game_won and player else -1 if game_won and not player else 0)

    game_won = True
    player = False
    print(1 if game_won and player else -1 if game_won and not player else 0)

    last_move = 3
    moves = [0, 1, 2, 3, 4, 5, 6]
    moves.sort(key=lambda x: pow(last_move - x, 2))
    print(moves)


def take_time():
    # sleep(0.1)
    pass


def np_board():
    """
    Board example
    # 0  1  2  3  4  5  6
    [ 6 13 20 27 34 41 48
      5 12 19 26 33 40 47
      4 11 18 25 32 39 46
      3 10 17 24 31 38 45
      2  9 16 23 30 37 44
      1  8 15 22 29 36 43
      0  7 14 21 28 35 42]
    """
    # board = np.zeros((7, 7), dtype=np.int16)
    # board[6][1] = 1
    # board[5][1] = 1
    # board[6][2] = 1
    # print(board.take(1, axis=1))

    a = 7
    b = 7
    board = np.zeros(a * b, dtype=np.int16)

    # input: X, Y
    x = 1
    y = 0
    board[b * x + y] = 1
    board[b * 1 + 1] = 1
    board[b * 2 + 0] = 1
    board[b * 0 + 2] = 2
    board[b * 1 + 3] = 2
    # board[b * 2 + 4] = 2
    board[b * 3 + 5] = 2
    board[b * 4 + 6] = 2
    """
    Board example
    # 0  1  2  3  4  5  6
    [ 6 13 20 27 34 41 48
      5 12 19 26 33 40 47
      4 11 18 25 32 39 46
      3 10 17 24 31 38 45
      2  9 16 23 30 37 44
      1  8 15 22 29 36 43
      0  7 14 21 28 35 42]
      
    [ 0  0  0  0  2  0  0
      0  0  0  2  0  0  0
      0  0  2  0  0  0  0
      0  2  0  0  0  0  0
      0  0  0  0  0  0  0
      0  1  0  0  0  0  0
      0  1  1  0  0  0  0]
    """

    # Diagonal /
    # n = 22
    # print(board)
    m = board & np.roll(board, 8)
    if np.any(m & np.roll(m, 16)):
        print('Found 4')
    # print(board)
    # print(board[n % 8::8])

    # Diagonal \
    # n = 26
    # limit = b * (n % 6) + 1
    # print(board[n:limit:6])
    # print(board[n % 6:n:6])


game_state = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [2, 1, 0, 0, 0, 0, 0],
    [1, 1, 1, 2, 1, 2, 0],
    [2, 1, 2, 0, 0, 0, 0],
    [2, 2, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0]
]

top_row = len(game_state[0]) - 1
end_col = len(game_state) - 1


def is_winning(col, row, val):
    # print(f'{v_max=} {v_min=}')

    # print('diagonal /', max_main(col, row, val) - min_main(col, row, val) + 1)
    v_max = max_main(col, row, val)
    v_min = min_main(col, row, val)
    if v_max - v_min + 1 >= 4:
        print('Diagonal /')
        return True

    # print('diagonal \ ', max_anti(col, row, val) - min_anti(col, row, val) + 1)
    v_max = max_anti(col, row, val)
    v_min = min_anti(col, row, val)
    print(f'{v_max=} {v_min=}')
    if v_max - v_min + 1 >= 4:
        print('Diagonal \\')
        return True

    # print('horizontal', max_row(col, row, val) - min_row(col, row, val))
    v_max = max_row(col, row, val)
    v_min = min_row(col, row, val)
    if v_max - v_min + 1 >= 4:
        print('Horizontal')
        return True

    # print('vertical', max_col(col, row, val) - min_col(col, row, val))
    v_max = max_col(col, row, val)
    v_min = min_col(col, row, val)
    if v_max - v_min + 1 >= 4:
        print('Vertical')
        return True

    return False


def max_col(col, row, val):
    if row == top_row:
        return row

    for i in range(row + 1, top_row + 1):
        if game_state[col][i] != val:
            return i - 1

    return top_row


def min_col(col, row, val):
    if row == 0:
        return row

    for i in range(row - 1, -1, -1):
        if game_state[col][i] != val:
            return i + 1

    return 0


def max_row(col, row, val):
    if col == end_col:
        return col

    for i in range(col + 1, end_col + 1):
        if game_state[i][row] != val:
            return i - 1

    return end_col


def min_row(col, row, val):
    if col == 0:
        return col

    for i in range(col - 1, -1, -1):
        if game_state[i][row] != val:
            return i + 1

    return 0


def max_main(col, row, val):
    if col == end_col or row == top_row:
        return col

    for i in range(1, min([end_col - col, top_row - row]) + 1):
        if game_state[col + i][row + i] != val:
            return col + i - 1

    return col + min([end_col - col, top_row - row])


def min_main(col, row, val):
    if col == 0 or row == 0:
        return col

    for i in range(1, min([col, row]) + 1):
        if game_state[col - i][row - i] != val:
            return col - i + 1

    return col - min([col, row])


def max_anti(col, row, val):
    if col == end_col or row == top_row:
        return col

    for i in range(1, min([end_col - col, row]) + 1):
        if game_state[col + i][row - i] != val:
            return col + i - 1

    return col + min([end_col - col, row])


def min_anti(col, row, val):
    if col == 0 or row == 0:
        return col

    for i in range(1, min([col, top_row - row]) + 1):
        if game_state[col - i][row + i] != val:
            return col - i + 1

    return col - min([col, top_row - row])


if __name__ == '__main__':
    np_board()

    # start = perf_counter()
    # for i in range(3):
    #     process1 = multiprocessing.Process(target=take_time)
    #     # process2 = multiprocessing.Process(target=take_time)
    #     process1.start()
    #     # process2.start()
    #     process1.join()
    #     # process2.join()
    # end = perf_counter()

    # print('Execute time:', end - start)
    my_dict = {}
    my_dict.update({'hello': 'world'})

    # r = requests.post('http://127.0.0.1:5000/check_win', json={'board': {}, 'last_move': {'x': 0, 'y': 0}})
    # print(r.text)
    print(is_winning(col=4, row=2, val=2))
