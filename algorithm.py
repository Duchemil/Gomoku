from bitboard import evaluate_board, play_move, undo_move, pos_to_bit, N_CELLS, has_five

def min_max(bb_X, bb_0, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or game_over(bb_X, bb_0):
        return evaluate_board(bb_X, bb_0), None

    if maximizingPlayer:
        maxEval = float('-inf')
        best_move = None
        for child_X, child_0, move in get_all_possible_moves(bb_X, bb_0, True):
            child_eval, _ = min_max(child_X, child_0, depth - 1, alpha, beta, False)
            if child_eval > maxEval:
                maxEval = child_eval
                best_move = move
            alpha = max(alpha, child_eval)
            if beta <= alpha:
                break
        return maxEval, best_move
    else:
        minEval = float('inf')
        for child_X, child_0, move in get_all_possible_moves(bb_X, bb_0, False):
            child_eval, _ = min_max(child_X, child_0, depth - 1, alpha, beta, True)
            if child_eval < minEval:
                minEval = child_eval
                best_move = move
            beta = min(beta, child_eval)
            if beta <= alpha:
                break
        return minEval, best_move

def game_over(bb_X, bb_0):
    return has_five(bb_X) or has_five(bb_0)

def get_legal_moves(bb_X, bb_0):
    occupied = bb_X | bb_0
    moves = []
    for pos in range (N_CELLS):
        if not ((occupied >> pos) & 1):
            row, col = divmod(pos, 19)
            moves.append((row, col))
    return moves

def get_all_possible_moves(bb_X, bb_0, maximizingPlayer=True):
    """Generate child positions for side to move."""
    player = 'X' if maximizingPlayer else 'O'
    children = []
    for (r, c) in get_legal_moves(bb_X, bb_0):
        new_X, new_O = play_move(bb_X, bb_0, r, c, player)
        children.append((new_X, new_O, (r, c)))
    return children