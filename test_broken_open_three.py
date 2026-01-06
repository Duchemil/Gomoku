import pytest
from bitboard import open_three, pos_to_bit


def place_direct(bb_X, bb_O, stones_X=None, stones_O=None):
    stones_X = stones_X or []
    stones_O = stones_O or []
    for r, c in stones_X:
        bb_X |= pos_to_bit(r, c)
    for r, c in stones_O:
        bb_O |= pos_to_bit(r, c)
    return bb_X, bb_O


def test_open_three_broken_horizontal_xx_x():
    # Pattern .XX.X. at row 10 columns 5..10 -> stones at 6,7,9; ends empty
    bb_X, bb_O = place_direct(0, 0, stones_X=[(10,6), (10,7), (10,9)])
    assert open_three(bb_X, bb_O) >= 1


def test_open_three_broken_horizontal_x_xx():
    # Pattern .X.XX. at row 8 columns 3..8 -> stones at 4,6,7; ends empty
    bb_X, bb_O = place_direct(0, 0, stones_X=[(8,4), (8,6), (8,7)])
    assert open_three(bb_X, bb_O) >= 1


def test_open_three_broken_diagonal_dr():
    # Diagonal down-right .XX.X. anchored around (5,5)..(10,10)
    # Place at (6,6), (7,7), (9,9)
    bb_X, bb_O = place_direct(0, 0, stones_X=[(6,6), (7,7), (9,9)])
    assert open_three(bb_X, bb_O) >= 1
