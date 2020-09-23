from collections import Counter

# Board matrix
board = [
    [None, None, None],
    [None, None, None],
    [None, None, None]
]
# Moves availables
board_moves = {
    'a1': [0,0],
    'a2': [0,1],
    'a3': [0,2],
    'b1': [1,0],
    'b2': [1,1],
    'b3': [1,2],
    'c1': [2,0],
    'c2': [2,1],
    'c3': [2,2]
}
# Winner combinations
winner_lines = {
    'r1': ['a1', 'a2', 'a3'],
    'r2': ['b1', 'b2', 'b3'],
    'r3': ['c1', 'c2', 'c3'],
    'c1': ['a1', 'b1', 'c1'],
    'c2': ['a2', 'b2', 'c2'],
    'c3': ['a3', 'b3', 'c3'],
    'd1': ['a1', 'b2', 'c3'],
    'd2': ['a3', 'b2', 'c1'],
}

def get_board():
    current_board = {}
    # Get rows
    for r in range(0,3):
        current_board['r'+str(r+1)] = board[r]
    # Get cols
    for c in range(0,3):
        current_board['c'+str(c+1)] = [board[0][c], board[1][c], board[2][c]]
    # Get diagonals
    diagonal_1 = []
    diagonal_2 = []
    diag_items = [2,1,0]
    for n in range(0,3):
        diagonal_1.append(board[n][n])
        diagonal_2.append(board[n][diag_items[n]])
    current_board['d1'] = diagonal_1
    current_board['d2'] = diagonal_2
    return current_board


def play(r, c, p):
    global board
    # Check if move selected is empty
    if board[r][c] is None:
        board[r][c] = p
        return True
    else:
        return False


def check_win():
    current_board = get_board()
    for k, v in current_board.items():
        if (v[0] == v[1] == v[2]) and v[0] is not None:
            return k
    else:
        return False


def select_computer_move(current_board):
    # Try to win
    for k, v in current_board.items():
        count = Counter(v)
        if count.get(None):
            if count['o'] == 2:
                return k
    # Prevent oponent win
    for k, v in current_board.items():
        count = Counter(v)
        if count.get(None):
            if count['x'] == 2:
                return k
    # Check if there is a line where I could win
    for k, v in current_board.items():
        count = Counter(v)
        if count.get(None):
            if (count['o'] == 1 and count[None] == 2) or count[None] == 3:
                return k
    # Movement by default
    for k, v in current_board.items():
        count = Counter(v)
        if count.get(None):
            return k


def computer_play():
    current_board = get_board()
    computer_move = select_computer_move(current_board)
    i = current_board[computer_move].index(None)
    move = winner_lines[computer_move][i]
    selection = board_moves.get(move)
    good = play(*selection, 'o')
    if good:
        return 'OK'
    else:
        return 'NOT_POSSIBLE'


def user_play():
    s = input('Insert your option: ')
    user_selection = board_moves.get(s)
    if user_selection:
        good = play(*user_selection, 'x')
        if good:
            return 'OK'
        else:
            return 'NOT_POSSIBLE'
    else:
        return 'INVALID'


def start_game():
    # When turn = True plays USER, when turn = False plays COMPUTER
    turn = True
    winner = False
    end = False
    movements = 0
    print('To play insert row (a,b,c) and col (1,2,3) like b1, a2, c0...\n')
    while winner == False and end == False:
        if turn:
            move = user_play()
        else:
            move = computer_play()

        if move == 'INVALID':
            print('Please, insert a valid option.')
        if move == 'NOT_POSSIBLE':
            print('That move is not possible. Please, select another option.')
        if move == 'OK':
            movements += 1
            turn = not turn
            # Print matrix to the user
            print('------------------------')
            for b in board:
                print(b)
            print('------------------------')
            print('\n')

            if movements >= 5:
                somebody_win = check_win()
                print(somebody_win)
                if somebody_win:
                    if turn:
                        print('You win: ', somebody_win)
                    else:
                        print('I win: ', somebody_win)
                    winner = True
                else:
                    if movements == 9:
                        print('Nobody wins')
                        end = True


def main():
    start_game()


if __name__ == "__main__":
    main()