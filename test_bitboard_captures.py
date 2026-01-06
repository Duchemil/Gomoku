import unittest

from bitboard import play_move, pos_to_bit


class CaptureTests(unittest.TestCase):
    def test_horizontal_forward_capture(self):
        bb_X = pos_to_bit(0, 0)
        bb_O = pos_to_bit(0, 1) | pos_to_bit(0, 2)

        bb_X, bb_O = play_move(bb_X, bb_O, 0, 3, 'X')

        self.assertEqual(bb_O & (pos_to_bit(0, 1) | pos_to_bit(0, 2)), 0)
        self.assertTrue(bb_X & pos_to_bit(0, 3))

    def test_horizontal_backward_capture(self):
        bb_X = pos_to_bit(0, 3)
        bb_O = pos_to_bit(0, 2) | pos_to_bit(0, 1)

        bb_X, bb_O = play_move(bb_X, bb_O, 0, 0, 'X')

        self.assertEqual(bb_O & (pos_to_bit(0, 1) | pos_to_bit(0, 2)), 0)
        self.assertTrue(bb_X & pos_to_bit(0, 0))

    def test_diagonal_down_right_capture(self):
        bb_X = pos_to_bit(1, 1)
        bb_O = pos_to_bit(2, 2) | pos_to_bit(3, 3)

        bb_X, bb_O = play_move(bb_X, bb_O, 4, 4, 'X')

        self.assertEqual(bb_O & (pos_to_bit(2, 2) | pos_to_bit(3, 3)), 0)
        self.assertTrue(bb_X & pos_to_bit(4, 4))


if __name__ == "__main__":
    unittest.main()
