import multiprocessing
from random import choice
from time import perf_counter, sleep
import numpy as np


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
    print(board)
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
