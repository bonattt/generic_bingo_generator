import unittest

import bingo


class TestBingo(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_insert_at_middle(self):
        start = [0, 1, 2, 4, 5, 6]
        expected = [0, 1, 2, "3", 4, 5, 6]
        bingo.insert_at(start, "3", 3)
        result = start # mutation
        self.assertSequenceEqual(expected, result)

    def test_insert_at_start(self):
        start = [1, 2, 3, 4, 5, 6]
        expected = ["0", 1, 2, 3, 4, 5, 6]
        bingo.insert_at(start, "0", 0)
        result = start # mutation
        self.assertSequenceEqual(expected, result)

    def test_insert_at_end(self):
        start = [0, 1, 2, 3, 4, 5]
        expected = [0, 1, 2, 3, 4, 5, "6"]
        bingo.insert_at(start, "6", 6)
        result = start # mutation
        self.assertSequenceEqual(expected, result)

    def test_insert_at_empty_list(self):
        start = []
        expected = ["0"]
        bingo.insert_at(start, "0", 0)
        result = start # mutation
        self.assertSequenceEqual(expected, result)


if __name__ == '__main__':
    unittest.main()