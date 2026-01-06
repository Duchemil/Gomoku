import pytest
from bitboard import play_move, pos_to_bit

# Helpers

def place_direct(bb_X, bb_O, stones_X=None, stones_O=None):
    stones_X = stones_X or []
    stones_O = stones_O or []
    for r, c in stones_X:
        bb_X |= pos_to_bit(r, c)
    for r, c in stones_O:
        bb_O |= pos_to_bit(r, c)
    return bb_X, bb_O


def test_black_double_three_center_horizontal_vertical():
    # Horizontal and vertical forks centered at (10,10)
    bb_X, bb_O = place_direct(0, 0, stones_X=[(10, 9), (10, 11), (9, 10), (11, 10)])
    with pytest.raises(ValueError):
        play_move(bb_X, bb_O, 10, 10, 'X')


def test_black_double_three_horizontal_diagonal_dr():
    # Horizontal and diagonal down-right forks centered at (10,10)
    bb_X, bb_O = place_direct(0, 0, stones_X=[(10, 9), (10, 11), (9, 9), (11, 11)])
    with pytest.raises(ValueError):
        play_move(bb_X, bb_O, 10, 10, 'X')


def test_black_double_three_near_edge_still_detected():
    # Near top edge but with both ends in-bounds and empty for both lines
    # Center at (2,10): horizontal (2,9),(2,11) and vertical (1,10),(3,10)
    bb_X, bb_O = place_direct(0, 0, stones_X=[(2, 9), (2, 11), (1, 10), (3, 10)])
    with pytest.raises(ValueError):
        play_move(bb_X, bb_O, 2, 10, 'X')


def test_white_not_forbidden_by_double_three():
    bb_X, bb_O = place_direct(0, 0, stones_X=[(10, 9), (10, 11), (9, 10), (11, 10)])
    bb_X_new, bb_O_new = play_move(bb_X, bb_O, 10, 10, 'O')
    assert bb_O_new & pos_to_bit(10, 10)


def test_occupied_cell_is_illegal():
    bb_X, bb_O = place_direct(0, 0, stones_X=[(10, 10)])
    with pytest.raises(ValueError):
        play_move(bb_X, bb_O, 10, 10, 'X')


def test_black_double_three_broken_both_directions():
    # Playing at (10,10) creates two broken open threes:
    # Horizontal .XX.X.: stones at (10,9) and (10,12), gap at (10,11), open ends at (10,8),(10,13)
    # Vertical   .X.XX.: stones at (12,10) and (13,10), gap at (11,10), open ends at (9,10),(14,10)
    bb_X, bb_O = place_direct(0, 0, stones_X=[(10, 9), (10, 12), (12, 10), (13, 10)])
    with pytest.raises(ValueError):
        play_move(bb_X, bb_O, 10, 10, 'X')
