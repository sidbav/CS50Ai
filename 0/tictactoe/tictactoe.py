"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    num_X = 0
    num_O = 0
    for row in board:
        for elem in row:
            if (elem == X):
                num_X += 1
            if (elem == O):
                num_O += 1

    if (num_O == num_X):
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    res = set()
    for i in range(3):
        for j in range(3):
            if (board[i][j] == EMPTY):
                res.add((i, j))
    return res


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i = action[0]
    j = action[1]

    if (board[i][j] == X or board[i][j] == O):
        raise ValueError

    res = copy.deepcopy(board)
    res[i][j] = player(board)
    return res


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check if there is a winner in the rows
    for row in board:
        if (row[0] == row[1] and row[1] == row[2]):
            return row[0]

    # Check if there is a winner in the columns
    for j in range(3):
        if (board[0][j] == board[1][j] and board[2][j] == board[1][j]):
            return board[0][j]

    # Check there is a winner in the diagonals
    if (board[0][0] == board[1][1] and board[1][1] == board[2][2]):
        return board[0][0]
    if (board[0][2] == board[1][1] and board[1][1] == board[2][0]):
        return board[1][1]

    # If none of the above return, return None
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # First check if there is a winner
    if (winner(board) is not None):
        return True

    # If there is no winner, check if there are any remaining empty squares
    for row in board:
        for elem in row:
            if (elem == EMPTY):
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if (win == X):
        return 1
    if (win == O):
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if (terminal(board)):
        return None
    acts = actions(board)
    turn = player(board)
    if (turn == X):
        val, action = max_value(board)
        return action
    else:
        val, action = min_value(board)
        return action


def max_value(board):
    """
    Returns a pair the value, and action which results in the max value, which
    would result in an X win
    """
    if terminal(board):
        return utility(board), None
    # in this case can be any value less than -1
    value = -500
    opt_action = None
    for action in actions(board):
        res = result(board, action)
        val, act = min_value(res)
        if (val > value):
            value = val
            opt_action = action
            # If we already have a value that results in 1, no need to look
            # at the rest
            if value == 1:
                return value, opt_action
    return value, opt_action

def min_value(board):
    """
    Returns a pair the value, and action which results in the min value, which
    would result in a O win
    """
    if terminal(board):
        return utility(board), None
    # in this case can be any value greater than 1
    value = 500
    opt_action = None
    for action in actions(board):
        res = result(board, action)
        val, act = max_value(res)
        if (val < value):
            value = val
            opt_action = action
            # If we already have a value that results in -1, no need to look
            # at the rest
            if value == -1:
                return value, opt_action
    return value, opt_action

