import pytest
from bitboard import play_move, pos_to_bit, set_bit

# Helper to pre-place stones directly by setting bits

def place_direct(bb_X, bb_O, stones_X=None, stones_O=None):
    stones_X = stones_X or []
    stones_O = stones_O or []
    for r, c in stones_X:
        bb_X |= pos_to_bit(r, c)
    for r, c in stones_O:
        bb_O |= pos_to_bit(r, c)
    return bb_X, bb_O


def test_black_double_three_is_forbidden():
    # Setup a position where placing Black at (10,10) creates two open threes:
    # Horizontal open three: stones at (10,9) and (10,11), empty at (10,8) and (10,12)
    # Vertical open three: stones at (9,10) and (11,10), empty at (8,10) and (12,10)
    bb_X, bb_O = 0, 0
    bb_X, bb_O = place_direct(bb_X, bb_O, stones_X=[(10, 9), (10, 11), (9, 10), (11, 10)])

    # Attempt to play Black at (10,10) should raise due to double three
    with pytest.raises(ValueError):
        play_move(bb_X, bb_O, 10, 10, 'X')


def test_white_not_forbidden_by_double_three():
    # Same setup but White plays the central move; rule applies only to Black
    bb_X, bb_O = 0, 0
    bb_X, bb_O = place_direct(bb_X, bb_O, stones_X=[(10, 9), (10, 11), (9, 10), (11, 10)])

    bb_X_new, bb_O_new = play_move(bb_X, bb_O, 10, 10, 'O')
    assert bb_O_new & pos_to_bit(10, 10) != 0
