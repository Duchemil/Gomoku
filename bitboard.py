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

MASK_COLS_0_TO_3 = mask_col[0] | mask_col[1] | mask_col[2] | mask_col[3]
MASK_COLS_0_TO_2 = mask_col[0] | mask_col[1] | mask_col[2]
MASK_COLS_0_TO_1 = mask_col[0] | mask_col[1]
MASK_COLS_15_TO_18 = mask_col[15] | mask_col[16] | mask_col[17] | mask_col[18]
MASK_COLS_16_TO_18 = mask_col[16] | mask_col[17] | mask_col[18]
MASK_COLS_17_TO_18 = mask_col[17] | mask_col[18]

mask_row = []
for r in range(BOARD_SIZE):
    m = 0
    for c in range(BOARD_SIZE):
        m |= (1 << (r * BOARD_SIZE + c))
    mask_row.append(m)

MASK_ROW0 = mask_row[0]
MASK_ROW1 = mask_row[1]
MASK_ROW2 = mask_row[2]
MASK_ROW3 = mask_row[3]
MASK_ROW15 = mask_row[15]
MASK_ROW16 = mask_row[16]
MASK_ROW17 = mask_row[17]
MASK_ROW18 = mask_row[18]

MASK_ROWS_15_TO_18 = MASK_ROW15 | MASK_ROW16 | MASK_ROW17 | MASK_ROW18
MASK_ROWS_16_TO_18 = MASK_ROW16 | MASK_ROW17 | MASK_ROW18
MASK_ROWS_17_TO_18 = MASK_ROW17 | MASK_ROW18

FULL_MASK = (1 << N_CELLS) - 1

MASK_NO_ROW0 = ~MASK_ROW0 & FULL_MASK
MASK_NO_ROW1 = ~MASK_ROW1 & FULL_MASK
MASK_NO_ROW2 = ~MASK_ROW2 & FULL_MASK
MASK_NO_ROW3 = ~MASK_ROW3 & FULL_MASK
MASK_NO_ROW15 = ~MASK_ROW15 & FULL_MASK
MASK_NO_ROW16 = ~MASK_ROW16 & FULL_MASK
MASK_NO_ROW17 = ~MASK_ROW17 & FULL_MASK
MASK_NO_ROW18 = ~MASK_ROW18 & FULL_MASK

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

    print("Open fours:", total)
    return total

def dead_four(bb_self, bb_ops):
    """Count half-open fours: OXXXX. or .XXXXO (edge counts as blocked)."""
    empty = ~(bb_self | bb_ops) & FULL_MASK
    total = 0

    def count_dir(shift, run_mask, before_mask, starts_before_edge, starts_after_edge):
        # Four-run starts (leftmost/topmost of the XXXX segment)
        starts = bb_self & (bb_self >> shift) & (bb_self >> (2 * shift)) & (bb_self >> (3 * shift))
        starts &= run_mask

        # Neighbor states aligned to 'starts'
        before_empty   = ((empty  & before_mask) << shift)
        before_blocked = ((bb_ops & before_mask) << shift) | starts_before_edge
        after_empty    = (empty  >> (4 * shift))
        after_blocked  = (bb_ops >> (4 * shift)) | starts_after_edge

        half_open = starts & ((before_empty & after_blocked) | (before_blocked & after_empty))
        return half_open.bit_count()

    # Horizontal
    total += count_dir(
        SHIFT_RIGHT,
        MASK_NO_COL18 & MASK_NO_COL17 & MASK_NO_COL16,
        MASK_NO_COL18,
        mask_col[0],                # blocked by left edge
        MASK_COLS_15_TO_18,         # blocked by right edge after 4
    )

    # Vertical
    total += count_dir(
        SHIFT_DOWN,
        FULL_MASK,
        FULL_MASK,
        MASK_ROW0,                  # blocked by top edge
        MASK_ROWS_15_TO_18,         # blocked by bottom edge after 4
    )

    # Diagonal down-right
    total += count_dir(
        SHIFT_DOWN_RIGHT,
        MASK_NO_COL18 & MASK_NO_COL17 & MASK_NO_COL16 & MASK_NO_COL15,
        MASK_NO_COL18,
        MASK_ROW0 | mask_col[0],    # blocked by top or left edge
        MASK_ROWS_15_TO_18 | MASK_COLS_15_TO_18,
    )

    # Diagonal down-left
    total += count_dir(
        SHIFT_DOWN_LEFT,
        MASK_NO_COL0 & MASK_NO_COL1 & MASK_NO_COL2 & MASK_NO_COL3,
        MASK_NO_COL0,
        MASK_ROW0 | mask_col[18],   # blocked by top or right edge
        MASK_ROWS_15_TO_18 | MASK_COLS_0_TO_3,
    )

    print("Dead fours:", total)
    return total

