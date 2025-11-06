BOARD_SIZE = 19
N_CELLS = BOARD_SIZE * BOARD_SIZE

SHIFT_RIGHT = 1
SHIFT_DOWN = BOARD_SIZE
SHIFT_DOWN_RIGHT = BOARD_SIZE + 1
SHIFT_DOWN_LEFT = BOARD_SIZE - 1

# Column masks for a 19x19 board to aid wrap-around in bitboard
mask_col = []
for c in range(BOARD_SIZE):
    m = 0
    for r in range(BOARD_SIZE):
        idx = r * BOARD_SIZE + c
        m |= (1 << idx)
    mask_col.append(m)

MASK_NO_COL0 = ~mask_col[0] & ((1 << N_CELLS) - 1)
MASK_NO_COL1 = ~mask_col[1] & ((1 << N_CELLS) - 1)
MASK_NO_COL2 = ~mask_col[2] & ((1 << N_CELLS) - 1)
MASK_NO_COL3 = ~mask_col[3] & ((1 << N_CELLS) - 1)
MASK_NO_COL15 = ~mask_col[15] & ((1 << N_CELLS) - 1)
MASK_NO_COL16 = ~mask_col[16] & ((1 << N_CELLS) - 1)
MASK_NO_COL17 = ~mask_col[17] & ((1 << N_CELLS) - 1)
MASK_NO_COL18 = ~mask_col[18] & ((1 << N_CELLS) - 1)

# --- Bitboard helper functions --- #
def pos_to_bit(row, col):
    """ Convert (row, col) to bitboard position. """
    return 1 << (row * BOARD_SIZE + col)

def set_bit(bb, row, col):
    """ Set the bit at (row, col) in the bitboard bb. """
    return bb | pos_to_bit(row, col)

def clear_bit(bb, row, col):
    """ Clear the bit at (row, col) in the bitboard bb. """
    return bb & ~pos_to_bit(row, col)

def get_bit(bb, row, col):
    """ Get the bit at (row, col) in the bitboard bb. """
    return (bb >> (row * BOARD_SIZE + col)) & 1

def in_bounds(row, col):
    """ Check if (row, col) is within board bounds. """
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

# --- Shapes detection --- #
def has_five(bb):
    """ Check if there are five in a row in any direction. """
    # Horizontal
    m = bb & (bb >> SHIFT_RIGHT) & (bb >> (2 * SHIFT_RIGHT)) & (bb >> (3 * SHIFT_RIGHT)) & (bb >> (4 * SHIFT_RIGHT))
    m &= MASK_NO_COL18 & MASK_NO_COL17 & MASK_NO_COL16 & MASK_NO_COL15
    if m != 0:
        return True
    
    # Vertical
    m = bb & (bb >> SHIFT_DOWN) & (bb >> (2 * SHIFT_DOWN)) & (bb >> (3 * SHIFT_DOWN)) & (bb >> (4 * SHIFT_DOWN))
    if m != 0:
        return True
    
    # Diagonal down-right
    m = bb & (bb >> SHIFT_DOWN_RIGHT) & (bb >> (2 * SHIFT_DOWN_RIGHT)) & (bb >> (3 * SHIFT_DOWN_RIGHT)) & (bb >> (4 * SHIFT_DOWN_RIGHT))
    m &= MASK_NO_COL18 & MASK_NO_COL17 & MASK_NO_COL16 & MASK_NO_COL15
    if m != 0:
        return True
    
    # Diagonal down-left
    m = bb & (bb >> SHIFT_DOWN_LEFT) & (bb >> (2 * SHIFT_DOWN_LEFT)) & (bb >> (3 * SHIFT_DOWN_LEFT)) & (bb >> (4 * SHIFT_DOWN_LEFT))
    m &= MASK_NO_COL0 & MASK_NO_COL1 & MASK_NO_COL2 & MASK_NO_COL3
    if m != 0:
        return True
    
    return False

