import unittest
from . import marshaller


class TestUM(unittest.TestCase):

    def setUp(self):
        pass

    def test_note_to_int_basic(self):
        self.assertEqual(marshaller.note_to_int(1, 1), 33)

    def test_note_to_int_special_char(self):
        self.assertEqual(marshaller.note_to_int("~", 1), 59)


if __name__ == '__main__':
    unittest.main()