def open_three(bb_self, bb_ops):
    """Count open-three patterns (.XXX.) for bb_self against bb_ops."""
    empty = ~(bb_self | bb_ops) & FULL_MASK
    total = 0

    def count_dir(shift, run_mask, before_mask):
        # Starts of XXX runs in this direction (leftmost cell of the run)
        starts = bb_self & (bb_self >> shift) & (bb_self >> (2 * shift))
        starts &= run_mask  # ensure the 3-run itself doesn’t wrap across columns

        # Align empties to the start bit:
        # - before_ok: empty exactly at i - shift  => (empty << shift) aligned to i
        # - after_ok:  empty exactly at i + 3*shift => (empty >> (3*shift)) aligned to i
        before_ok = (empty & before_mask) << shift
        after_ok  = empty >> (3 * shift)

        live3_starts = starts & before_ok & after_ok
        return live3_starts.bit_count()

    # Horizontal
    total += count_dir(
        SHIFT_RIGHT,
        MASK_NO_COL18 & MASK_NO_COL17 & MASK_NO_COL16,  # 3 stones fit to the right
        MASK_NO_COL18,  # before (i - 1) must not come from col 18 wrapping to next row
    )

    # Vertical (no column wrap-around on vertical shifts; run_mask is full board)
    total += count_dir(
        SHIFT_DOWN,
        FULL_MASK,
        FULL_MASK,
    )

    # Diagonal down-right
    total += count_dir(
        SHIFT_DOWN_RIGHT,
        MASK_NO_COL18 & MASK_NO_COL17 & MASK_NO_COL16,
        MASK_NO_COL18,  # avoid wrapping from last column
    )

    # Diagonal down-left
    total += count_dir(
        SHIFT_DOWN_LEFT,
        MASK_NO_COL0 & MASK_NO_COL1 & MASK_NO_COL2,
        MASK_NO_COL0,  # avoid wrapping from first column
    )

    return total