def open_four(bb_self, bb_ops):
    """Count open-four patterns (.XXXX.) for bb_self against bb_ops."""
    empty = ~(bb_self | bb_ops) & ((1 << N_CELLS) - 1)
    total = 0

    def count_dir(shift, run_mask, before_mask):
        # Starts of XXXX runs in this direction (leftmost cell of the run)
        starts = bb_self & (bb_self >> shift) & (bb_self >> (2 * shift)) & (bb_self >> (3 * shift))
        starts &= run_mask  # ensure the 4-run itself doesn’t wrap across columns

        # Align empties to the start bit:
        # - before_ok: empty exactly at i - shift  => (empty << shift) aligned to i
        # - after_ok:  empty exactly at i + 4*shift => (empty >> (4*shift)) aligned to i
        before_ok = (empty & before_mask) << shift
        after_ok  = empty >> (4 * shift)

        live4_starts = starts & before_ok & after_ok
        return live4_starts.bit_count()

    # Horizontal
    total += count_dir(
        SHIFT_RIGHT,
        MASK_NO_COL18 & MASK_NO_COL17 & MASK_NO_COL16 & MASK_NO_COL15,  # 4 stones fit to the right
        MASK_NO_COL18,  # before (i - 1) must not come from col 18 wrapping to next row
    )

    # Vertical (no column wrap-around on vertical shifts; run_mask is full board)
    total += count_dir(
        SHIFT_DOWN,
        (1 << N_CELLS) - 1,
        (1 << N_CELLS) - 1,
    )

    # Diagonal down-right
    total += count_dir(
        SHIFT_DOWN_RIGHT,
        MASK_NO_COL18 & MASK_NO_COL17 & MASK_NO_COL16 & MASK_NO_COL15,
        MASK_NO_COL18,  # avoid wrapping from last column
    )

    # Diagonal down-left
    total += count_dir(
        SHIFT_DOWN_LEFT,
        MASK_NO_COL0 & MASK_NO_COL1 & MASK_NO_COL2 & MASK_NO_COL3,
        MASK_NO_COL0,  # avoid wrapping from first column
    )

    return total

# --- Evaluation function --- #
def evaluate_board(bb_X, bb_0):
    """ Evaluation function to calculate the board state, the higher the score, the better the position. """
    score_X = 0
    score_0 = 0

    # if has_five(bb_X):
    #     score_X += 100000
    # if has_five(bb_0):
    #     score_0 += 100000

    score_X += open_four(bb_X, bb_0) * 1000
    score_0 += open_four(bb_0, bb_X) * 1000

    return score_X - score_0

# --- Move functions --- #
def play_move(bb_X, bb_0, row, col, player):
    """ Play a move at (row, col) on the bitboard bb. """
    if player == 'X':
        bb_X = set_bit(bb_X, row, col)
    else:
        bb_0 = set_bit(bb_0, row, col)
    return bb_X, bb_0

def undo_move(bb_X, bb_0, row, col, player):
    """ Undo a move at (row, col) on the bitboard bb. """
    if player == 'X':
        bb_X = clear_bit(bb_X, row, col)
    else:
        bb_0 = clear_bit(bb_0, row, col)
    return bb_X, bb_0

# --- Debugging function --- #
def print_board(bb_X, bb_0):
    """ Print the board for debugging purposes. """
    for r in range(BOARD_SIZE):
        row_str = ""
        for c in range(BOARD_SIZE):
            if get_bit(bb_X, r, c):
                row_str += "X "
            elif get_bit(bb_0, r, c):
                row_str += "O "
            else:
                row_str += ". "
        print(row_str)
    print()

# --- Exemple d'utilisation ---
if __name__ == "__main__":
    bb_X = 0
    bb_O = 0

    # X joue une ligne de 4
    bb_X, bb_O = play_move(bb_X, bb_O, 7, 2, 'O')
    bb_X, bb_O = play_move(bb_X, bb_O, 2, 16, 'O')
    for c in range(0, 2):
        bb_X, bb_O = play_move(bb_X, bb_O, 3, c, 'X')
    for c in range(15, 19):
        bb_X, bb_O = play_move(bb_X, bb_O, 2, c, 'X')

    for c in range(8, 12):
        bb_X, bb_O = play_move(bb_X, bb_O, 8, c, 'X')

    print_board(bb_X, bb_O)
    print("Évaluation:", evaluate_board(bb_X, bb_O))

    # X complète la ligne (5)
    bb_X, bb_O = play_move(bb_X, bb_O, 8, 7, 'O')
    print_board(bb_X, bb_O)
    print("Évaluation:", evaluate_board(bb_X, bb_O))