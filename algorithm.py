from bitboard import evaluate_board, play_move, undo_move, pos_to_bit, N_CELLS

def min_max(bb_X, bb_0, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or game_over(bb_X, bb_0):
        return evaluate_board(bb_X, bb_0), None

    if maximizingPlayer:
        maxEval = float('-inf')
        for child in get_all_possible_moves(bb_X, bb_0):
            eval = min_max(child, depth - 1, alpha, beta, False)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = float('inf')
        for child in get_all_possible_moves(position):
            eval = min_max(child, depth - 1, alpha, beta, True)
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return minEval

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