def dead_three(bb_self, bb_ops):
    """Count half-open threes: OXXX. or .XXXO (edge counts as blocked)."""
    empty = ~(bb_self | bb_ops) & FULL_MASK
    total = 0

    def count_dir(shift, run_mask, before_mask, after_mask, starts_before_edge, starts_after_edge):
        # Three-run starts (leftmost/topmost of the XXX segment)
        starts = bb_self & (bb_self >> shift) & (bb_self >> (2 * shift))
        starts &= run_mask

        # Neighbor states aligned to 'starts'
        before_empty   = ((empty  & before_mask) << shift)
        before_blocked = ((bb_ops & before_mask) << shift) | starts_before_edge
        # IMPORTANT: mask before shifting right to avoid cross-row/edge wrap
        after_empty    = ((empty  & after_mask) >> (3 * shift))
        after_blocked  = ((bb_ops & after_mask) >> (3 * shift)) | starts_after_edge

        half_open = starts & ((before_empty & after_blocked) | (before_blocked & after_empty))
        return half_open.bit_count()

    # Horizontal: allow starts at col 16; prevent wrap from cols 0..2 when shifting right by 3
    total += count_dir(
        SHIFT_RIGHT,
        MASK_NO_COL18 & MASK_NO_COL17,                          # 3 stones fit to the right
        MASK_NO_COL18,                                          # no wrap on left-shift
        MASK_NO_COL0 & MASK_NO_COL1 & MASK_NO_COL2,             # prevent right-shift wrap from next row
        mask_col[0],                                            # left edge blocks "before"
        MASK_COLS_16_TO_18,                                     # right edge blocks "after"
    )

    # Vertical: no column wrap needed; right-shift by 3*DOWN never wraps columns
    total += count_dir(
        SHIFT_DOWN,
        FULL_MASK,
        FULL_MASK,
        FULL_MASK,                                              # safe for vertical
        MASK_ROW0,                                              # top edge blocks "before"
        MASK_ROWS_16_TO_18,                                     # bottom edge blocks "after"
    )

    # Diagonal down-right: prevent wrap from left/top when shifting right by 3*(down-right)
    total += count_dir(
        SHIFT_DOWN_RIGHT,
        MASK_NO_COL18 & MASK_NO_COL17,                          # 3 stones fit down-right
        MASK_NO_COL18,                                          # avoid left-shift from last column
        (MASK_NO_COL0 & MASK_NO_COL1 & MASK_NO_COL2             # avoid right-shift wrap from first 3 cols
         & MASK_NO_ROW0 & MASK_NO_ROW1 & MASK_NO_ROW2),         # and first 3 rows
        MASK_ROW0 | mask_col[0],
        MASK_ROWS_16_TO_18 | MASK_COLS_16_TO_18,
    )

    # Diagonal down-left: prevent wrap from right/top when shifting right by 3*(down-left)
    total += count_dir(
        SHIFT_DOWN_LEFT,
        MASK_NO_COL0 & MASK_NO_COL1,                            # 3 stones fit down-left
        MASK_NO_COL0,                                           # avoid left-shift from first column
        (MASK_NO_COL16 & MASK_NO_COL17 & MASK_NO_COL18          # avoid right-shift wrap from last 3 cols
         & MASK_NO_ROW0 & MASK_NO_ROW1 & MASK_NO_ROW2),         # and first 3 rows
        MASK_ROW0 | mask_col[18],
        MASK_ROWS_16_TO_18 | MASK_COLS_0_TO_2,
    )

    return total

# --- Evaluation function --- #
def evaluate_board(bb_X, bb_0):
    """ Evaluation function to calculate the board state. """
    score_X = 0
    score_0 = 0

    if has_five(bb_X):
        print("Five in a row: {'X'}")
        score_X += 100000
    if has_five(bb_0):
        print("Five in a row: {'O'}")
        score_0 += 100000

    # Open fours
    score_X += open_four(bb_X, bb_0) * 15000
    score_0 += open_four(bb_0, bb_X) * 15000

    # Dead fours
    score_X += dead_four(bb_X, bb_0) * 5000
    score_0 += dead_four(bb_0, bb_X) * 5000

    # Double threat detection
    # if ((open_three(bb_X, bb_0) >=2 or (dead_four(bb_X, bb_0) == 2)) or (open_three(bb_X, bb_0) == 1 and dead_four(bb_X, bb_0) == 1)):
    #     score_X += 10000
    # if ((open_three(bb_0, bb_X) >=2 or (dead_four(bb_0, bb_X) == 2)) or (open_three(bb_0, bb_X) == 1 and dead_four(bb_0, bb_X) == 1)):
    #     score_0 += 10000

    if (open_three(bb_X, bb_0) >= 1):
        print("Open three detected for X")
        score_X += open_three(bb_X, bb_0) * 1000

    if (dead_three(bb_X, bb_0) >= 1):
        print("Dead three detected for X")
        score_X += dead_three(bb_X, bb_0) * 1000
    # if (dead_three(bb_0, bb_X) >= 1):
    #     score_0 += open_three(bb_0, bb_X) * 1000

    return score_X - score_0

DIRS = [
    (SHIFT_RIGHT, MASK_NO_COL18 & MASK_NO_COL17 & MASK_NO_COL16),
    (SHIFT_DOWN, FULL_MASK),  # vertical safe
    (SHIFT_DOWN_RIGHT, MASK_NO_COL18 & MASK_NO_COL17 & MASK_NO_COL16),
    (SHIFT_DOWN_LEFT, MASK_NO_COL0 & MASK_NO_COL1 & MASK_NO_COL2),
]

def apply_captures(bb_self, bb_opp, move_bit):
    """Remove captured opponent pairs created by the stone at move_bit."""
    # Forward and backward for each direction
    for shift, run_mask in DIRS:
        # forward
        if move_bit & run_mask & (run_mask >> shift) & (run_mask >> (2*shift)):
            a = move_bit << shift
            b = move_bit << (2*shift)
            c = move_bit << (3*shift)
            if (a & bb_opp) and (b & bb_opp) and (c & bb_self):
                bb_opp ^= (a | b)
        # backward
        if move_bit & run_mask & (run_mask << shift) & (run_mask << (2*shift)):
            a = move_bit >> shift
            b = move_bit >> (2*shift)
            c = move_bit >> (3*shift)
            if (a & bb_opp) and (b & bb_opp) and (c & bb_self):
                bb_opp ^= (a | b)
    return bb_self, bb_opp

# --- Move functions --- #
def play_move(bb_X, bb_0, row, col, player):
    """ Play a move at (row, col) on the bitboard bb. """
    move_bit = pos_to_bit(row, col)
    if (bb_X | bb_0) & move_bit:
        raise ValueError("Cell already occupied")

    if player == 'X':
        bb_self, bb_opp = bb_X | move_bit, bb_0
        bb_self, bb_opp = apply_captures(bb_self, bb_opp, move_bit)
        return bb_self, bb_opp

    bb_self, bb_opp = bb_0 | move_bit, bb_X
    bb_self, bb_opp = apply_captures(bb_self, bb_opp, move_bit)
    return bb_opp, bb_self

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

# --- Main --- #
if __name__ == "__main__":
    bb_X = 0
    bb_O = 0

    # X joue une ligne de 4
    # bb_X, bb_O = play_move(bb_X, bb_O, 7, 2, 'O')
    # bb_X, bb_O = play_move(bb_X, bb_O, 2, 16, 'O')
    # for c in range(0, 2):
    #     bb_X, bb_O = play_move(bb_X, bb_O, 3, c, 'X')
    # for c in range(17, 19):
    #     bb_X, bb_O = play_move(bb_X, bb_O, 2, c, 'X')
    for c in range(15, 18):
        bb_X, bb_O = play_move(bb_X, bb_O, 4, c, 'X')
    # bb_X, bb_O = play_move(bb_X, bb_O, 4, 14, 'O')
    for c in range(15, 19):
        bb_X, bb_O = play_move(bb_X, bb_O, 8, c, 'X')

    # bb_X, bb_O = play_move(bb_X, bb_O, 15, 4, 'O')
    for c in range(16, 19):
        bb_X, bb_O = play_move(bb_X, bb_O, c, 4, 'X')

    bb_X, bb_O = play_move(bb_X, bb_O, 10, 10, 'X')
    bb_X, bb_O = play_move(bb_X, bb_O, 11, 11, 'X')
    bb_X, bb_O = play_move(bb_X, bb_O, 12, 12, 'X')
    bb_X, bb_O = play_move(bb_X, bb_O, 13, 13, 'X')
    # bb_X, bb_O = play_move(bb_X, bb_O, 14, 14, 'O')
    print("Évaluation:", evaluate_board(bb_X, bb_O))

    # X complète la ligne (5)
    # bb_X, bb_O = play_move(bb_X, bb_O, 8, 7, 'O')
    # bb_X, bb_O = play_move(bb_X, bb_O, 8, 12, 'O')
    # bb_X, bb_O = play_move(bb_X, bb_O, 9, 9, 'O')
    print_board(bb_X, bb_O)
    print("Évaluation:", evaluate_board(bb_X, bb_O))

    # --- Test capture application --- #
    print("Avant application des captures:")
    print_board(bb_X, bb_O)

    # Appliquer les captures pour le dernier coup joué par X (ligne de 4)
    bb_X, bb_O = apply_captures(bb_X, bb_O, pos_to_bit(4, 17))

    print("Après application des captures:")
    print_board(bb_X, bb_O)

    print("Évaluation:", evaluate_board(bb_X, bb_O))